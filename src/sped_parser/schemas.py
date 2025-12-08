"""
Pydantic models for SPED data structures.

This module defines type-safe data models for SPED file contents using Pydantic.
All monetary values use Decimal for precision.
"""

from decimal import Decimal
from typing import Literal, Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd


class SPEDHeader(BaseModel):
    """
    Header information common to all SPED file types.
    Contains company identification and period information.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file_type: Literal["contribuicoes", "fiscal", "ecd"]
    cnpj: str = Field(..., pattern=r"^\d{14}$", description="Company CNPJ (14 digits)")
    company_name: str = Field(..., description="Company legal name")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    uf: str = Field(..., pattern=r"^[A-Z]{2}$", description="State (UF) code")


class SPEDItem(BaseModel):
    """
    Represents a single item/product in a SPED document.
    Used for both sales (débitos) and purchases (créditos).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Item identification
    ncm: str = Field(..., pattern=r"^\d{8}$", description="NCM code (8 digits)")
    cfop: str = Field(..., pattern=r"^\d{4}$", description="CFOP code (4 digits)")
    item_code: str = Field(..., description="Internal item code")
    description: Optional[str] = Field(None, description="Item description")

    # Values
    total_value: Decimal = Field(..., description="Total item value")
    quantity: Optional[Decimal] = Field(None, description="Item quantity (QTD)")
    unit: Optional[str] = Field(None, description="Unit of measure (UNID)")

    # Tax values (current system)
    icms_value: Decimal = Field(Decimal("0"), description="ICMS tax value")
    pis_value: Decimal = Field(Decimal("0"), description="PIS tax value")
    cofins_value: Decimal = Field(Decimal("0"), description="COFINS tax value")
    ipi_value: Optional[Decimal] = Field(None, description="IPI tax value")

    # Tax rates (critical for LC 214 recalculation)
    aliq_pis: Optional[Decimal] = Field(None, description="PIS tax rate (%)")
    aliq_cofins: Optional[Decimal] = Field(None, description="COFINS tax rate (%)")
    aliq_icms: Optional[Decimal] = Field(None, description="ICMS tax rate (%)")

    # Tax bases (critical for IBS/CBS calculation)
    vl_bc_pis: Optional[Decimal] = Field(None, description="PIS tax base")
    vl_bc_cofins: Optional[Decimal] = Field(None, description="COFINS tax base")
    vl_bc_icms: Optional[Decimal] = Field(None, description="ICMS tax base")

    # CST codes
    cst_pis: Optional[str] = Field(None, description="CST PIS code")
    cst_cofins: Optional[str] = Field(None, description="CST COFINS code")
    cst_icms: Optional[str] = Field(None, description="CST ICMS code")

    # Credit classification (critical for LC 214 credit rules)
    nat_bc_cred: Optional[str] = Field(None, description="Nature of credit base code")

    # Document reference (for audit trail)
    document_number: Optional[str] = Field(None, description="Document number (NUM_DOC)")
    document_key: Optional[str] = Field(None, description="NFe access key (CHV_NFE)")
    document_date: Optional[date] = Field(None, description="Document date (DT_DOC)")

    # Operation
    operation: Literal["entrada", "saida"] = Field(..., description="Operation type")
    participant_uf: Optional[str] = Field(
        None, pattern=r"^[A-Z]{2}$", description="Participant UF (for purchases)"
    )


class SPEDExpense(BaseModel):
    """
    Represents an accounting expense from ECD.
    Used for expense credits calculation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    account_code: str = Field(..., description="Chart of accounts code")
    account_description: Optional[str] = Field(None, description="Account name")
    reference_code: Optional[str] = Field(None, description="Reference chart code")
    value: Decimal = Field(..., description="Account value/balance")
    is_debit: bool = Field(..., description="True if debit, False if credit")


class SPEDData(BaseModel):
    """
    Main data structure for parsed SPED file.
    Provides three levels of API access:
    - Level 1 (High): Typed business data (sales_items, purchase_items, expenses)
    - Level 2 (Mid): get_register(code) returns any register as list[dict]
    - Level 3 (Low): raw_dataframe property returns full pandas DataFrame
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # ━━━ Level 1: High-level typed data ━━━
    file_type: Literal["contribuicoes", "fiscal", "ecd"]
    header: SPEDHeader
    sales_items: list[SPEDItem] = Field(default_factory=list)
    purchase_items: list[SPEDItem] = Field(default_factory=list)
    expenses: list[SPEDExpense] = Field(default_factory=list)

    # ━━━ Internal: Raw DataFrame for levels 2 & 3 ━━━
    _raw_df: Optional[pd.DataFrame] = None

    @property
    def raw_dataframe(self) -> pd.DataFrame:
        """
        Level 3: Get raw pandas DataFrame with all registers.

        Returns:
            Full DataFrame with all parsed records.

        Example:
            >>> data = parser.parse_file("file.txt")
            >>> df = data.raw_dataframe
            >>> c197 = df[df['0'] == 'C197']
        """
        if self._raw_df is None:
            raise ValueError("Raw DataFrame not available (file not parsed yet)")
        return self._raw_df

    def get_register(self, code: str) -> list[dict]:
        """
        Level 2: Get any register by code as list of dictionaries.

        Args:
            code: Register code (e.g., 'M100', 'C100', 'E110')

        Returns:
            List of dictionaries, one per record matching the code.
            Column names are string indices ('0', '1', '2', etc.)

        Example:
            >>> data = parser.parse_file("file.txt")
            >>> m100_records = data.get_register('M100')
            >>> for record in m100_records:
            ...     print(record['7'])  # VL_CRED
        """
        if self._raw_df is None:
            raise ValueError("Raw DataFrame not available (file not parsed yet)")

        rows = self._raw_df[self._raw_df["0"] == code]
        return rows.to_dict("records")

    def set_raw_dataframe(self, df: pd.DataFrame) -> None:
        """
        Internal method to set the raw DataFrame.
        Called by parsers after reading the file.
        """
        self._raw_df = df


class ReformImpactReport(BaseModel):
    """
    Tax reform impact analysis report.
    Compares current tax burden vs projected under new tax reform rules.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cnpj: str = Field(..., pattern=r"^\d{14}$")
    company_name: str
    period: str = Field(..., description="Analysis period (e.g., '2024-01')")
    analysis_year: int = Field(..., description="Target year for reform projection")

    # Current taxes (PIS/COFINS/ICMS)
    current_pis: Decimal
    current_cofins: Decimal
    current_icms: Decimal
    current_total: Decimal

    # Projected taxes (IBS/CBS/IS)
    projected_ibs: Decimal
    projected_cbs: Decimal
    projected_is: Decimal
    projected_total: Decimal

    # Impact
    change_absolute: Decimal = Field(..., description="Absolute change (positive = increase)")
    change_percent: Decimal = Field(..., description="Percentage change")

    # Detailed breakdown
    items: list[dict] = Field(default_factory=list, description="NCM-level breakdown")
