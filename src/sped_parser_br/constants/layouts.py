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
        'REG': 1,
        'COD_VER': 2,
        'TIPO_ESCRIT': 3,
        'IND_SIT_ESP': 4,
        'NUM_REC_ANTERIOR': 5,
        'DT_INI': 6,
        'DT_FIN': 7,
        'NOME': 8,
        'CNPJ': 9,
        'UF': 10,
        'COD_MUN': 11,
        'SUFRAMA': 12,
        'IND_NAT_PJ': 13,
        'IND_ATIV': 14,
    }

    RECORD_0140 = {
        'REG': 1,
        'COD_EST': 2,
        'NOME': 3,
        'CNPJ': 4,
        'UF': 5,
        'IE': 6,
        'COD_MUN': 7,
        'IM': 8,
        'SUFRAMA': 9,
    }

    RECORD_0200 = {
        'REG': 1,
        'COD_ITEM': 2,
        'DESCR_ITEM': 3,
        'COD_BARRA': 4,
        'COD_ANT_ITEM': 5,
        'UNID_INV': 6,
        'TIPO_ITEM': 7,
        'COD_NCM': 8,
        'EX_IPI': 9,
        'COD_GEN': 10,
    }

    # Bloco A: Services Documents
    RECORD_A100 = {
        'REG': 1,
        'IND_OPER': 2,
        'IND_EMIT': 3,
        'COD_PART': 4,
        'COD_SIT': 5,
        'SER': 6,
        'SUB': 7,
        'NUM_DOC': 8,
        'CHV_NFSE': 9,
        'DT_DOC': 10,
        'DT_EXE_SERV': 11,
        'VL_DOC': 12,
        'IND_PGTO': 13,
        'VL_DESC': 14,
        'VL_PIS': 15,
        'VL_COFINS': 16,
        'VL_PIS_RET': 17,
        'VL_COFINS_RET': 18,
        'VL_ISS': 19,
    }

    RECORD_A170 = {
        'REG': 1,
        'NUM_ITEM': 2,
        'COD_ITEM': 3,
        'DESCR_COMPL': 4,
        'VL_ITEM': 5,
        'VL_DESC': 6,
        'NAT_BC_CRED': 7,
        'IND_ORIG_CRED': 8,
        'CST_PIS': 9,
        'VL_BC_PIS': 10,
        'ALIQ_PIS': 11,
        'VL_PIS': 12,
        'CST_COFINS': 13,
        'VL_BC_COFINS': 14,
        'ALIQ_COFINS': 15,
        'VL_COFINS': 16,
        'COD_CTA': 17,
        'COD_CCUS': 18,
    }

    # Bloco C: Fiscal Documents - Goods
    RECORD_C100 = {
        'REG': 1,
        'IND_OPER': 2,
        'IND_EMIT': 3,
        'COD_PART': 4,
        'COD_MOD': 5,
        'COD_SIT': 6,
        'SER': 7,
        'NUM_DOC': 8,
        'CHV_NFE': 9,
        'DT_DOC': 10,
        'DT_E_S': 11,
        'VL_DOC': 12,
        'IND_PGTO': 13,
        'VL_DESC': 14,
        'VL_ABAT_NT': 15,
        'VL_MERC': 16,
        'IND_FRT': 17,
        'VL_FRT': 18,
        'VL_SEG': 19,
        'VL_OUT_DA': 20,
        'VL_BC_ICMS': 21,
        'VL_ICMS': 22,
        'VL_BC_ICMS_ST': 23,
        'VL_ICMS_ST': 24,
        'VL_IPI': 25,
        'VL_PIS': 26,
        'VL_COFINS': 27,
        'VL_PIS_ST': 28,
        'VL_COFINS_ST': 29,
    }

    RECORD_C170 = {
        'REG': 1,
        'NUM_ITEM': 2,
        'COD_ITEM': 3,
        'DESCR_COMPL': 4,
        'QTD': 5,
        'UNID': 6,
        'VL_ITEM': 7,
        'VL_DESC': 8,
        'IND_MOV': 9,
        'CST_ICMS': 10,
        'CFOP': 11,
        'COD_NAT': 12,
        'VL_BC_ICMS': 13,
        'ALIQ_ICMS': 14,
        'VL_ICMS': 15,
        'VL_BC_ICMS_ST': 16,
        'ALIQ_ST': 17,
        'VL_ICMS_ST': 18,
        'IND_APUR': 19,
        'CST_PIS': 20,
        'VL_BC_PIS': 21,
        'ALIQ_PIS': 22,
        'QUANT_BC_PIS': 23,
        'ALIQ_PIS_QUANT': 24,
        'VL_PIS': 25,
        'CST_COFINS': 26,
        'VL_BC_COFINS': 27,
        'ALIQ_COFINS': 28,
        'QUANT_BC_COFINS': 29,
        'ALIQ_COFINS_QUANT': 30,
        'VL_COFINS': 31,
        'COD_CTA': 32,
    }

    # Bloco M: Calculation of PIS/COFINS Contribution
    RECORD_M100 = {
        'REG': 1,
        'COD_CRED': 2,
        'IND_CRED_ORI': 3,
        'VL_BC_COFINS': 4,
        'ALIQ_COFINS': 5,
        'QUANT_BC_COFINS': 6,
        'ALIQ_COFINS_QUANT': 7,
        'VL_CRED': 8,
        'VL_AJUS_ACRES': 9,
        'VL_AJUS_REDUC': 10,
        'VL_CRED_DIF': 11,
        'VL_CRED_DISP': 12,
        'IND_DESC_CRED': 13,
        'VL_CRED_DESC': 14,
        'SLD_CRED': 15,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EFD FISCAL LAYOUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class EFDFiscalLayout:
    """Record layouts for EFD Fiscal (ICMS/IPI)."""

    # Bloco 0: Opening, Identification and References
    RECORD_0000 = {
        'REG': 1,
        'COD_VER': 2,
        'COD_FIN': 3,
        'DT_INI': 4,
        'DT_FIN': 5,
        'NOME': 6,
        'CNPJ': 7,
        'CPF': 8,
        'UF': 9,
        'IE': 10,
        'COD_MUN': 11,
        'IM': 12,
        'SUFRAMA': 13,
        'IND_PERFIL': 14,
        'IND_ATIV': 15,
    }

    RECORD_0150 = {
        'REG': 1,
        'COD_PART': 2,
        'NOME': 3,
        'COD_PAIS': 4,
        'CNPJ': 5,
        'CPF': 6,
        'IE': 7,
        'COD_MUN': 8,
        'SUFRAMA': 9,
        'END': 10,
        'NUM': 11,
        'COMPL': 12,
        'BAIRRO': 13,
    }

    RECORD_0200 = {
        'REG': 1,
        'COD_ITEM': 2,
        'DESCR_ITEM': 3,
        'COD_BARRA': 4,
        'COD_ANT_ITEM': 5,
        'UNID_INV': 6,
        'TIPO_ITEM': 7,
        'COD_NCM': 8,
        'EX_IPI': 9,
        'COD_GEN': 10,
        'COD_LST': 11,
        'ALIQ_ICMS': 12,
    }

    # Bloco C: Fiscal Documents - Goods
    RECORD_C100 = {
        'REG': 1,
        'IND_OPER': 2,
        'IND_EMIT': 3,
        'COD_PART': 4,
        'COD_MOD': 5,
        'COD_SIT': 6,
        'SER': 7,
        'NUM_DOC': 8,
        'CHV_NFE': 9,
        'DT_DOC': 10,
        'DT_E_S': 11,
        'VL_DOC': 12,
        'IND_PGTO': 13,
        'VL_DESC': 14,
        'VL_ABAT_NT': 15,
        'VL_MERC': 16,
        'IND_FRT': 17,
        'VL_FRT': 18,
        'VL_SEG': 19,
        'VL_OUT_DA': 20,
        'VL_BC_ICMS': 21,
        'VL_ICMS': 22,
        'VL_BC_ICMS_ST': 23,
        'VL_ICMS_ST': 24,
        'VL_IPI': 25,
        'VL_PIS': 26,
        'VL_COFINS': 27,
        'VL_PIS_ST': 28,
        'VL_COFINS_ST': 29,
    }

    RECORD_C170 = {
        'REG': 1,
        'NUM_ITEM': 2,
        'COD_ITEM': 3,
        'DESCR_COMPL': 4,
        'QTD': 5,
        'UNID': 6,
        'VL_ITEM': 7,
        'VL_DESC': 8,
        'IND_MOV': 9,
        'CST_ICMS': 10,
        'CFOP': 11,
        'COD_NAT': 12,
        'VL_BC_ICMS': 13,
        'ALIQ_ICMS': 14,
        'VL_ICMS': 15,
        'VL_BC_ICMS_ST': 16,
        'ALIQ_ST': 17,
        'VL_ICMS_ST': 18,
        'IND_APUR': 19,
        'CST_IPI': 20,
        'COD_ENQ': 21,
        'VL_BC_IPI': 22,
        'ALIQ_IPI': 23,
        'VL_IPI': 24,
        'CST_PIS': 25,
        'VL_BC_PIS': 26,
        'ALIQ_PIS': 27,
        'QUANT_BC_PIS': 28,
        'ALIQ_PIS_QUANT': 29,
        'VL_PIS': 30,
        'CST_COFINS': 31,
        'VL_BC_COFINS': 32,
        'ALIQ_COFINS': 33,
        'QUANT_BC_COFINS': 34,
        'ALIQ_COFINS_QUANT': 35,
        'VL_COFINS': 36,
        'COD_CTA': 37,
    }

    RECORD_C190 = {
        'REG': 1,
        'CST_ICMS': 2,
        'CFOP': 3,
        'ALIQ_ICMS': 4,
        'VL_OPR': 5,
        'VL_BC_ICMS': 6,
        'VL_ICMS': 7,
        'VL_BC_ICMS_ST': 8,
        'VL_ICMS_ST': 9,
        'VL_RED_BC': 10,
        'VL_IPI': 11,
        'COD_OBS': 12,
    }

    # Bloco E: ICMS - Assessment
    RECORD_E110 = {
        'REG': 1,
        'VL_TOT_DEBITOS': 2,
        'VL_AJ_DEBITOS': 3,
        'VL_TOT_AJ_DEBITOS': 4,
        'VL_ESTORNOS_CRED': 5,
        'VL_TOT_CREDITOS': 6,
        'VL_AJ_CREDITOS': 7,
        'VL_TOT_AJ_CREDITOS': 8,
        'VL_ESTORNOS_DEB': 9,
        'VL_SLD_CREDOR_ANT': 10,
        'VL_SLD_APURADO': 11,
        'VL_TOT_DED': 12,
        'VL_ICMS_RECOLHER': 13,
        'VL_SLD_CREDOR_TRANSPORTAR': 14,
        'DEB_ESP': 15,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ECD LAYOUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ECDLayout:
    """Record layouts for ECD (Escrituração Contábil Digital)."""

    # Bloco 0: Opening
    RECORD_0000 = {
        'REG': 1,
        'LECD': 2,
        'DT_INI': 3,
        'DT_FIN': 4,
        'NOME': 5,
        'CNPJ': 6,
        'UF': 7,
        'IE': 8,
        'COD_MUN': 9,
        'IM': 10,
        'IND_SIT_ESP': 11,
        'IND_SIT_INI_PER': 12,
        'IND_NIRE': 13,
        'IND_FIN_ESC': 14,
        'COD_HASH_SUB': 15,
        'NIRE': 16,
    }

    # Bloco I: Chart of Accounts and P&L
    RECORD_I050 = {
        'REG': 1,
        'DT_ALT': 2,
        'COD_NAT': 3,
        'IND_CTA': 4,
        'NIVEL': 5,
        'COD_CTA': 6,
        'NOME_CTA': 7,
    }

    RECORD_I051 = {
        'REG': 1,
        'COD_CCUS': 2,
        'COD_CTA_REF': 3,
    }

    RECORD_I155 = {
        'REG': 1,
        'COD_CTA': 2,
        'COD_CCUS': 3,
        'VL_SLD_INI': 4,
        'IND_DC_INI': 5,
        'VL_DEB': 6,
        'VL_CRED': 7,
        'VL_SLD_FIN': 8,
        'IND_DC_FIN': 9,
    }

    RECORD_I355 = {
        'REG': 1,
        'COD_CTA': 2,
        'COD_CCUS': 3,
        'VL_CTA': 4,
        'IND_VL': 5,
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
