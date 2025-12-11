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
from .constants import COLUMN_COUNT_FISCAL, PARENT_CODES_FISCAL, EFDFiscalLayout, IBGE_UF_CODES
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
        rec_0000 = df[df["1"] == "0000"]
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
        rec_0200 = df[df["1"] == "0200"].copy()
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
        rec_0150 = df[df["1"] == "0150"].copy()
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

        # Extract UF from COD_MUN using IBGE mapping
        # COD_MUN first 2 digits are IBGE state codes (11=RO, 13=AM, 35=SP, etc.)
        rec_0150["ibge_code"] = rec_0150["COD_MUN"].astype(str).str[:2]
        rec_0150["UF"] = rec_0150["ibge_code"].map(IBGE_UF_CODES)

        return rec_0150[["COD_PART", "NOME", "UF"]].drop_duplicates(subset="COD_PART")

    def _extract_c170_purchases(
        self, df: pd.DataFrame, products: pd.DataFrame, participants: pd.DataFrame
    ) -> list[SPEDItem]:
        """Extract C170 purchase items (entradas only)."""
        # Get C100 invoice headers for ind_oper, cod_part, and document info
        c100 = df[df["1"] == "C100"].copy()
        if c100.empty:
            return []

        c100_layout = EFDFiscalLayout.RECORD_C100
        c100["IND_OPER"] = c100[str(c100_layout["IND_OPER"])]
        c100["COD_PART"] = c100[str(c100_layout["COD_PART"])]
        c100["NUM_DOC"] = c100[str(c100_layout["NUM_DOC"])]
        c100["CHV_NFE"] = c100[str(c100_layout["CHV_NFE"])]
        c100["DT_DOC"] = c100[str(c100_layout["DT_DOC"])]
        c100_data = c100.set_index("id")[["IND_OPER", "COD_PART", "NUM_DOC", "CHV_NFE", "DT_DOC"]]

        # Get C170 items
        c170 = df[df["1"] == "C170"].copy()
        if c170.empty:
            return []

        layout = EFDFiscalLayout.RECORD_C170

        # Filter for purchases (ind_oper == '0')
        c170["ind_oper"] = c170["id_pai"].map(c100_data["IND_OPER"])
        c170["cod_part"] = c170["id_pai"].map(c100_data["COD_PART"])
        c170["num_doc"] = c170["id_pai"].map(c100_data["NUM_DOC"])
        c170["chv_nfe"] = c170["id_pai"].map(c100_data["CHV_NFE"])
        c170["dt_doc"] = c170["id_pai"].map(c100_data["DT_DOC"])
        c170_purchases = c170[c170["ind_oper"] == "0"].copy()

        if c170_purchases.empty:
            return []

        # Extract fields from C170
        c170_purchases["COD_ITEM"] = c170_purchases[str(layout["COD_ITEM"])]
        c170_purchases["CFOP"] = c170_purchases[str(layout["CFOP"])]
        c170_purchases["VL_ITEM"] = c170_purchases[str(layout["VL_ITEM"])]
        c170_purchases["QTD"] = c170_purchases[str(layout["QTD"])]
        c170_purchases["UNID"] = c170_purchases[str(layout["UNID"])]
        c170_purchases["DESCR_COMPL"] = c170_purchases[str(layout["DESCR_COMPL"])]

        # Tax values
        c170_purchases["VL_ICMS"] = c170_purchases[str(layout["VL_ICMS"])]
        c170_purchases["VL_PIS"] = c170_purchases[str(layout["VL_PIS"])]
        c170_purchases["VL_COFINS"] = c170_purchases[str(layout["VL_COFINS"])]
        c170_purchases["VL_IPI"] = c170_purchases[str(layout["VL_IPI"])]

        # Tax rates
        c170_purchases["ALIQ_ICMS"] = c170_purchases[str(layout["ALIQ_ICMS"])]
        c170_purchases["ALIQ_PIS"] = c170_purchases[str(layout["ALIQ_PIS"])]
        c170_purchases["ALIQ_COFINS"] = c170_purchases[str(layout["ALIQ_COFINS"])]

        # Tax bases
        c170_purchases["VL_BC_ICMS"] = c170_purchases[str(layout["VL_BC_ICMS"])]
        c170_purchases["VL_BC_PIS"] = c170_purchases[str(layout["VL_BC_PIS"])]
        c170_purchases["VL_BC_COFINS"] = c170_purchases[str(layout["VL_BC_COFINS"])]

        # CST codes
        c170_purchases["CST_ICMS"] = c170_purchases[str(layout["CST_ICMS"])]
        c170_purchases["CST_PIS"] = c170_purchases[str(layout["CST_PIS"])]
        c170_purchases["CST_COFINS"] = c170_purchases[str(layout["CST_COFINS"])]

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
                        quantity=self._to_decimal(row.get("QTD")) if pd.notna(row.get("QTD")) else None,
                        unit=str(row.get("UNID", "")) if pd.notna(row.get("UNID")) else None,
                        icms_value=self._to_decimal(row.get("VL_ICMS", 0)),
                        pis_value=self._to_decimal(row.get("VL_PIS", 0)),
                        cofins_value=self._to_decimal(row.get("VL_COFINS", 0)),
                        ipi_value=self._to_decimal(row.get("VL_IPI")) if pd.notna(row.get("VL_IPI")) else None,
                        aliq_pis=self._to_decimal(row.get("ALIQ_PIS")) if pd.notna(row.get("ALIQ_PIS")) else None,
                        aliq_cofins=self._to_decimal(row.get("ALIQ_COFINS")) if pd.notna(row.get("ALIQ_COFINS")) else None,
                        aliq_icms=self._to_decimal(row.get("ALIQ_ICMS")) if pd.notna(row.get("ALIQ_ICMS")) else None,
                        vl_bc_pis=self._to_decimal(row.get("VL_BC_PIS")) if pd.notna(row.get("VL_BC_PIS")) else None,
                        vl_bc_cofins=self._to_decimal(row.get("VL_BC_COFINS")) if pd.notna(row.get("VL_BC_COFINS")) else None,
                        vl_bc_icms=self._to_decimal(row.get("VL_BC_ICMS")) if pd.notna(row.get("VL_BC_ICMS")) else None,
                        operation="entrada",
                        participant_uf=str(row.get("UF", ""))[:2] if row.get("UF") else None,
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
