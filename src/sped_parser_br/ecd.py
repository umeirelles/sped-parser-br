"""
ECD parser (Escrituração Contábil Digital).

This parser extracts accounting data for expense credit calculation.
"""

import logging
from datetime import datetime
from decimal import Decimal

import pandas as pd

from .base import SPEDParser
from .constants import COLUMN_COUNT_ECD, PARENT_CODES_ECD, ECDLayout
from .schemas import SPEDData, SPEDHeader, SPEDExpense

logger = logging.getLogger(__name__)


class ECDParser(SPEDParser):
    """
    Parser for ECD (Escrituração Contábil Digital).

    Use this parser for EXPENSE data from accounting records. This file contains:
    - I050/I051: Chart of accounts with reference codes
    - I155: Account balances (detailed)
    - I355: P&L balances (summary)

    Use I355 for expense credits calculation under tax reform.
    """

    num_columns = COLUMN_COUNT_ECD
    parent_codes = PARENT_CODES_ECD
    end_marker = "I990"

    def _extract_data(self, df: pd.DataFrame) -> SPEDData:
        """
        Extract typed business data from ECD.

        Extracts:
        - Header from 0000 record
        - Expense accounts from I355 (P&L balances)
        - Account descriptions from I050

        Args:
            df: Parsed DataFrame

        Returns:
            SPEDData with header and expenses populated
        """
        header = self._extract_header(df)
        account_refs = self._build_account_refs(df)

        # Extract I355 P&L balances
        expenses = self._extract_i355(df, account_refs)

        logger.info(f"Extracted {len(expenses)} I355 expense accounts")

        return SPEDData(
            file_type="ecd",
            header=header,
            sales_items=[],
            purchase_items=[],
            expenses=expenses,
        )

    def _extract_header(self, df: pd.DataFrame) -> SPEDHeader:
        """Extract header from 0000 record."""
        rec_0000 = df[df["1"] == "0000"]
        if rec_0000.empty:
            raise ValueError("No 0000 record found in file")

        layout = ECDLayout.RECORD_0000
        row = rec_0000.iloc[0]

        # Parse dates
        dt_ini_str = row.get(str(layout["DT_INI"]), "")
        dt_fin_str = row.get(str(layout["DT_FIN"]), "")

        dt_ini = self._parse_date(dt_ini_str)
        dt_fin = self._parse_date(dt_fin_str)

        return SPEDHeader(
            file_type="ecd",
            cnpj=row.get(str(layout["CNPJ"]), "").zfill(14),
            company_name=row.get(str(layout["NOME"]), ""),
            period_start=dt_ini,
            period_end=dt_fin,
            uf=row.get(str(layout["UF"]), ""),
        )

    def _build_account_refs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build account reference lookup from I050 and I051 records.

        I050 contains chart of accounts.
        I051 maps account codes to reference plan codes.
        """
        # Get I050 chart of accounts
        rec_i050 = df[df["1"] == "I050"].copy()
        if rec_i050.empty:
            return pd.DataFrame(columns=["COD_CTA", "NOME_CTA", "COD_CTA_REF"])

        layout = ECDLayout.RECORD_I050
        rec_i050 = rec_i050.rename(
            columns={
                str(layout["COD_CTA"]): "COD_CTA",
                str(layout["NOME_CTA"]): "NOME_CTA",
            }
        )

        # Get I051 reference mappings
        rec_i051 = df[df["1"] == "I051"].copy()
        if not rec_i051.empty:
            layout_i051 = ECDLayout.RECORD_I051
            rec_i051 = rec_i051.rename(
                columns={
                    str(layout_i051["COD_CTA_REF"]): "COD_CTA_REF",
                }
            )
            # I051 is child of I050, so we can use id_pai to link
            rec_i051["COD_CTA"] = rec_i051["id_pai"].map(
                rec_i050.set_index("id")["COD_CTA"]
            )

            # Merge reference codes
            rec_i050 = rec_i050.merge(
                rec_i051[["COD_CTA", "COD_CTA_REF"]], on="COD_CTA", how="left"
            )

        return rec_i050[["COD_CTA", "NOME_CTA", "COD_CTA_REF"]].drop_duplicates(
            subset="COD_CTA"
        )

    def _extract_i355(
        self, df: pd.DataFrame, account_refs: pd.DataFrame
    ) -> list[SPEDExpense]:
        """
        Extract I355 P&L balance records.

        I355 contains profit & loss account balances, which are used for
        calculating expense credits under tax reform.
        """
        rec_i355 = df[df["1"] == "I355"].copy()
        if rec_i355.empty:
            return []

        layout = ECDLayout.RECORD_I355

        # Extract fields
        rec_i355["COD_CTA"] = rec_i355[str(layout["COD_CTA"])]
        rec_i355["VL_CTA"] = rec_i355[str(layout["VL_CTA"])]
        rec_i355["IND_VL"] = rec_i355[str(layout["IND_VL"])]  # D or C (debit/credit)

        # Merge with account descriptions
        rec_i355 = rec_i355.merge(account_refs, on="COD_CTA", how="left")

        # Convert to SPEDExpense objects
        expenses = []
        for _, row in rec_i355.iterrows():
            try:
                ind_vl = str(row.get("IND_VL", "")).upper()
                is_debit = ind_vl == "D"

                expenses.append(
                    SPEDExpense(
                        account_code=str(row.get("COD_CTA", "")),
                        account_description=row.get("NOME_CTA"),
                        reference_code=row.get("COD_CTA_REF"),
                        value=self._to_decimal(row.get("VL_CTA", 0)),
                        is_debit=is_debit,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse I355 record: {e}")
                continue

        return expenses

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse DDMMYYYY date string."""
        if not date_str or len(date_str) < 8:
            return datetime(2024, 1, 1).date()

        try:
            return datetime.strptime(date_str[:8], "%d%m%Y").date()
        except ValueError:
            return datetime(2024, 1, 1).date()

    @staticmethod
    def _to_decimal(value) -> Decimal:
        """Convert value to Decimal, handling comma decimals."""
        if pd.isna(value):
            return Decimal("0")

        try:
            val_str = str(value).replace(",", ".")
            return Decimal(val_str)
        except:
            return Decimal("0")
