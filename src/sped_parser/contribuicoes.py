"""
EFD Contribuições parser (PIS/COFINS).

This parser should be used for SALES data (débitos).
Do NOT use this parser for purchase credits - use EFDFiscalParser instead.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

import pandas as pd

from .base import SPEDParser
from .constants import (
    COLUMN_COUNT_CONTRIB,
    PARENT_CODES_CONTRIBUICOES,
    EFDContribuicoesLayout,
)
from .schemas import SPEDData, SPEDHeader, SPEDItem

logger = logging.getLogger(__name__)


class EFDContribuicoesParser(SPEDParser):
    """
    Parser for EFD Contribuições (PIS/COFINS).

    Use this parser for SALES data (débitos). This file contains:
    - C170: Item-level sales data with NCM, CFOP, values
    - A170: Service sales
    - M blocks: Current PIS/COFINS totals

    Important: For purchase CREDITS, use EFDFiscalParser, not this parser.
    """

    num_columns = COLUMN_COUNT_CONTRIB
    parent_codes = PARENT_CODES_CONTRIBUICOES
    end_marker = "9999"

    def _extract_data(self, df: pd.DataFrame) -> SPEDData:
        """
        Extract typed business data from EFD Contribuições.

        Extracts:
        - Header from 0000 record
        - Sales items from C170 (saídas only)
        - Service sales from A170

        Args:
            df: Parsed DataFrame

        Returns:
            SPEDData with header and sales_items populated
        """
        header = self._extract_header(df)
        products = self._build_product_lookup(df)

        # Extract C170 sales (saídas = ind_oper == '1')
        c170_sales = self._extract_c170_sales(df, products)

        # Extract A170 service sales (saídas = ind_oper == '1')
        a170_sales = self._extract_a170_sales(df, products)

        logger.info(
            f"Extracted {len(c170_sales)} C170 sales items + {len(a170_sales)} A170 service items"
        )

        return SPEDData(
            file_type="contribuicoes",
            header=header,
            sales_items=c170_sales + a170_sales,
            purchase_items=[],  # Don't use Contribuições for purchases!
            expenses=[],
        )

    def _extract_header(self, df: pd.DataFrame) -> SPEDHeader:
        """Extract header from 0000 record."""
        rec_0000 = df[df["0"] == "0000"]
        if rec_0000.empty:
            raise ValueError("No 0000 record found in file")

        layout = EFDContribuicoesLayout.RECORD_0000
        row = rec_0000.iloc[0]

        # Parse dates
        dt_ini_str = row.get(str(layout["DT_INI"]), "")
        dt_fin_str = row.get(str(layout["DT_FIN"]), "")

        dt_ini = self._parse_date(dt_ini_str)
        dt_fin = self._parse_date(dt_fin_str)

        return SPEDHeader(
            file_type="contribuicoes",
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

        layout = EFDContribuicoesLayout.RECORD_0200
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

    def _extract_c170_sales(
        self, df: pd.DataFrame, products: pd.DataFrame
    ) -> list[SPEDItem]:
        """Extract C170 sales items (saídas only)."""
        # Get C100 invoice headers for ind_oper lookup
        c100 = df[df["0"] == "C100"].copy()
        if c100.empty:
            return []

        c100_layout = EFDContribuicoesLayout.RECORD_C100
        c100["IND_OPER"] = c100[str(c100_layout["IND_OPER"])]
        c100_ind_oper = c100.set_index("id")["IND_OPER"]

        # Get C170 items
        c170 = df[df["0"] == "C170"].copy()
        if c170.empty:
            return []

        layout = EFDContribuicoesLayout.RECORD_C170

        # Filter for sales (ind_oper == '1')
        c170["ind_oper"] = c170["id_pai"].map(c100_ind_oper)
        c170_sales = c170[c170["ind_oper"] == "1"].copy()

        if c170_sales.empty:
            return []

        # Extract fields
        c170_sales["COD_ITEM"] = c170_sales[str(layout["COD_ITEM"])]
        c170_sales["CFOP"] = c170_sales[str(layout["CFOP"])]
        c170_sales["VL_ITEM"] = c170_sales[str(layout["VL_ITEM"])]
        c170_sales["CST_PIS"] = c170_sales[str(layout["CST_PIS"])]
        c170_sales["VL_PIS"] = c170_sales[str(layout["VL_PIS"])]
        c170_sales["CST_COFINS"] = c170_sales[str(layout["CST_COFINS"])]
        c170_sales["VL_COFINS"] = c170_sales[str(layout["VL_COFINS"])]
        c170_sales["DESCR_COMPL"] = c170_sales[str(layout["DESCR_COMPL"])]

        # Merge with products to get NCM
        c170_sales = c170_sales.merge(products, on="COD_ITEM", how="left")

        # Convert to SPEDItem objects
        items = []
        for _, row in c170_sales.iterrows():
            try:
                ncm = str(row.get("COD_NCM", "")).zfill(8)
                if not ncm or ncm == "00000000":
                    ncm = "00000000"  # Default NCM

                items.append(
                    SPEDItem(
                        ncm=ncm,
                        cfop=str(row.get("CFOP", "")).zfill(4),
                        item_code=str(row.get("COD_ITEM", "")),
                        description=row.get("DESCR_ITEM") or row.get("DESCR_COMPL"),
                        total_value=self._to_decimal(row.get("VL_ITEM", 0)),
                        pis_value=self._to_decimal(row.get("VL_PIS", 0)),
                        cofins_value=self._to_decimal(row.get("VL_COFINS", 0)),
                        operation="saida",
                        cst_pis=str(row.get("CST_PIS", "")),
                        cst_cofins=str(row.get("CST_COFINS", "")),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse C170 item: {e}")
                continue

        return items

    def _extract_a170_sales(
        self, df: pd.DataFrame, products: pd.DataFrame
    ) -> list[SPEDItem]:
        """Extract A170 service sales (saídas only)."""
        # Get A100 service headers for ind_oper lookup
        a100 = df[df["0"] == "A100"].copy()
        if a100.empty:
            return []

        a100_layout = EFDContribuicoesLayout.RECORD_A100
        a100["IND_OPER"] = a100[str(a100_layout["IND_OPER"])]
        a100_ind_oper = a100.set_index("id")["IND_OPER"]

        # Get A170 items
        a170 = df[df["0"] == "A170"].copy()
        if a170.empty:
            return []

        layout = EFDContribuicoesLayout.RECORD_A170

        # Filter for sales (ind_oper == '1')
        a170["ind_oper"] = a170["id_pai"].map(a100_ind_oper)
        a170_sales = a170[a170["ind_oper"] == "1"].copy()

        if a170_sales.empty:
            return []

        # Extract fields
        a170_sales["COD_ITEM"] = a170_sales[str(layout["COD_ITEM"])]
        a170_sales["VL_ITEM"] = a170_sales[str(layout["VL_ITEM"])]
        a170_sales["CST_PIS"] = a170_sales[str(layout["CST_PIS"])]
        a170_sales["VL_PIS"] = a170_sales[str(layout["VL_PIS"])]
        a170_sales["CST_COFINS"] = a170_sales[str(layout["CST_COFINS"])]
        a170_sales["VL_COFINS"] = a170_sales[str(layout["VL_COFINS"])]
        a170_sales["DESCR_COMPL"] = a170_sales[str(layout["DESCR_COMPL"])]

        # Merge with products to get NCM (services may not have NCM)
        a170_sales = a170_sales.merge(products, on="COD_ITEM", how="left")

        # Convert to SPEDItem objects
        items = []
        for _, row in a170_sales.iterrows():
            try:
                ncm = str(row.get("COD_NCM", "")).zfill(8)
                if not ncm or ncm == "00000000":
                    ncm = "00000000"  # Services often don't have NCM

                items.append(
                    SPEDItem(
                        ncm=ncm,
                        cfop="5933",  # Default CFOP for services
                        item_code=str(row.get("COD_ITEM", "")),
                        description=row.get("DESCR_ITEM") or row.get("DESCR_COMPL"),
                        total_value=self._to_decimal(row.get("VL_ITEM", 0)),
                        pis_value=self._to_decimal(row.get("VL_PIS", 0)),
                        cofins_value=self._to_decimal(row.get("VL_COFINS", 0)),
                        operation="saida",
                        cst_pis=str(row.get("CST_PIS", "")),
                        cst_cofins=str(row.get("CST_COFINS", "")),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse A170 item: {e}")
                continue

        return items

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse DDMMYYYY date string."""
        if not date_str or len(date_str) < 8:
            return datetime(2024, 1, 1)  # Default date

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
            # Replace comma with period
            val_str = str(value).replace(",", ".")
            return Decimal(val_str)
        except:
            return Decimal("0")
