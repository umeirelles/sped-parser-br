"""
SPED constants and reference data.

This package contains all constant values used in SPED file parsing:
- CST codes (PIS/COFINS and ICMS)
- CFOP codes and descriptions
- UF codes and state names
- Record layouts with column positions
- Parent register codes for hierarchy
- Operation indicators and document status codes
"""

from .cst import CST_PIS_COFINS, CST_ICMS
from .cfop import CFOP_DESCRIPTIONS
from .uf import UF_CODES
from .indicators import IND_OPER, COD_SIT, NAT_BC_CRED
from .layouts import (
    ENCODING,
    DELIMITER,
    CHUNK_SIZE,
    COLUMN_COUNT_CONTRIB,
    COLUMN_COUNT_FISCAL,
    COLUMN_COUNT_ECD,
    EFDContribuicoesLayout,
    EFDFiscalLayout,
    ECDLayout,
    PARENT_CODES_CONTRIBUICOES,
    PARENT_CODES_FISCAL,
    PARENT_CODES_ECD,
)

__all__ = [
    # CST codes
    "CST_PIS_COFINS",
    "CST_ICMS",
    # CFOP codes
    "CFOP_DESCRIPTIONS",
    # UF codes
    "UF_CODES",
    # Indicators
    "IND_OPER",
    "COD_SIT",
    "NAT_BC_CRED",
    # Parsing constants
    "ENCODING",
    "DELIMITER",
    "CHUNK_SIZE",
    "COLUMN_COUNT_CONTRIB",
    "COLUMN_COUNT_FISCAL",
    "COLUMN_COUNT_ECD",
    # Layouts
    "EFDContribuicoesLayout",
    "EFDFiscalLayout",
    "ECDLayout",
    # Parent codes
    "PARENT_CODES_CONTRIBUICOES",
    "PARENT_CODES_FISCAL",
    "PARENT_CODES_ECD",
]
