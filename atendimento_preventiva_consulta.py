"""
Consultas e estruturas de dados para o módulo de Atendimento Preventivo
"""

from dataclasses import dataclass, field
from typing import List, Optional


MAPEAMENTO_PATRIMONIO_ATIVIDADE = {
    'FEL': 'COLHEITA',
    'GAR': 'COLHEITA',
    'GRU': 'COLHEITA',
    'SKD': 'COLHEITA',
    'PAC': 'SILVICULTURA',
    'TRA': 'SILVICULTURA',
    'CMK': 'CARVOARIA',
    'CTC': 'CARVOARIA',
    'CTL': 'CARVOARIA',
    'CTQ': 'CARVOARIA',
    'CPP': 'CARVOARIA',
    'ONB': 'AGRICULTURA',
    'VCL': 'AGRICULTURA',
    'VPG': 'AGRICULTURA',
    'VPL': 'AGRICULTURA',
}

ATIVIDADES_DISPONIVEIS = [
    'SILVICULTURA',
    'COLHEITA',
    'CARVOARIA',
    'OBRAS CIVIS',
    'AGRICULTURA',
    'PECUARIA'
]


def get_atividade_from_patrimonio(patrimonio: str) -> str:
    """Retorna a atividade baseada no prefixo do patrimônio"""
    if not patrimonio:
        return 'SILVICULTURA'
    prefixo = patrimonio[:3].upper()
    return MAPEAMENTO_PATRIMONIO_ATIVIDADE.get(prefixo, 'SILVICULTURA')


@dataclass
class Equipment:
    """Representa um equipamento com informações de manutenção"""
    id: int
    patrimonio: str
    name: str
    status: str
    hours: float
    horimetro: float = 0.0
    data_lancamento: str = ""
    a_fazer: str = ""
    faltando: float = 0.0
    farm_id: Optional[int] = None
    farm_name: Optional[str] = None
    regional: Optional[str] = None
    abbr: Optional[str] = None
    atividade: Optional[str] = None
    tipo: Optional[str] = None

    def __post_init__(self):
        if self.atividade is None:
            self.atividade = get_atividade_from_patrimonio(self.patrimonio)
        
        # Definir tipo baseado no patrimônio (KM para equipamentos específicos)
        if self.tipo is None:
            # Equipamentos que usam KM
            km_prefixes = ['CMK', 'CTC', 'CTL', 'CTQ', 'CPP', 'ONB', 'VCL', 'VPG', 'VPL']
            prefixo = self.patrimonio[:3].upper()
            self.tipo = 'KM' if prefixo in km_prefixes else 'HOR'

    def to_dict(self):
        return {
            'id': self.id,
            'patrimonio': self.patrimonio,
            'name': self.name,
            'status': self.status,
            'hours': self.hours,
            'horimetro': self.horimetro,
            'dataLancamento': self.data_lancamento,
            'aFazer': self.a_fazer,
            'faltando': self.faltando,
            'farmId': self.farm_id,
            'farmName': self.farm_name,
            'regional': self.regional,
            'abbr': self.abbr,
            'atividade': self.atividade,
            'tipo': self.tipo
        }


@dataclass
class Farm:
    """Representa uma fazenda com seus equipamentos"""
    id: int
    name: str
    abbr: str
    lat: float
    lng: float
    regional: str
    equipment: List[Equipment] = field(default_factory=list)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbr': self.abbr,
            'lat': self.lat,
            'lng': self.lng,
            'regional': self.regional,
            'equipment': [e.to_dict() for e in self.equipment]
        }


FAZENDAS_COORDENADAS = {
    "OFICINA POMPEU": [-19.233086, -44.997034, "Pompéu"],
    "ESCRITORIO POMPEU": [-19.233086, -44.997034, "Pompéu"],
    "GRAVATA": [-18.771972, -44.95719, "Felixlândia"],
    "CARAIBAS": [-17.508293, -44.478075, "Felixlândia"],
    "LORENA": [-18.696141, -44.826428, "Felixlândia"],
    "SACO FECHADO": [-18.700495, -44.868714, "Felixlândia"],
    "BOM JARDIM": [-18.645822, -45.307758, "Morada Nova"],
    "BURITIZINHO": [-18.514693, -45.348162, "Morada Nova"],
    "CANDELARIA": [-18.903743, -45.328917, "Morada Nova"],
    "MATINADA E MELANCIAS": [-18.544228, -45.290323, "Morada Nova"],
    "PONTAL": [-18.774347, -45.231318, "Morada Nova"],
    "OFICINA PONTAL": [-18.774347, -45.231318, "Morada Nova"],
    "SANTA HELENA": [-18.537247, -45.361849, "Morada Nova"],
    "APARICAO DE BAIXO": [-19.789592, -44.638523, "Pompéu"],
    "BOCAINA": [-19.262179, -44.787674, "Pompéu"],
    "BREJINHO": [-19.507701, -45.137712, "Pompéu"],
    "BURITI DO MEIO": [-19.320698, -45.261038, "Pompéu"],
    "BURITI GRANDE": [-19.320698, -45.261038, "Morada Nova"],
    "BURITY GRANDE": [-19.320698, -45.261038, "Pompéu"],
    "CANTA GALO": [-19.159901, -45.256149, "Pompéu"],
    "CIPO DO CHUMBO": [-19.42051, -44.80681, "Pompéu"],
    "FURADO": [-19.334842, -45.017132, "Pompéu"],
    "OLHOS DAGUA": [-19.432765, -45.178494, "Pompéu"],
    "PAULISTA": [-19.434739, -44.952723, "Pompéu"],
    "RETIRO DA MARMELADA": [-18.9454, -45.095962, "Pompéu"],
    "CAETITU": [-19.202869, -44.772752, "Pompéu"],
    "PINDAIBAS": [-18.939052, -44.938645, "Pompéu"],
    "SAO GERALDO": [-19.100531, -45.235767, "Pompéu"],
    "GROTA DAGUA": [-19.080386, -45.254644, "Pompéu"],
    "ANDAIME": [-19.795795, -44.683642, "Pompéu"],
    "SANTA QUITERIA": [-18.478492, -45.581518, "Morada Nova"],
    "PALMITAL": [-19.891824, -44.64646, "Pompéu"],
    "CORREGO DAS LAGES": [-18.518715, -45.540127, "Morada Nova"],
    "RIBEIRO MANSO": [-18.834246, -44.801995, "Felixlândia"],
    "MAMONAS": [-19.494709, -45.121617, "Pompéu"],
    "BAGACO": [-18.686688, -45.290644, "Morada Nova"],
    "MATA DO CEDRO": [-19.901446, -44.554349, "Pompéu"],
    "MONJOLINHO": [-19.074022, -44.745408, "Pompéu"],
    "SAO JOAO DO CURRALINHO": [-18.348071, -45.39182, "Morada Nova"],
    "CAPAO SECO": [-18.804976, -44.841958, "Felixlândia"],
    "MATO SECO": [-19.607301, -45.208723, "Pompéu"],
    "POVOACAO": [-18.673136, -45.288634, "Morada Nova"],
    "SAO JOSE": [-19.367274, -45.048546, "Pompéu"],
    "GAMA": [-18.796859, -45.265522, "Morada Nova"],
    "JANDAIA": [-19.104303, -44.618727, "Pompéu"],
    "CACHOEIRA": [-18.602736, -45.264711, "Morada Nova"],
    "PAI LOURENCO": [-18.776974, -45.409541, "Morada Nova"],
    "MARMELADA": [-19.044345, -45.230869, "Pompéu"],
    "MAU CABELO": [-19.111048, -45.261568, "Pompéu"],
    "MOINHO": [-19.337948, -45.197458, "Pompéu"],
    "FECHO": [-19.374867, -45.160855, "Pompéu"],
    "CANOAS": [-19.528661, -45.136652, "Pompéu"],
    "URUCUM": [-19.486345, -45.192972, "Pompéu"],
    "RETIRO": [-19.325246, -44.775401, "Pompéu"],
    "JATAI": [-19.284028, -44.758041, "Pompéu"],
    "BARRA": [-19.441019, -44.64676, "Pompéu"],
    "RIO VELHO": [-19.042765, -44.724462, "Pompéu"],
    "CHAPADA": [-17.141049, -44.495901, "Felixlândia"],
}

# Dados da planilha com tipo incluído
DADOS_PLANILHA = [
    # Formato: (status, patrimonio, horimetro, data_lancamento, alerta, a_fazer, faltando, tipo, fazenda, regional)
    ("VERDE", "FEL1001", 23555.5, "28/11/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "OFICINA POMPEU", "Pompéu"),
    ("VERDE", "GAR1017", 17122.9, "01/12/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "CANTA GALO", "Pompéu"),
    ("VERDE", "GAR1019", 11585.4, "01/12/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "CANTA GALO", "Pompéu"),
    ("VERDE", "GRU1003", 18227.7, "01/12/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "MOINHO", "Pompéu"),
    ("VERDE", "GRU1004", 17753.5, "02/12/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "BOM JARDIM", "Morada Nova"),
    ("VERDE", "GRU1022", 7596.9, "02/12/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "BOM JARDIM", "Morada Nova"),
    ("VERDE", "GRU1023", 7257.6, "01/12/2025", "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE", "17/12/2025", 15, "HOR", "BOM JARDIM", "Morada Nova"),
    ("VERDE", "GRU1009", 16992.7, "02/12/2025", "MANUTENÇAO PREVENTIVA 1000", "17000", 7.3, "HOR", "OFICINA POMPEU", "Pompéu"),
    ("AMARELO", "PAC9103", 13034.4, "28/11/2025", "MANUTENÇAO PREVENTIVA 1000", "13000", -34.4, "HOR", "PONTAL", "Morada Nova"),
    ("AMARELO", "PAC9108", 15028.2, "20/11/2025", "MANUTENÇAO PREVENTIVA 1000", "15000", -28.2, "HOR", "BARRA", "Pompéu"),
    ("VERDE", "PAC9112", 8972.1, "01/12/2025", "MANUTENÇAO PREVENTIVA 1000", "9000", 27.9, "HOR", "GRAVATA", "Felixlândia"),
    ("VERDE", "PAC9124", 12994.0, "05/11/2025", "MANUTENÇAO PREVENTIVA 1000", "13000", 6, "HOR", "FURADO", "Pompéu"),
    ("AMARELO", "SKD1020", 11020.6, "01/12/2025", "MANUTENÇAO PREVENTIVA 1000", "11000", -20.6, "HOR", "PAULISTA", "Pompéu"),
    ("VERDE", "TRA0004", 6932.9, "27/11/2025", "MANUTENÇAO PREVENTIVA 1000", "7000", 67.1, "HOR", "SANTA HELENA", "Morada Nova"),
    ("AMARELO", "TRA0016", 1030.7, "24/11/2025", "MANUTENÇAO PREVENTIVA 1000", "1000", -30.7, "HOR", "RIO VELHO", "Pompéu"),
    ("VERDE", "TRA0027", 2936.1, "20/11/2025", "MANUTENÇAO PREVENTIVA 1000", "3000", 63.9, "HOR", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "TRA0046", 2983.2, "17/11/2025", "MANUTENÇAO PREVENTIVA 1000", "3000", 16.8, "HOR", "CACHOEIRA", "Morada Nova"),
    ("VERDE", "TRA0076", 5942.3, "28/11/2025", "MANUTENÇAO PREVENTIVA 1000", "6000", 57.7, "HOR", "CACHOEIRA", "Morada Nova"),
    ("AMARELO", "TRA0082", 2012.3, "01/12/2025", "MANUTENÇAO PREVENTIVA 1000", "2000", -12.3, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "TRA0062", 9642.2, "20/11/2025", "MANUTENÇAO PREVENTIVA 1200", "9700", 57.8, "HOR", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "GRU1005", 19930.5, "02/12/2025", "MANUTENÇAO PREVENTIVA 2000", "20000", 69.5, "HOR", "BARRA", "Pompéu"),
    ("VERDE", "FEL1028", 735.8, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "750", 14.2, "HOR", "MARMELADA", "Pompéu"),
    ("VERDE", "GRU1003", 18227.7, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "18250", 22.3, "HOR", "MOINHO", "Pompéu"),
    ("VERDE", "GRU1011", 16670.7, "18/11/2025", "MANUTENÇAO PREVENTIVA 250", "16750", 79.3, "HOR", "CARAIBAS", "Felixlândia"),
    ("AMARELO", "GRU1023", 7257.6, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "7250", -7.6, "HOR", "BOM JARDIM", "Morada Nova"),
    ("VERDE", "PAC9101", 8687.1, "26/11/2025", "MANUTENÇAO PREVENTIVA 250", "8750", 62.9, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "PAC9107", 14673.5, "24/11/2025", "MANUTENÇAO PREVENTIVA 250", "14750", 76.5, "HOR", "RIO VELHO", "Pompéu"),
    ("VERDE", "PAC9118", 10752.8, "02/12/2025", "MANUTENÇAO PREVENTIVA 250", "10750", -2.8, "HOR", "JANDAIA", "Pompéu"),
    ("VERDE", "PAC9125", 12235.0, "18/11/2025", "MANUTENÇAO PREVENTIVA 250", "12250", 15, "HOR", "BARRA", "Pompéu"),
    ("VERDE", "PAC9127", 14214.5, "28/11/2025", "MANUTENÇAO PREVENTIVA 250", "14250", 35.5, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "PAC9128", 12221.0, "02/12/2025", "MANUTENÇAO PREVENTIVA 250", "12250", 29, "HOR", "FURADO", "Pompéu"),
    ("VERDE", "PAC9129", 11194.0, "26/11/2025", "MANUTENÇAO PREVENTIVA 250", "11250", 56, "HOR", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "PAC9132", 14448.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "14500", 52, "HOR", "GRAVATA", "Felixlândia"),
    ("VERDE", "PAC9133", 13729.2, "26/11/2025", "MANUTENÇAO PREVENTIVA 250", "13750", 20.8, "HOR", "GRAVATA", "Felixlândia"),
    ("VERMELHO", "PAC9135", 10808.7, "29/11/2025", "MANUTENÇAO PREVENTIVA 250", "10750", -58.7, "HOR", "BOM JARDIM", "Morada Nova"),
    ("AMARELO", "PAC9141", 6753.7, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "6750", -3.7, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "PAC9142", 4697.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "4750", 53, "HOR", "CARAIBAS", "Felixlândia"),
    ("VERDE", "PAC9146", 1208.5, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "1250", 41.5, "HOR", "RETIRO", "Pompéu"),
    ("VERDE", "TRA0013", 14154.4, "27/11/2025", "MANUTENÇAO PREVENTIVA 250", "14250", 95.6, "HOR", "OLHOS DAGUA", "Pompéu"),
    ("VERDE", "TRA0026", 1235.6, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "1250", 14.4, "HOR", "GRAVATA", "Felixlândia"),
    ("AMARELO", "TRA0028", 7251.1, "25/11/2025", "MANUTENÇAO PREVENTIVA 250", "7250", -1.1, "HOR", "CACHOEIRA", "Morada Nova"),
    ("VERDE", "TRA0033", 14672.3, "26/11/2025", "MANUTENÇAO PREVENTIVA 250", "14750", 77.7, "HOR", "RETIRO", "Pompéu"),
    ("VERDE", "TRA0037", 15213.6, "26/11/2025", "MANUTENÇAO PREVENTIVA 250", "15250", 36.4, "HOR", "CHAPADA", "Felixlândia"),
    ("VERDE", "TRA0039", 9680.8, "24/11/2025", "MANUTENÇAO PREVENTIVA 250", "9750", 69.2, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "TRA0045", 2216.9, "27/11/2025", "MANUTENÇAO PREVENTIVA 250", "2250", 33.1, "HOR", "BURITI GRANDE", "Morada Nova"),
    ("VERDE", "TRA0048", 16181.4, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "16250", 68.6, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "TRA0053", 10231.2, "27/11/2025", "MANUTENÇAO PREVENTIVA 250", "10250", 18.8, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "TRA0058", 7665.0, "27/11/2025", "MANUTENÇAO PREVENTIVA 250", "7750", 85, "HOR", "CARAIBAS", "Felixlândia"),
    ("VERDE", "TRA0069", 6232.0, "02/12/2025", "MANUTENÇAO PREVENTIVA 250", "6250", 18, "HOR", "OLHOS DAGUA", "Pompéu"),
    ("VERDE", "TRA0077", 4417.4, "27/11/2025", "MANUTENÇAO PREVENTIVA 250", "4500", 82.6, "HOR", "OLHOS DAGUA", "Pompéu"),
    ("VERDE", "UNI0003", 9675.4, "26/11/2025", "MANUTENÇAO PREVENTIVA 250", "9750", 74.6, "HOR", "CACHOEIRA", "Morada Nova"),
    ("VERDE", "UNI0054", 13715.7, "01/12/2025", "MANUTENÇAO PREVENTIVA 250", "13750", 34.3, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "TRA0085", 1464.0, "29/11/2025", "MANUTENÇAO PREVENTIVA 300", "1500", 36, "HOR", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "TRA0080", 3568.7, "28/11/2025", "MANUTENÇAO PREVENTIVA 400", "3600", 31.3, "HOR", "PONTAL", "Morada Nova"),
    ("VERMELHO", "FEL1001", 23555.5, "28/11/2025", "MANUTENÇAO PREVENTIVA 500", "23500", -55.5, "HOR", "OFICINA POMPEU", "Pompéu"),
    ("VERDE", "GRU1024", 1421.5, "02/12/2025", "MANUTENÇAO PREVENTIVA 500", "1500", 78.5, "HOR", "GRAVATA", "Felixlândia"),
    ("AMARELO", "GRU1025", 1501.6, "02/12/2025", "MANUTENÇAO PREVENTIVA 500", "1500", -1.6, "HOR", "SACO FECHADO", "Felixlândia"),
    ("VERDE", "PAC9123", 13437.6, "28/11/2025", "MANUTENÇAO PREVENTIVA 500", "13500", 62.4, "HOR", "OFICINA PONTAL", "Morada Nova"),
    ("VERDE", "PAC9138", 7421.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "7500", 79, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "PAC9145", 1414.2, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "1500", 85.8, "HOR", "RETIRO", "Pompéu"),
    ("VERDE", "SKD1026", 1446.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "1500", 54, "HOR", "PAULISTA", "Pompéu"),
    ("VERDE", "TRA0011", 9429.0, "14/11/2025", "MANUTENÇAO PREVENTIVA 500", "9500", 71, "HOR", "BARRA", "Pompéu"),
    ("VERDE", "TRA0047", 2483.5, "27/11/2025", "MANUTENÇAO PREVENTIVA 500", "2500", 16.5, "HOR", "OLHOS DAGUA", "Pompéu"),
    ("VERDE", "TRA0049", 17442.9, "02/12/2025", "MANUTENÇAO PREVENTIVA 500", "17500", 57.1, "HOR", "RETIRO", "Pompéu"),
    ("AMARELO", "TRA0052", 14504.7, "27/11/2025", "MANUTENÇAO PREVENTIVA 500", "14500", -4.7, "HOR", "BURITI GRANDE", "Morada Nova"),
    ("VERDE", "TRA0057", 9479.2, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "9500", 20.8, "HOR", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "TRA0060", 4428.0, "26/11/2025", "MANUTENÇAO PREVENTIVA 500", "4500", 72, "HOR", "PAI LOURENCO", "Morada Nova"),
    ("VERDE", "TRA0064", 1400.3, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "1500", 99.7, "HOR", "LORENA", "Felixlândia"),
    ("VERDE", "TRA0071", 7446.8, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "7500", 53.2, "HOR", "LORENA", "Felixlândia"),
    ("VERDE", "UNI0063", 7434.1, "01/12/2025", "MANUTENÇAO PREVENTIVA 500", "7500", 65.9, "HOR", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "TRA0078", 2920.9, "21/11/2025", "MANUTENÇAO PREVENTIVA 900", "3000", 79.1, "HOR", "PONTAL", "Morada Nova"),
    ("VERDE", "FEL1001", 23555.5, "28/11/2025", "MANUTENÇÃO PREVENTIVA AFEX TRIMESTRAL", "19/12/2025", 17, "HOR", "OFICINA POMPEU", "Pompéu"),
    ("VERDE", "FEL1016", 18526.8, "28/11/2025", "MANUTENÇÃO PREVENTIVA AFEX TRIMESTRAL", "19/12/2025", 17, "HOR", "CARAIBAS", "Felixlândia"),
    ("VERDE", "FEL1018", 11273.1, "28/11/2025", "MANUTENÇÃO PREVENTIVA AFEX TRIMESTRAL", "19/12/2025", 17, "HOR", "MARMELADA", "Pompéu"),
    ("VERDE", "FEL1028", 735.8, "01/12/2025", "MANUTENÇÃO PREVENTIVA AFEX TRIMESTRAL", "21/12/2025", 19, "HOR", "MARMELADA", "Pompéu"),
    ("VERMELHO", "CMK4305", 504625.0, "27/11/2025", "MANUTENÇAO PREVENTIVA 10000", "15/02/2026", 75, "KM", "ESCRITORIO POMPEU", "Pompéu"),
    ("VERDE", "CMK4306", 238868.0, "02/12/2025", "MANUTENÇAO PREVENTIVA 10000", "239770", 902, "KM", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "CPP4411", 72410.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 10000", "73300", 890, "KM", "GRAVATA", "Felixlândia"),
    ("VERDE", "CTC4601", 179274.0, "24/11/2025", "MANUTENÇAO PREVENTIVA 10000", "180000", 726, "KM", "SANTA HELENA", "Morada Nova"),
    ("AMARELO", "CTC4610", 526037.0, "27/11/2025", "MANUTENÇAO PREVENTIVA 10000", "526033", -4, "KM", "ESCRITORIO POMPEU", "Pompéu"),
    ("VERDE", "CTL4701", 280539.3, "01/12/2025", "MANUTENÇAO PREVENTIVA 10000", "281253", 713.7, "KM", "SACO FECHADO", "Felixlândia"),
    ("VERMELHO", "CTQ4003", 310547.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 10000", "0", -310547.0, "KM", "ESCRITORIO POMPEU", "Pompéu"),
    ("VERMELHO", "CTQ4009", 118156.0, "28/11/2025", "MANUTENÇAO PREVENTIVA 10000", "0", -118156.0, "KM", "PONTAL", "Morada Nova"),
    ("VERMELHO", "CTQ4010", 38001.0, "27/11/2025", "MANUTENÇAO PREVENTIVA 10000", "0", -38001.0, "KM", "ESCRITORIO POMPEU", "Pompéu"),
    ("VERMELHO", "CTQ4011", 29481.0, "26/11/2025", "MANUTENÇAO PREVENTIVA 10000", "0", -29481.0, "KM", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "ONB8402", 259985.0, "28/11/2025", "MANUTENÇAO PREVENTIVA 10000", "260713", 728, "KM", "BOM JARDIM", "Morada Nova"),
    ("VERDE", "ONB8809", 29959.0, "28/11/2025", "MANUTENÇAO PREVENTIVA 10000", "30612", 653, "KM", "RIO VELHO", "Pompéu"),
    ("VERDE", "VCL5008", 113414.0, "30/10/2025", "MANUTENÇAO PREVENTIVA 10000", "114318", 904, "KM", "FURADO", "Pompéu"),
    ("VERDE", "VCL5015", 99480.0, "28/11/2025", "MANUTENÇAO PREVENTIVA 10000", "100200", 720, "KM", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "VCL5029", 41031.0, "14/11/2025", "MANUTENÇAO PREVENTIVA 10000", "41037", 6, "KM", "RETIRO DA MARMELADA", "Pompéu"),
    ("VERDE", "VPG5804", 256989.0, "26/11/2025", "MANUTENÇAO PREVENTIVA 10000", "257351", 362, "KM", "ESCRITORIO POMPEU", "Pompéu"),
    ("VERMELHO", "VPG5810", 198901.0, "27/11/2025", "MANUTENÇAO PREVENTIVA 10000", "198177", -724, "KM", "ESCRITORIO POMPEU", "Pompéu"),
    ("VERDE", "VPG5813", 205692.0, "29/11/2025", "MANUTENÇAO PREVENTIVA 10000", "206635", 943, "KM", "SANTA HELENA", "Morada Nova"),
    ("VERMELHO", "VPG5819", 145230.0, "02/12/2025", "MANUTENÇAO PREVENTIVA 10000", "10000", -135230.0, "KM", "BURITY GRANDE", "Pompéu"),
    ("VERDE", "VPL5401", 204920.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 10000", "205070", 150, "KM", "SANTA HELENA", "Morada Nova"),
    ("VERDE", "VPL5402", 179121.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 10000", "179924", 803, "KM", "GRAVATA", "Felixlândia"),
    ("VERMELHO", "CMK4303", 674147.0, "01/12/2025", "MANUTENÇAO PREVENTIVA 5000", "670513", -3634, "KM", "RETIRO", "Pompéu"),
]

HORAS_POR_TIPO = {
    "INSPEÇÃO PREVENTIVA DE MATERIAL RODANTE": 1.0,
    "INSPEÇAO PREVENTIVA DE MATERIAL RODANTE": 1.0,
    "MANUTENÇÃO PREVENTIVA 250": 1.5,
    "MANUTENÇAO PREVENTIVA 250": 1.5,
    "MANUTENÇÃO PREVENTIVA 300": 1.5,
    "MANUTENÇAO PREVENTIVA 300": 1.5,
    "MANUTENÇÃO PREVENTIVA 400": 1.5,
    "MANUTENÇAO PREVENTIVA 400": 1.5,
    "MANUTENÇÃO PREVENTIVA 500": 2.0,
    "MANUTENÇAO PREVENTIVA 500": 2.0,
    "MANUTENÇÃO PREVENTIVA 900": 2.0,
    "MANUTENÇAO PREVENTIVA 900": 2.0,
    "MANUTENÇÃO PREVENTIVA 1000": 3.0,
    "MANUTENÇAO PREVENTIVA 1000": 3.0,
    "MANUTENÇÃO PREVENTIVA 1200": 2.5,
    "MANUTENÇAO PREVENTIVA 1200": 2.5,
    "MANUTENÇÃO PREVENTIVA 2000": 3.0,
    "MANUTENÇAO PREVENTIVA 2000": 3.0,
    "MANUTENÇÃO PREVENTIVA 5000": 2.0,
    "MANUTENÇAO PREVENTIVA 5000": 2.0,
    "MANUTENÇÃO PREVENTIVA 10000": 2.0,
    "MANUTENÇAO PREVENTIVA 10000": 2.0,
    "MANUTENÇÃO PREVENTIVA AFEX TRIMESTRAL": 2.5,
}


def get_abbr(name: str) -> str:
    """Gera abreviação de 2 letras para o nome da fazenda"""
    clean_name = name.replace('FAZENDA ', '').replace('ESCRITORIO ', '').replace('OFICINA ', '')
    words = clean_name.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return clean_name[:2].upper()


def get_hours_for_maintenance(alerta: str) -> float:
    """Retorna as horas estimadas para um tipo de manutenção"""
    for tipo, horas in HORAS_POR_TIPO.items():
        if tipo in alerta.upper():
            return horas
    return 1.5


def generate_farms() -> List[Farm]:
    """Gera lista de fazendas com seus equipamentos a partir dos dados"""
    farms_dict = {}
    farm_id = 1
    equip_id = 1

    for fazenda_nome, coords in FAZENDAS_COORDENADAS.items():
        lat, lng, regional = coords
        if fazenda_nome not in farms_dict:
            farms_dict[fazenda_nome] = Farm(
                id=farm_id,
                name=f"FAZENDA {fazenda_nome}",
                abbr=get_abbr(fazenda_nome),
                lat=lat,
                lng=lng,
                regional=regional,
                equipment=[]
            )
            farm_id += 1

    for row in DADOS_PLANILHA:
        status, patrimonio, horimetro, data_lancamento, alerta, a_fazer, faltando, tipo, fazenda, regional = row

        if not fazenda or fazenda == 'nan' or str(fazenda) == 'nan':
            continue

        if fazenda not in FAZENDAS_COORDENADAS:
            continue

        horas = get_hours_for_maintenance(alerta)
        atividade = get_atividade_from_patrimonio(patrimonio)

        eq = Equipment(
            id=equip_id,
            patrimonio=patrimonio,
            name=alerta,
            status=status,
            hours=horas,
            horimetro=horimetro,
            data_lancamento=str(data_lancamento),
            a_fazer=str(a_fazer),
            faltando=faltando,
            farm_id=farms_dict[fazenda].id,
            farm_name=farms_dict[fazenda].name,
            regional=farms_dict[fazenda].regional,
            abbr=farms_dict[fazenda].abbr,
            atividade=atividade,
            tipo=tipo
        )
        farms_dict[fazenda].equipment.append(eq)
        equip_id += 1

    return list(farms_dict.values())


ALL_FARMS = generate_farms()


def get_all_equipment() -> List[Equipment]:
    """Retorna todos os equipamentos de todas as fazendas"""
    equipment = []
    for farm in ALL_FARMS:
        for eq in farm.equipment:
            eq.farm_id = farm.id
            eq.farm_name = farm.name
            eq.regional = farm.regional
            eq.abbr = farm.abbr
            equipment.append(eq)
    return equipment


def get_farm_by_id(farm_id: int) -> Optional[Farm]:
    """Busca fazenda por ID"""
    for farm in ALL_FARMS:
        if farm.id == farm_id:
            return farm
    return None


def get_farm_by_name(name: str) -> Optional[Farm]:
    """Busca fazenda por nome"""
    for farm in ALL_FARMS:
        if farm.name == name or farm.name.replace('FAZENDA ', '') == name:
            return farm
    return None


def get_equipment_by_id(equip_id: int) -> Optional[Equipment]:
    """Busca equipamento por ID"""
    for farm in ALL_FARMS:
        for eq in farm.equipment:
            if eq.id == equip_id:
                return eq
    return None