"""Module to handle related processes for persons and companies."""
from typing import Literal

# Local imports
from escavador_api.exceptions import EscavadorAPIInvalidParametersException
from escavador_api.aux.base import BaseMixin


class RelatedProcessMixin(BaseMixin):
    """Class to handle related processes for persons and companies."""

    def get_related_processes(self,
                              cpf_cnpj: str | None = None,
                              nome: str | None = None,
                              ordena_por: str = "data_inicio",
                              ordem: str = "desc",
                              limit: Literal[20, 50, 100] = 100,
                              tribunais: list[str] | None = None,
                              incluir_homonimos: bool | None = None,
                              incluir_mesma_raiz_cnpj: bool | None = None,
                              polo: Literal["ATIVO", "PASSIVO", "ADVOGADO", "OUTROS"] | None = None, # NOQA
                              status: Literal[
                                  "ATIVO", "INATIVO"] | None = None,
                              data_minima: str | None = None,
                              data_maxima: str | None = None,
                              assuntos_codigos_cnj: list[int] | None = None,
                              classes_codigos_cnj: list[int] | None = None,
                              materias_codigos_cnj: list[int] | None = None,
                              valor_causa_minimo: float | None = None,
                              valor_causa_maximo: float | None = None,
                              envolvidos_relacionados: list[str] | None = None, # NOQA
                              ) -> list[dict]:
        """List processes related to a person or a company.

        Either ``cpf_cnpj`` or ``nome`` is required. Paginated API
        items are collected into one list.

        Args:
            cpf_cnpj (str, optional):
                CPF or CNPJ used to search related processes.
            nome (str, optional):
                Name used to search related processes.
            ordena_por (str):
                Field used to sort results. Defaults to ``data_inicio``.
            ordem (str):
                Sort direction. Defaults to ``desc``.
            limit (Literal[20, 50, 100]):
                Page size sent to the API. Defaults to 100.
            tribunais (list[str], optional):
                Court codes to filter the search.
            incluir_homonimos (bool, optional):
                Include namesakes when searching by name.
            incluir_mesma_raiz_cnpj (bool, optional):
                Include companies that share the same CNPJ root.
            polo (Literal["ATIVO", "PASSIVO", "ADVOGADO", "OUTROS"], optional):
                Party role used as a filter.
            status (Literal["ATIVO", "INATIVO"], optional):
                Process status used as a filter.
            data_minima (str, optional):
                Earliest process start date accepted by the API.
            data_maxima (str, optional):
                Latest process start date accepted by the API.
            assuntos_codigos_cnj (list[int], optional):
                CNJ subject codes used as a filter.
            classes_codigos_cnj (list[int], optional):
                CNJ class codes used as a filter.
            materias_codigos_cnj (list[int], optional):
                CNJ matter codes used as a filter.
            valor_causa_minimo (float, optional):
                Minimum claim value.
            valor_causa_maximo (float, optional):
                Maximum claim value.
            envolvidos_relacionados (list[str], optional):
                Related parties used as a filter.

        Returns:
            list[dict]:
                Process records returned by the Escavador API.

        Raises:
            EscavadorAPIInvalidParametersException:
                If both cpf_cnpj and nome are missing.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
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