"""
EFD Fiscal parser (ICMS/IPI).

This parser should be used for PURCHASE data (créditos).
This file contains ALL incoming invoices, which is needed for complete credit calculation.
"""

import logging
from datetime import datetime
from decimal import Decimal

import pandas as pd

from .base import SPEDParser
from .constants import COLUMN_COUNT_FISCAL, PARENT_CODES_FISCAL, EFDFiscalLayout
from .schemas import SPEDData, SPEDHeader, SPEDItem

logger = logging.getLogger(__name__)


class EFDFiscalParser(SPEDParser):
    """
    Parser for EFD Fiscal (ICMS/IPI).

    Use this parser for PURCHASE data (créditos). This file contains:
    - C170: ALL incoming invoice items (entradas)
    - 0150: Participant/supplier information (for UF)
    - E110: ICMS assessment totals

    Important: C170 in EFD Fiscal is ONLY for purchases (entradas).
    For sales, use EFDContribuicoesParser C170.
    """

    num_columns = COLUMN_COUNT_FISCAL
    parent_codes = PARENT_CODES_FISCAL
    end_marker = "9999"

    def _extract_data(self, df: pd.DataFrame) -> SPEDData:
        """
        Extract typed business data from EFD Fiscal.

        Extracts:
        - Header from 0000 record
        - Purchase items from C170 (entradas only)
        - Participant UF for each purchase

        Args:
            df: Parsed DataFrame

        Returns:
            SPEDData with header and purchase_items populated
        """
        header = self._extract_header(df)
        products = self._build_product_lookup(df)
        participants = self._build_participant_lookup(df)

        # Extract C170 purchases (entradas = ind_oper == '0')
        c170_purchases = self._extract_c170_purchases(df, products, participants)

        logger.info(f"Extracted {len(c170_purchases)} C170 purchase items")

        return SPEDData(
            file_type="fiscal",
            header=header,
            sales_items=[],  # Use Contribuições for sales!
            purchase_items=c170_purchases,
            expenses=[],
        )

    def _extract_header(self, df: pd.DataFrame) -> SPEDHeader:
        """Extract header from 0000 record."""
        rec_0000 = df[df["0"] == "0000"]
        if rec_0000.empty:
            raise ValueError("No 0000 record found in file")

        layout = EFDFiscalLayout.RECORD_0000
        row = rec_0000.iloc[0]

        # Parse dates
        dt_ini_str = row.get(str(layout["DT_INI"]), "")
        dt_fin_str = row.get(str(layout["DT_FIN"]), "")

        dt_ini = self._parse_date(dt_ini_str)
        dt_fin = self._parse_date(dt_fin_str)

        return SPEDHeader(
            file_type="fiscal",
            cnpj=row.get(str(layout["CNPJ"]), "").zfill(14),
            company_name=row.get(str(layout["NOME"]), ""),
            period_start=dt_ini,
            period_end=dt_fin,
            uf=row.get(str(layout["UF"]), ""),
        )

    def _build_product_lookup(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build product lookup from 0200 records."""
        rec_0200 = df[df["0"] == "0200"].copy()
        if rec_0200.empty:
            return pd.DataFrame(columns=["COD_ITEM", "DESCR_ITEM", "COD_NCM"])

        layout = EFDFiscalLayout.RECORD_0200
        rec_0200 = rec_0200.rename(
            columns={
                str(layout["COD_ITEM"]): "COD_ITEM",
                str(layout["DESCR_ITEM"]): "DESCR_ITEM",
                str(layout["COD_NCM"]): "COD_NCM",
            }
        )
        return rec_0200[["COD_ITEM", "DESCR_ITEM", "COD_NCM"]].drop_duplicates(
            subset="COD_ITEM"
        )

    def _build_participant_lookup(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build participant lookup from 0150 records (for supplier UF)."""
        rec_0150 = df[df["0"] == "0150"].copy()
        if rec_0150.empty:
            return pd.DataFrame(columns=["COD_PART", "NOME", "COD_MUN"])

        layout = EFDFiscalLayout.RECORD_0150
        rec_0150 = rec_0150.rename(
            columns={
                str(layout["COD_PART"]): "COD_PART",
                str(layout["NOME"]): "NOME",
                str(layout["COD_MUN"]): "COD_MUN",
            }
        )

        # Extract UF from COD_MUN (first 2 digits)
        rec_0150["UF"] = rec_0150["COD_MUN"].astype(str).str[:2]

        return rec_0150[["COD_PART", "NOME", "UF"]].drop_duplicates(subset="COD_PART")

    def _extract_c170_purchases(
        self, df: pd.DataFrame, products: pd.DataFrame, participants: pd.DataFrame
    ) -> list[SPEDItem]:
        """Extract C170 purchase items (entradas only)."""
        # Get C100 invoice headers for ind_oper and cod_part lookup
        c100 = df[df["0"] == "C100"].copy()
        if c100.empty:
            return []

        c100_layout = EFDFiscalLayout.RECORD_C100
        c100["IND_OPER"] = c100[str(c100_layout["IND_OPER"])]
        c100["COD_PART"] = c100[str(c100_layout["COD_PART"])]
        c100_data = c100.set_index("id")[["IND_OPER", "COD_PART"]]

        # Get C170 items
        c170 = df[df["0"] == "C170"].copy()
        if c170.empty:
            return []

        layout = EFDFiscalLayout.RECORD_C170

        # Filter for purchases (ind_oper == '0')
        c170["ind_oper"] = c170["id_pai"].map(c100_data["IND_OPER"])
        c170["cod_part"] = c170["id_pai"].map(c100_data["COD_PART"])
        c170_purchases = c170[c170["ind_oper"] == "0"].copy()

        if c170_purchases.empty:
            return []

        # Extract fields
        c170_purchases["COD_ITEM"] = c170_purchases[str(layout["COD_ITEM"])]
        c170_purchases["CFOP"] = c170_purchases[str(layout["CFOP"])]
        c170_purchases["VL_ITEM"] = c170_purchases[str(layout["VL_ITEM"])]
        c170_purchases["VL_ICMS"] = c170_purchases[str(layout["VL_ICMS"])]
        c170_purchases["VL_PIS"] = c170_purchases[str(layout["VL_PIS"])]
        c170_purchases["VL_COFINS"] = c170_purchases[str(layout["VL_COFINS"])]
        c170_purchases["CST_ICMS"] = c170_purchases[str(layout["CST_ICMS"])]
        c170_purchases["CST_PIS"] = c170_purchases[str(layout["CST_PIS"])]
        c170_purchases["CST_COFINS"] = c170_purchases[str(layout["CST_COFINS"])]
        c170_purchases["DESCR_COMPL"] = c170_purchases[str(layout["DESCR_COMPL"])]

        # Merge with products to get NCM
        c170_purchases = c170_purchases.merge(products, on="COD_ITEM", how="left")

        # Merge with participants to get UF
        c170_purchases = c170_purchases.merge(
            participants, left_on="cod_part", right_on="COD_PART", how="left"
        )

        # Convert to SPEDItem objects
        items = []
        for _, row in c170_purchases.iterrows():
            try:
                ncm = str(row.get("COD_NCM", "")).zfill(8)
                if not ncm or ncm == "00000000":
                    ncm = "00000000"

                items.append(
                    SPEDItem(
                        ncm=ncm,
                        cfop=str(row.get("CFOP", "")).zfill(4),
                        item_code=str(row.get("COD_ITEM", "")),
                        description=row.get("DESCR_ITEM") or row.get("DESCR_COMPL"),
                        total_value=self._to_decimal(row.get("VL_ITEM", 0)),
                        icms_value=self._to_decimal(row.get("VL_ICMS", 0)),
                        pis_value=self._to_decimal(row.get("VL_PIS", 0)),
                        cofins_value=self._to_decimal(row.get("VL_COFINS", 0)),
                        operation="entrada",
                        participant_uf=str(row.get("UF", ""))[:2] if row.get("UF") else None,
                        cst_icms=str(row.get("CST_ICMS", "")),
                        cst_pis=str(row.get("CST_PIS", "")),
                        cst_cofins=str(row.get("CST_COFINS", "")),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse C170 item: {e}")
                continue

        return items

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
