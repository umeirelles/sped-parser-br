"""
SPED file record layouts and parent register codes.

This module defines:
- Column positions for each record type (as dictionaries mapping field names to column indices)
- Parent register codes for hierarchy construction
- Encoding and parsing constants
"""

# File encoding and parsing
ENCODING = 'latin-1'
DELIMITER = '|'
CHUNK_SIZE = 200_000

# Column counts for different file types
COLUMN_COUNT_CONTRIB = 40  # SPED Contribuições
COLUMN_COUNT_FISCAL = 42   # SPED Fiscal
COLUMN_COUNT_ECD = 40      # ECD


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EFD CONTRIBUIÇÕES LAYOUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class EFDContribuicoesLayout:
    """Record layouts for EFD Contribuições (PIS/COFINS)."""

    # Bloco 0: Opening, Identification and References
    RECORD_0000 = {
        'REG': 0,
        'COD_VER': 1,
        'TIPO_ESCRIT': 2,
        'IND_SIT_ESP': 3,
        'NUM_REC_ANTERIOR': 4,
        'DT_INI': 5,
        'DT_FIN': 6,
        'NOME': 7,
        'CNPJ': 8,
        'UF': 9,
        'COD_MUN': 10,
        'SUFRAMA': 11,
        'IND_NAT_PJ': 12,
        'IND_ATIV': 13,
    }

    RECORD_0140 = {
        'REG': 0,
        'COD_EST': 1,
        'NOME': 2,
        'CNPJ': 3,
        'UF': 4,
        'IE': 5,
        'COD_MUN': 6,
        'IM': 7,
        'SUFRAMA': 8,
    }

    RECORD_0200 = {
        'REG': 0,
        'COD_ITEM': 1,
        'DESCR_ITEM': 2,
        'COD_BARRA': 3,
        'COD_ANT_ITEM': 4,
        'UNID_INV': 5,
        'TIPO_ITEM': 6,
        'COD_NCM': 7,
        'EX_IPI': 8,
        'COD_GEN': 9,
    }

    # Bloco A: Services Documents
    RECORD_A100 = {
        'REG': 0,
        'IND_OPER': 1,
        'IND_EMIT': 2,
        'COD_PART': 3,
        'COD_SIT': 4,
        'SER': 5,
        'SUB': 6,
        'NUM_DOC': 7,
        'CHV_NFSE': 8,
        'DT_DOC': 9,
        'DT_EXE_SERV': 10,
        'VL_DOC': 11,
        'IND_PGTO': 12,
        'VL_DESC': 13,
        'VL_PIS': 14,
        'VL_COFINS': 15,
        'VL_PIS_RET': 16,
        'VL_COFINS_RET': 17,
        'VL_ISS': 18,
    }

    RECORD_A170 = {
        'REG': 0,
        'NUM_ITEM': 1,
        'COD_ITEM': 2,
        'DESCR_COMPL': 3,
        'VL_ITEM': 4,
        'VL_DESC': 5,
        'NAT_BC_CRED': 6,
        'IND_ORIG_CRED': 7,
        'CST_PIS': 8,
        'VL_BC_PIS': 9,
        'ALIQ_PIS': 10,
        'VL_PIS': 11,
        'CST_COFINS': 12,
        'VL_BC_COFINS': 13,
        'ALIQ_COFINS': 14,
        'VL_COFINS': 15,
        'COD_CTA': 16,
        'COD_CCUS': 17,
    }

    # Bloco C: Fiscal Documents - Goods
    RECORD_C100 = {
        'REG': 0,
        'IND_OPER': 1,
        'IND_EMIT': 2,
        'COD_PART': 3,
        'COD_MOD': 4,
        'COD_SIT': 5,
        'SER': 6,
        'NUM_DOC': 7,
        'CHV_NFE': 8,
        'DT_DOC': 9,
        'DT_E_S': 10,
        'VL_DOC': 11,
        'IND_PGTO': 12,
        'VL_DESC': 13,
        'VL_ABAT_NT': 14,
        'VL_MERC': 15,
        'IND_FRT': 16,
        'VL_FRT': 17,
        'VL_SEG': 18,
        'VL_OUT_DA': 19,
        'VL_BC_ICMS': 20,
        'VL_ICMS': 21,
        'VL_BC_ICMS_ST': 22,
        'VL_ICMS_ST': 23,
        'VL_IPI': 24,
        'VL_PIS': 25,
        'VL_COFINS': 26,
        'VL_PIS_ST': 27,
        'VL_COFINS_ST': 28,
    }

    RECORD_C170 = {
        'REG': 0,
        'NUM_ITEM': 1,
        'COD_ITEM': 2,
        'DESCR_COMPL': 3,
        'QTD': 4,
        'UNID': 5,
        'VL_ITEM': 6,
        'VL_DESC': 7,
        'IND_MOV': 8,
        'CST_ICMS': 9,
        'CFOP': 10,
        'COD_NAT': 11,
        'VL_BC_ICMS': 12,
        'ALIQ_ICMS': 13,
        'VL_ICMS': 14,
        'VL_BC_ICMS_ST': 15,
        'ALIQ_ST': 16,
        'VL_ICMS_ST': 17,
        'IND_APUR': 18,
        'CST_PIS': 19,
        'VL_BC_PIS': 20,
        'ALIQ_PIS': 21,
        'QUANT_BC_PIS': 22,
        'ALIQ_PIS_QUANT': 23,
        'VL_PIS': 24,
        'CST_COFINS': 25,
        'VL_BC_COFINS': 26,
        'ALIQ_COFINS': 27,
        'QUANT_BC_COFINS': 28,
        'ALIQ_COFINS_QUANT': 29,
        'VL_COFINS': 30,
        'COD_CTA': 31,
    }

    # Bloco M: Calculation of PIS/COFINS Contribution
    RECORD_M100 = {
        'REG': 0,
        'COD_CRED': 1,
        'IND_CRED_ORI': 2,
        'VL_BC_COFINS': 3,
        'ALIQ_COFINS': 4,
        'QUANT_BC_COFINS': 5,
        'ALIQ_COFINS_QUANT': 6,
        'VL_CRED': 7,
        'VL_AJUS_ACRES': 8,
        'VL_AJUS_REDUC': 9,
        'VL_CRED_DIF': 10,
        'VL_CRED_DISP': 11,
        'IND_DESC_CRED': 12,
        'VL_CRED_DESC': 13,
        'SLD_CRED': 14,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EFD FISCAL LAYOUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class EFDFiscalLayout:
    """Record layouts for EFD Fiscal (ICMS/IPI)."""

    # Bloco 0: Opening, Identification and References
    RECORD_0000 = {
        'REG': 0,
        'COD_VER': 1,
        'COD_FIN': 2,
        'DT_INI': 3,
        'DT_FIN': 4,
        'NOME': 5,
        'CNPJ': 6,
        'CPF': 7,
        'UF': 8,
        'IE': 9,
        'COD_MUN': 10,
        'IM': 11,
        'SUFRAMA': 12,
        'IND_PERFIL': 13,
        'IND_ATIV': 14,
    }

    RECORD_0150 = {
        'REG': 0,
        'COD_PART': 1,
        'NOME': 2,
        'COD_PAIS': 3,
        'CNPJ': 4,
        'CPF': 5,
        'IE': 6,
        'COD_MUN': 7,
        'SUFRAMA': 8,
        'END': 9,
        'NUM': 10,
        'COMPL': 11,
        'BAIRRO': 12,
    }

    RECORD_0200 = {
        'REG': 0,
        'COD_ITEM': 1,
        'DESCR_ITEM': 2,
        'COD_BARRA': 3,
        'COD_ANT_ITEM': 4,
        'UNID_INV': 5,
        'TIPO_ITEM': 6,
        'COD_NCM': 7,
        'EX_IPI': 8,
        'COD_GEN': 9,
        'COD_LST': 10,
        'ALIQ_ICMS': 11,
    }

    # Bloco C: Fiscal Documents - Goods
    RECORD_C100 = {
        'REG': 0,
        'IND_OPER': 1,
        'IND_EMIT': 2,
        'COD_PART': 3,
        'COD_MOD': 4,
        'COD_SIT': 5,
        'SER': 6,
        'NUM_DOC': 7,
        'CHV_NFE': 8,
        'DT_DOC': 9,
        'DT_E_S': 10,
        'VL_DOC': 11,
        'IND_PGTO': 12,
        'VL_DESC': 13,
        'VL_ABAT_NT': 14,
        'VL_MERC': 15,
        'IND_FRT': 16,
        'VL_FRT': 17,
        'VL_SEG': 18,
        'VL_OUT_DA': 19,
        'VL_BC_ICMS': 20,
        'VL_ICMS': 21,
        'VL_BC_ICMS_ST': 22,
        'VL_ICMS_ST': 23,
        'VL_IPI': 24,
        'VL_PIS': 25,
        'VL_COFINS': 26,
        'VL_PIS_ST': 27,
        'VL_COFINS_ST': 28,
    }

    RECORD_C170 = {
        'REG': 0,
        'NUM_ITEM': 1,
        'COD_ITEM': 2,
        'DESCR_COMPL': 3,
        'QTD': 4,
        'UNID': 5,
        'VL_ITEM': 6,
        'VL_DESC': 7,
        'IND_MOV': 8,
        'CST_ICMS': 9,
        'CFOP': 10,
        'COD_NAT': 11,
        'VL_BC_ICMS': 12,
        'ALIQ_ICMS': 13,
        'VL_ICMS': 14,
        'VL_BC_ICMS_ST': 15,
        'ALIQ_ST': 16,
        'VL_ICMS_ST': 17,
        'IND_APUR': 18,
        'CST_IPI': 19,
        'COD_ENQ': 20,
        'VL_BC_IPI': 21,
        'ALIQ_IPI': 22,
        'VL_IPI': 23,
        'CST_PIS': 24,
        'VL_BC_PIS': 25,
        'ALIQ_PIS': 26,
        'QUANT_BC_PIS': 27,
        'ALIQ_PIS_QUANT': 28,
        'VL_PIS': 29,
        'CST_COFINS': 30,
        'VL_BC_COFINS': 31,
        'ALIQ_COFINS': 32,
        'QUANT_BC_COFINS': 33,
        'ALIQ_COFINS_QUANT': 34,
        'VL_COFINS': 35,
        'COD_CTA': 36,
    }

    RECORD_C190 = {
        'REG': 0,
        'CST_ICMS': 1,
        'CFOP': 2,
        'ALIQ_ICMS': 3,
        'VL_OPR': 4,
        'VL_BC_ICMS': 5,
        'VL_ICMS': 6,
        'VL_BC_ICMS_ST': 7,
        'VL_ICMS_ST': 8,
        'VL_RED_BC': 9,
        'VL_IPI': 10,
        'COD_OBS': 11,
    }

    # Bloco E: ICMS - Assessment
    RECORD_E110 = {
        'REG': 0,
        'VL_TOT_DEBITOS': 1,
        'VL_AJ_DEBITOS': 2,
        'VL_TOT_AJ_DEBITOS': 3,
        'VL_ESTORNOS_CRED': 4,
        'VL_TOT_CREDITOS': 5,
        'VL_AJ_CREDITOS': 6,
        'VL_TOT_AJ_CREDITOS': 7,
        'VL_ESTORNOS_DEB': 8,
        'VL_SLD_CREDOR_ANT': 9,
        'VL_SLD_APURADO': 10,
        'VL_TOT_DED': 11,
        'VL_ICMS_RECOLHER': 12,
        'VL_SLD_CREDOR_TRANSPORTAR': 13,
        'DEB_ESP': 14,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ECD LAYOUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ECDLayout:
    """Record layouts for ECD (Escrituração Contábil Digital)."""

    # Bloco 0: Opening
    RECORD_0000 = {
        'REG': 0,
        'LECD': 1,
        'DT_INI': 2,
        'DT_FIN': 3,
        'NOME': 4,
        'CNPJ': 5,
        'UF': 6,
        'IE': 7,
        'COD_MUN': 8,
        'IM': 9,
        'IND_SIT_ESP': 10,
        'IND_SIT_INI_PER': 11,
        'IND_NIRE': 12,
        'IND_FIN_ESC': 13,
        'COD_HASH_SUB': 14,
        'NIRE': 15,
    }

    # Bloco I: Chart of Accounts and P&L
    RECORD_I050 = {
        'REG': 0,
        'DT_ALT': 1,
        'COD_NAT': 2,
        'IND_CTA': 3,
        'NIVEL': 4,
        'COD_CTA': 5,
        'NOME_CTA': 6,
    }

    RECORD_I051 = {
        'REG': 0,
        'COD_CCUS': 1,
        'COD_CTA_REF': 2,
    }

    RECORD_I155 = {
        'REG': 0,
        'COD_CTA': 1,
        'COD_CCUS': 2,
        'VL_SLD_INI': 3,
        'IND_DC_INI': 4,
        'VL_DEB': 5,
        'VL_CRED': 6,
        'VL_SLD_FIN': 7,
        'IND_DC_FIN': 8,
    }

    RECORD_I355 = {
        'REG': 0,
        'COD_CTA': 1,
        'COD_CCUS': 2,
        'VL_CTA': 3,
        'IND_VL': 4,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PARENT REGISTER CODES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


PARENT_CODES_CONTRIBUICOES = [
    "0000", "0140", "A100", "C100", "C180", "C190", "C380", "C400", "C500",
    "C600", "C800", "D100", "D500", "F100", "F120", "F130", "F150", "F200",
    "F500", "F600", "F700", "F800", "I100", "M100", "M200", "M300", "M350",
    "M400", "M500", "M600", "M700", "M800", "P100", "P200", "1010", "1020",
    "1050", "1100", "1200", "1300", "1500", "1600", "1700", "1800", "1900"
]

PARENT_CODES_FISCAL = [
    "0000",
    "C100", "C300", "C350", "C400", "C495", "C500", "C600", "C700", "C800", "C860",
    "D100", "D300", "D350", "D400", "D500", "D600", "D695", "D700", "D750",
    "E100", "E200", "E300", "E500",
    "G110",
    "H005",
    "K100", "K200", "K210", "K220", "K230", "K250", "K260", "K270", "K280", "K290", "K300",
    "1100", "1200", "1300", "1350", "1390", "1400", "1500", "1600", "1601", "1700", "1800",
    "1900", "1960", "1970", "1980"
]

PARENT_CODES_ECD = [
    "0000", "0001", "C001", "C040", "C050", "C150", "C600", "I001", "I010", "I050", "I150"
]
