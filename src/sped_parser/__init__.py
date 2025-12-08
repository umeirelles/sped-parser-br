"""
SPED Parser - Python library for parsing Brazilian SPED files.

This library provides parsers for:
- EFD Contribuições (PIS/COFINS) - for sales data
- EFD Fiscal (ICMS/IPI) - for purchase data
- ECD (Escrituração Contábil Digital) - for expense data

Example usage:
    >>> from sped_parser import EFDContribuicoesParser
    >>> parser = EFDContribuicoesParser()
    >>> data = parser.parse_file("efd_contribuicoes_2024.txt")
    >>> print(f"Company: {data.header.company_name}")
    >>> print(f"Sales items: {len(data.sales_items)}")
"""

from .contribuicoes import EFDContribuicoesParser
from .fiscal import EFDFiscalParser
from .ecd import ECDParser
from .schemas import (
    SPEDData,
    SPEDItem,
    SPEDExpense,
    SPEDHeader,
    ReformImpactReport,
)
from .exceptions import (
    SPEDError,
    SPEDParseError,
    SPEDValidationError,
    SPEDEncodingError,
    SPEDFileNotFoundError,
    SPEDEmptyFileError,
)

__version__ = "0.1.0"

__all__ = [
    # Parsers
    "EFDContribuicoesParser",
    "EFDFiscalParser",
    "ECDParser",
    # Schemas
    "SPEDData",
    "SPEDItem",
    "SPEDExpense",
    "SPEDHeader",
    "ReformImpactReport",
    # Exceptions
    "SPEDError",
    "SPEDParseError",
    "SPEDValidationError",
    "SPEDEncodingError",
    "SPEDFileNotFoundError",
    "SPEDEmptyFileError",
]
