"""
Operation indicators and document status codes for SPED files.

These constants are critical for FISCALIA tax reform simulation:
- IND_OPER: Determines if operation is entrada (purchase) or saída (sale)
- COD_SIT: Document status (regular, canceled, denied, etc.)
- NAT_BC_CRED: Nature of credit base - essential for LC 214 credit classification
"""

# IND_OPER - Operation Indicator
# Determines if transaction is entrada (purchase/input) or saída (sale/output)
IND_OPER = {
    "0": "Entrada",
    "1": "Saida",
}

# COD_SIT - Document Situation Codes
# Indicates document status (regular, canceled, denied, etc.)
COD_SIT = {
    "00": "Documento regular",
    "01": "Documento regular extemporaneo",
    "02": "Documento cancelado",
    "03": "Documento cancelado extemporaneo",
    "04": "NFe denegada",
    "05": "NFe numeracao inutilizada",
    "06": "Documento fiscal complementar",
    "07": "Documento fiscal complementar extemporaneo",
    "08": "Documento fiscal emitido com base em Regime Especial ou Norma Especifica",
}

# NAT_BC_CRED - Nature of Credit Base
# CRITICAL for LC 214 credit classification and recalculation
# Determines what type of input/expense generates credit
NAT_BC_CRED = {
    "01": "Aquisicao de bens para revenda",
    "02": "Aquisicao de bens utilizados como insumo",
    "03": "Aquisicao de servicos utilizados como insumo",
    "04": "Energia eletrica e termica, inclusive sob a forma de vapor",
    "05": "Alugueis de predios",
    "06": "Alugueis de maquinas e equipamentos",
    "07": "Armazenagem de mercadoria e frete na operacao de venda",
    "08": "Contraprestacoes de arrendamento mercantil",
    "09": "Maquinas, equipamentos e outros bens incorporados ao ativo imobilizado (credito sobre encargos de depreciacao)",
    "10": "Maquinas, equipamentos e outros bens incorporados ao ativo imobilizado (credito com base no valor de aquisicao)",
    "11": "Amortizacao e depreciacao de edificacoes e benfeitorias em imoveis",
    "12": "Devolucao de vendas sujeitas a incidencia nao-cumulativa",
    "13": "Outras operacoes com direito a credito",
    "14": "Atividade de transporte de cargas - subcontratacao",
    "15": "Atividade de transporte de cargas - vendas com tributacao monofasica",
    "16": "Outras situacoes",
}

# IBGE_UF_CODES - IBGE State Codes to UF Mapping
# Maps the first 2 digits of COD_MUN (IBGE municipality code) to UF state code
# Used to extract participant UF from 0150 records
IBGE_UF_CODES = {
    "11": "RO",  # Rondônia
    "12": "AC",  # Acre
    "13": "AM",  # Amazonas
    "14": "RR",  # Roraima
    "15": "PA",  # Pará
    "16": "AP",  # Amapá
    "17": "TO",  # Tocantins
    "21": "MA",  # Maranhão
    "22": "PI",  # Piauí
    "23": "CE",  # Ceará
    "24": "RN",  # Rio Grande do Norte
    "25": "PB",  # Paraíba
    "26": "PE",  # Pernambuco
    "27": "AL",  # Alagoas
    "28": "SE",  # Sergipe
    "29": "BA",  # Bahia
    "31": "MG",  # Minas Gerais
    "32": "ES",  # Espírito Santo
    "33": "RJ",  # Rio de Janeiro
    "35": "SP",  # São Paulo
    "41": "PR",  # Paraná
    "42": "SC",  # Santa Catarina
    "43": "RS",  # Rio Grande do Sul
    "50": "MS",  # Mato Grosso do Sul
    "51": "MT",  # Mato Grosso
    "52": "GO",  # Goiás
    "53": "DF",  # Distrito Federal
}
