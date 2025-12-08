"""
Abstract base parser for SPED files.

This module provides the base SPEDParser class that implements common parsing logic
for all SPED file types (EFD Contribuições, EFD Fiscal, ECD).
"""

import csv
import logging
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from .constants import ENCODING, DELIMITER, CHUNK_SIZE
from .exceptions import (
    SPEDParseError,
    SPEDEncodingError,
    SPEDFileNotFoundError,
    SPEDEmptyFileError,
)
from .schemas import SPEDData

logger = logging.getLogger(__name__)


class SPEDParser(ABC):
    """
    Abstract base class for SPED file parsers.

    Implements common parsing logic:
    - File reading with C engine fallback to Python engine
    - Chunked processing for large files
    - End marker detection (9999 or I990)
    - Parent ID assignment for hierarchical records
    - Header extraction

    Subclasses must implement:
    - num_columns: Number of columns in this file type
    - parent_codes: List of register codes that are parents in hierarchy
    - end_marker: Register code that marks end of file
    - _extract_data: Business logic to extract typed data from DataFrame
    """

    ENCODING = ENCODING
    DELIMITER = DELIMITER
    CHUNK_SIZE = CHUNK_SIZE

    @property
    @abstractmethod
    def num_columns(self) -> int:
        """Number of columns in this SPED file type."""
        ...

    @property
    @abstractmethod
    def parent_codes(self) -> list[str]:
        """List of register codes that act as parents in hierarchy."""
        ...

    @property
    @abstractmethod
    def end_marker(self) -> str:
        """Register code that marks end of file (e.g., '9999' or 'I990')."""
        ...

    @abstractmethod
    def _extract_data(self, df: pd.DataFrame) -> SPEDData:
        """
        Extract typed business data from parsed DataFrame.

        Args:
            df: Parsed DataFrame with all records

        Returns:
            SPEDData with header, sales_items, purchase_items, expenses
        """
        ...

    def parse(self, content: bytes) -> SPEDData:
        """
        Parse SPED file content from bytes.

        Args:
            content: Raw file bytes

        Returns:
            SPEDData with parsed content and layered API access

        Raises:
            SPEDParseError: If parsing fails
            SPEDEncodingError: If file encoding is invalid
            SPEDEmptyFileError: If file is empty or has no valid records
        """
        logger.info(f"Parsing with {self.__class__.__name__}")

        try:
            df = self._read_file(content)
            df = self._trim_at_end_marker(df)
            df = self._assign_parent_ids(df)

            if df.empty:
                raise SPEDEmptyFileError("File has no valid records after parsing")

            # Extract business data
            sped_data = self._extract_data(df)

            # Set raw DataFrame for layered API
            sped_data.set_raw_dataframe(df)

            return sped_data

        except UnicodeDecodeError as e:
            raise SPEDEncodingError(f"Failed to decode file with {self.ENCODING} encoding: {e}")
        except Exception as e:
            if isinstance(e, (SPEDParseError, SPEDEncodingError, SPEDEmptyFileError)):
                raise
            raise SPEDParseError(f"Failed to parse SPED file: {e}")

    def parse_file(self, file_path: Union[str, Path]) -> SPEDData:
        """
        Parse SPED file from filesystem path.

        Args:
            file_path: Path to SPED file

        Returns:
            SPEDData with parsed content

        Raises:
            SPEDFileNotFoundError: If file doesn't exist
            SPEDParseError: If parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise SPEDFileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Reading file: {file_path}")
        with open(path, "rb") as f:
            content = f.read()

        return self.parse(content)

    def _read_file(self, content: bytes) -> pd.DataFrame:
        """
        Read SPED file with fallback strategy.

        First tries fast C engine, falls back to Python engine with chunking if needed.

        Args:
            content: File bytes

        Returns:
            DataFrame with string columns numbered 0, 1, 2, ...
        """
        column_names = [str(i) for i in range(self.num_columns)]
        file_obj = BytesIO(content)

        # Try fast C engine first
        try:
            logger.debug("Attempting to read with C engine")
            df = pd.read_csv(
                file_obj,
                header=None,
                delimiter=self.DELIMITER,
                names=column_names,
                low_memory=False,
                encoding=self.ENCODING,
                dtype=str,
                engine="c",
                on_bad_lines="skip",
            )
            logger.debug(f"Successfully read {len(df)} rows with C engine")
            return df

        except (pd.errors.ParserError, csv.Error) as e:
            logger.debug(f"C engine failed ({e}), falling back to Python engine with chunking")

        # Fallback: Python engine with chunking
        file_obj.seek(0)
        reader = pd.read_csv(
            file_obj,
            header=None,
            delimiter=self.DELIMITER,
            names=column_names,
            encoding=self.ENCODING,
            dtype=str,
            engine="python",
            on_bad_lines="skip",
            chunksize=self.CHUNK_SIZE,
            quoting=csv.QUOTE_NONE,
        )

        parts = []
        for chunk in reader:
            # Check for end marker in this chunk
            if "0" in chunk.columns:
                mask_end = chunk["0"].astype(str).eq(self.end_marker)
                if mask_end.any():
                    first_idx = int(np.argmax(mask_end.to_numpy()))
                    parts.append(chunk.iloc[: first_idx + 1])
                    break
            parts.append(chunk)

        df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=column_names)
        logger.debug(f"Read {len(df)} rows with Python engine (chunked)")
        return df

    def _trim_at_end_marker(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trim DataFrame at end marker record.

        Args:
            df: DataFrame with all records

        Returns:
            DataFrame trimmed at end marker (inclusive)
        """
        if df.empty or "0" not in df.columns:
            return df

        mask = df["0"].astype(str).eq(self.end_marker)
        if mask.any():
            cut_idx = int(np.argmax(mask.to_numpy()))
            df = df.iloc[: cut_idx + 1].copy()
            logger.debug(f"Trimmed at end marker {self.end_marker} (row {cut_idx})")

        return df

    def _assign_parent_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign parent IDs for hierarchical record relationships.

        Uses forward-fill to propagate parent IDs to child records.

        Args:
            df: DataFrame with records

        Returns:
            DataFrame with 'id_pai' column
        """
        if df.empty:
            return df

        # Create row IDs
        df.insert(0, "id_pai", None)
        df.insert(0, "id", df.index.astype(str))

        # Mark parent records
        if "0" in df.columns:
            is_parent = df["0"].isin(self.parent_codes)
            df.loc[is_parent, "id_pai"] = df.loc[is_parent, "id"]

        # Forward-fill parent IDs
        df["id_pai"] = df["id_pai"].ffill()

        logger.debug(f"Assigned parent IDs ({len(self.parent_codes)} parent types)")
        return df
