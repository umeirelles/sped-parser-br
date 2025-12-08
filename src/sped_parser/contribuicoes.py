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
        # Get C100 invoice headers for ind_oper and document info
        c100 = df[df["0"] == "C100"].copy()
        if c100.empty:
            return []

        c100_layout = EFDContribuicoesLayout.RECORD_C100
        c100["IND_OPER"] = c100[str(c100_layout["IND_OPER"])]
        c100["NUM_DOC"] = c100[str(c100_layout["NUM_DOC"])]
        c100["CHV_NFE"] = c100[str(c100_layout["CHV_NFE"])]
        c100["DT_DOC"] = c100[str(c100_layout["DT_DOC"])]
        c100_data = c100.set_index("id")[["IND_OPER", "NUM_DOC", "CHV_NFE", "DT_DOC"]]

        # Get C170 items
        c170 = df[df["0"] == "C170"].copy()
        if c170.empty:
            return []

        layout = EFDContribuicoesLayout.RECORD_C170

        # Filter for sales (ind_oper == '1')
        c170["ind_oper"] = c170["id_pai"].map(c100_data["IND_OPER"])
        c170["num_doc"] = c170["id_pai"].map(c100_data["NUM_DOC"])
        c170["chv_nfe"] = c170["id_pai"].map(c100_data["CHV_NFE"])
        c170["dt_doc"] = c170["id_pai"].map(c100_data["DT_DOC"])
        c170_sales = c170[c170["ind_oper"] == "1"].copy()

        if c170_sales.empty:
            return []

        # Extract fields from C170
        c170_sales["COD_ITEM"] = c170_sales[str(layout["COD_ITEM"])]
        c170_sales["CFOP"] = c170_sales[str(layout["CFOP"])]
        c170_sales["VL_ITEM"] = c170_sales[str(layout["VL_ITEM"])]
        c170_sales["QTD"] = c170_sales[str(layout["QTD"])]
        c170_sales["UNID"] = c170_sales[str(layout["UNID"])]
        c170_sales["DESCR_COMPL"] = c170_sales[str(layout["DESCR_COMPL"])]

        # Tax values
        c170_sales["VL_ICMS"] = c170_sales[str(layout["VL_ICMS"])]
        c170_sales["VL_PIS"] = c170_sales[str(layout["VL_PIS"])]
        c170_sales["VL_COFINS"] = c170_sales[str(layout["VL_COFINS"])]

        # Tax rates
        c170_sales["ALIQ_ICMS"] = c170_sales[str(layout["ALIQ_ICMS"])]
        c170_sales["ALIQ_PIS"] = c170_sales[str(layout["ALIQ_PIS"])]
        c170_sales["ALIQ_COFINS"] = c170_sales[str(layout["ALIQ_COFINS"])]

        # Tax bases
        c170_sales["VL_BC_ICMS"] = c170_sales[str(layout["VL_BC_ICMS"])]
        c170_sales["VL_BC_PIS"] = c170_sales[str(layout["VL_BC_PIS"])]
        c170_sales["VL_BC_COFINS"] = c170_sales[str(layout["VL_BC_COFINS"])]

        # CST codes
        c170_sales["CST_ICMS"] = c170_sales[str(layout["CST_ICMS"])]
        c170_sales["CST_PIS"] = c170_sales[str(layout["CST_PIS"])]
        c170_sales["CST_COFINS"] = c170_sales[str(layout["CST_COFINS"])]

        # Merge with products to get NCM
        c170_sales = c170_sales.merge(products, on="COD_ITEM", how="left")

        # Convert to SPEDItem objects
        items = []
        for _, row in c170_sales.iterrows():
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
                        quantity=self._to_decimal(row.get("QTD")) if pd.notna(row.get("QTD")) else None,
                        unit=str(row.get("UNID", "")) if pd.notna(row.get("UNID")) else None,
                        icms_value=self._to_decimal(row.get("VL_ICMS", 0)),
                        pis_value=self._to_decimal(row.get("VL_PIS", 0)),
                        cofins_value=self._to_decimal(row.get("VL_COFINS", 0)),
                        aliq_pis=self._to_decimal(row.get("ALIQ_PIS")) if pd.notna(row.get("ALIQ_PIS")) else None,
                        aliq_cofins=self._to_decimal(row.get("ALIQ_COFINS")) if pd.notna(row.get("ALIQ_COFINS")) else None,
                        aliq_icms=self._to_decimal(row.get("ALIQ_ICMS")) if pd.notna(row.get("ALIQ_ICMS")) else None,
                        vl_bc_pis=self._to_decimal(row.get("VL_BC_PIS")) if pd.notna(row.get("VL_BC_PIS")) else None,
                        vl_bc_cofins=self._to_decimal(row.get("VL_BC_COFINS")) if pd.notna(row.get("VL_BC_COFINS")) else None,
                        vl_bc_icms=self._to_decimal(row.get("VL_BC_ICMS")) if pd.notna(row.get("VL_BC_ICMS")) else None,
                        operation="saida",
                        cst_icms=str(row.get("CST_ICMS", "")),
                        cst_pis=str(row.get("CST_PIS", "")),
                        cst_cofins=str(row.get("CST_COFINS", "")),
                        document_number=str(row.get("num_doc", "")) if pd.notna(row.get("num_doc")) else None,
                        document_key=str(row.get("chv_nfe", "")) if pd.notna(row.get("chv_nfe")) else None,
                        document_date=self._parse_date(str(row.get("dt_doc", ""))) if pd.notna(row.get("dt_doc")) else None,
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
        # Get A100 service headers for ind_oper and document info
        a100 = df[df["0"] == "A100"].copy()
        if a100.empty:
            return []

        a100_layout = EFDContribuicoesLayout.RECORD_A100
        a100["IND_OPER"] = a100[str(a100_layout["IND_OPER"])]
        a100["NUM_DOC"] = a100[str(a100_layout["NUM_DOC"])]
        a100["CHV_NFSE"] = a100[str(a100_layout["CHV_NFSE"])]
        a100["DT_DOC"] = a100[str(a100_layout["DT_DOC"])]
        a100_data = a100.set_index("id")[["IND_OPER", "NUM_DOC", "CHV_NFSE", "DT_DOC"]]

        # Get A170 items
        a170 = df[df["0"] == "A170"].copy()
        if a170.empty:
            return []

        layout = EFDContribuicoesLayout.RECORD_A170

        # Filter for sales (ind_oper == '1')
        a170["ind_oper"] = a170["id_pai"].map(a100_data["IND_OPER"])
        a170["num_doc"] = a170["id_pai"].map(a100_data["NUM_DOC"])
        a170["chv_nfse"] = a170["id_pai"].map(a100_data["CHV_NFSE"])
        a170["dt_doc"] = a170["id_pai"].map(a100_data["DT_DOC"])
        a170_sales = a170[a170["ind_oper"] == "1"].copy()

        if a170_sales.empty:
            return []

        # Extract fields from A170
        a170_sales["COD_ITEM"] = a170_sales[str(layout["COD_ITEM"])]
        a170_sales["VL_ITEM"] = a170_sales[str(layout["VL_ITEM"])]
        a170_sales["DESCR_COMPL"] = a170_sales[str(layout["DESCR_COMPL"])]

        # Tax values
        a170_sales["VL_PIS"] = a170_sales[str(layout["VL_PIS"])]
        a170_sales["VL_COFINS"] = a170_sales[str(layout["VL_COFINS"])]

        # Tax rates
        a170_sales["ALIQ_PIS"] = a170_sales[str(layout["ALIQ_PIS"])]
        a170_sales["ALIQ_COFINS"] = a170_sales[str(layout["ALIQ_COFINS"])]

        # Tax bases
        a170_sales["VL_BC_PIS"] = a170_sales[str(layout["VL_BC_PIS"])]
        a170_sales["VL_BC_COFINS"] = a170_sales[str(layout["VL_BC_COFINS"])]

        # Credit classification (critical for LC 214!)
        a170_sales["NAT_BC_CRED"] = a170_sales[str(layout["NAT_BC_CRED"])]

        # CST codes
        a170_sales["CST_PIS"] = a170_sales[str(layout["CST_PIS"])]
        a170_sales["CST_COFINS"] = a170_sales[str(layout["CST_COFINS"])]

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
                        aliq_pis=self._to_decimal(row.get("ALIQ_PIS")) if pd.notna(row.get("ALIQ_PIS")) else None,
                        aliq_cofins=self._to_decimal(row.get("ALIQ_COFINS")) if pd.notna(row.get("ALIQ_COFINS")) else None,
                        vl_bc_pis=self._to_decimal(row.get("VL_BC_PIS")) if pd.notna(row.get("VL_BC_PIS")) else None,
                        vl_bc_cofins=self._to_decimal(row.get("VL_BC_COFINS")) if pd.notna(row.get("VL_BC_COFINS")) else None,
                        nat_bc_cred=str(row.get("NAT_BC_CRED", "")) if pd.notna(row.get("NAT_BC_CRED")) else None,
                        operation="saida",
                        cst_pis=str(row.get("CST_PIS", "")),
                        cst_cofins=str(row.get("CST_COFINS", "")),
                        document_number=str(row.get("num_doc", "")) if pd.notna(row.get("num_doc")) else None,
                        document_key=str(row.get("chv_nfse", "")) if pd.notna(row.get("chv_nfse")) else None,
                        document_date=self._parse_date(str(row.get("dt_doc", ""))) if pd.notna(row.get("dt_doc")) else None,
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
