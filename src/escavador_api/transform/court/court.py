"""Module to transform the process data."""
import re


class TransformCourtData:
    """Transform the court data."""

    TRIBUNAL_TO_UF = {
        # Tribunais Superiores e Órgãos de Âmbito Nacional (BR)
        "STF": "BR",
        "STJ": "BR",
        "TST": "BR",
        "TSE": "BR",
        "STM": "BR",
        "CNJ": "BR",

        # Tribunais Regionais Federais (TRFs)
        "TRF1": (
            "AC,AM,AP,BA,DF,GO,MA,MT,PA,PI,RO,RR,TO"),
        "TRF2": "ES,RJ",
        "TRF3": "MS,SP",
        "TRF4": "PR,RS,SC",
        "TRF5": "AL,CE,PB,PE,RN,SE",
        "TRF6": "MG",

        # Tribunais de Justiça Estaduais (TJs)
        "TJAC": "AC",
        "TJAL": "AL",
        "TJAM": "AM",
        "TJAP": "AP",
        "TJBA": "BA",
        "TJCE": "CE",
        "TJDFT": "DF",
        "TJES": "ES",
        "TJGO": "GO",
        "TJMA": "MA",
        "TJMG": "MG",
        "TJMS": "MS",
        "TJMT": "MT",
        "TJPA": "PA",
        "TJPB": "PB",
        "TJPE": "PE",
        "TJPI": "PI",
        "TJPR": "PR",
        "TJRJ": "RJ",
        "TJRN": "RN",
        "TJRO": "RO",
        "TJRR": "RR",
        "TJRS": "RS",
        "TJSC": "SC",
        "TJSE": "SE",
        "TJSP": "SP",
        "TJTO": "TO",

        # Tribunais Regionais do Trabalho (TRTs)
        "TRT1": "RJ",
        "TRT2": "SP",  # Capital, Grande SP e Baixada Santista
        "TRT3": "MG",
        "TRT4": "RS",
        "TRT5": "BA",
        "TRT6": "PE",
        "TRT7": "CE",
        "TRT8": "PA,AP",
        "TRT9": "PR",
        "TRT10": "DF,TO",
        "TRT11": "AM,RR",
        "TRT12": "SC",
        "TRT13": "PB",
        "TRT14": "RO,AC",
        "TRT15": "SP",  # Campinas e Interior de SP
        "TRT16": "MA",
        "TRT17": "ES",
        "TRT18": "GO",
        "TRT19": "AL",
        "TRT20": "SE",
        "TRT21": "RN",
        "TRT22": "PI",
        "TRT23": "MT",
        "TRT24": "MS",

        # Tribunais Regionais Eleitorais (TREs)
        "TREAC": "AC",
        "TREAL": "AL",
        "TREAM": "AM",
        "TREAP": "AP",
        "TREBA": "BA",
        "TRECE": "CE",
        "TREDF": "DF",
        "TREES": "ES",
        "TREGO": "GO",
        "TREMA": "MA",
        "TREMG": "MG",
        "TREMS": "MS",
        "TREMT": "MT",
        "TREPA": "PA",
        "TREPB": "PB",
        "TREPE": "PE",
        "TREPI": "PI",
        "TREPR": "PR",
        "TRERJ": "RJ",
        "TRERN": "RN",
        "TRERO": "RO",
        "TRERR": "RR",
        "TRERS": "RS",
        "TRESC": "SC",
        "TRESE": "SE",
        "TRESP": "SP",
        "TRETO": "TO",

        # Tribunais de Justiça Militar Estadual (TJMs)
        "TJMMG": "MG",
        "TJMRS": "RS",
        "TJMSP": "SP",
    }

    def __init__(self, process_data: dict):
        self.process_data = process_data

    @classmethod
    def run(cls, court_data: dict) -> dict:
        """Normalize tribunal fields from one Escavador fonte.

        Args:
            court_data (dict):
                ``tribunal`` object from the API (``id``, ``nome``,
                ``sigla``, ``categoria``).

        Returns:
            dict:
                ``court_id``, ``court_name``, ``court_acronym``
                (alphanumeric, uppercased), ``court_category``, and
                ``court_state``. ``court_state`` is a comma-separated UF
                list from ``TRIBUNAL_TO_UF``, or ``None`` when the acronym
                is unknown.
        """
        court_id = court_data.get('id')
        court_name = court_data.get('nome')
        court_acronym = court_data.get('sigla')
        court_category = court_data.get('categoria')
        tribunal_uf = None
        clear_court_acronym = None
        if court_acronym is not None:
            clear_court_acronym = re.sub(
                r"[^A-Za-z0-9]", "", str(court_acronym)).upper()
            tribunal_uf = cls.TRIBUNAL_TO_UF.get(clear_court_acronym)

        return {
            "court_id": court_id,
            "court_name": court_name,
            "court_acronym": clear_court_acronym or court_acronym,
            "court_category": court_category,
            "court_state": tribunal_uf,
        }