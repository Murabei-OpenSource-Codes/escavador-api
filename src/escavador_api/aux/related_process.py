"""Module to handle related processes for persons and companies."""
from typing import Literal, Any

# Local imports
from escavador_api.exceptions import EscavadorAPIInvalidParametersException
from escavador_api.aux.base import BaseMixin


class RelatedProcessMixin(BaseMixin):
    """Class to handle related processes for persons and companies."""

    def get_related_processes(self,
                              cpf_cnpj: str = None,
                              nome: str = None,
                              ordena_por: str = "data_inicio",
                              ordem: str = "desc",
                              limit: Literal[20, 50, 100] = 100,
                              tribunais: list[str] = None,
                              incluir_homonimos: bool = None,
                              incluir_mesma_raiz_cnpj: bool = None,
                              polo: Literal["ATIVO", "PASSIVO", "ADVOGADO", "OUTROS"] = None, # NOQA
                              status: Literal["ATIVO", "INATIVO"] = None,
                              data_minima: str = None,
                              data_maxima: str = None,
                              assuntos_codigos_cnj: list[int] = None,
                              classes_codigos_cnj: list[int] = None,
                              materias_codigos_cnj: list[int] = None,
                              valor_causa_minimo: float = None,
                              valor_causa_maximo: float = None,
                              envolvidos_relacionados: list[str] = None) -> Any: # NOQA
        """Get the related processes for the person and company."""
        url = "v2/envolvido/processos"

        if cpf_cnpj is None and nome is None:
            msg = "Either cpf_cnpj or nome must be provided"
            raise EscavadorAPIInvalidParametersException(message=msg)

        params = {}
        if cpf_cnpj is not None:
            params["cpf_cnpj"] = cpf_cnpj
        if nome is not None:
            params["nome"] = nome
        if ordena_por is not None:
            params["ordena_por"] = ordena_por
        if ordem is not None:
            params["ordem"] = ordem
        if limit is not None:
            params["limit"] = limit
        if tribunais is not None:
            params["tribunais"] = tribunais
        if incluir_homonimos is not None:
            params["incluir_homonimos"] = incluir_homonimos
        if incluir_mesma_raiz_cnpj is not None:
            params["incluir_mesma_raiz_cnpj"] = incluir_mesma_raiz_cnpj
        if polo is not None:
            params["polo"] = polo
        if status is not None:
            params["status"] = status
        if data_minima is not None:
            params["data_minima"] = data_minima
        if data_maxima is not None:
            params["data_maxima"] = data_maxima
        if assuntos_codigos_cnj is not None:
            params["assuntos_codigos_cnj"] = assuntos_codigos_cnj
        if classes_codigos_cnj is not None:
            params["classes_codigos_cnj"] = classes_codigos_cnj
        if materias_codigos_cnj is not None:
            params["materias_codigos_cnj"] = materias_codigos_cnj
        if valor_causa_minimo is not None:
            params["valor_causa_minimo"] = valor_causa_minimo
        if valor_causa_maximo is not None:
            params["valor_causa_maximo"] = valor_causa_maximo
        if envolvidos_relacionados is not None:
            params["envolvidos_relacionados"] = envolvidos_relacionados
        return list(self.fetch_paginated(url=url, params=params))