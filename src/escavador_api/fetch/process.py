"""Module to handle processes requests."""
from typing import Any, Iterator, Literal, TypedDict
from escavador_api.exceptions import EscavadorAPIProblemAPIException


# Local imports
from escavador_api.fetch.base import FetchBaseMixin
from escavador_api.utils.process import validate_process_number


class KeywordDict(TypedDict):
    """Special type for parameter in `create_monitoring_new_process`.

    Used as parameter typing for `create_monitoring_new_process`.
    """
    condicao: Literal["CONTEM", "NAO_CONTEM", "CONTEM_ALGUMA"]
    termo: str


class FetchProcessMixin(FetchBaseMixin):
    """Mixin to handle processes requests."""

    def get_courts(self) -> dict:
        """List all available courts for searches in Escavador.

        Returns:
            dict:
                JSON response returned by the Escavador API listing
                the courts available for search.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/tribunais"
        return self.get(url=url)

    def get_process_info(self, process_number: str) -> dict:
        """Retrieve process information from Escavador using CNJ number.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            dict:
                JSON response returned by the Escavador API containing
                information about the process.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}"\
            .format(process_number=process_number)
        return self.get(url=url)


    def request_ai_summary(self, process_number: str) -> dict:
        """Request a summary of available process information using CNJ number.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request details and status.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = (
            "v2/processos/numero_cnj/{process_number}/ia/"
            "resumo/solicitar-atualizacao")\
            .format(process_number=process_number)
        return self.post(url=url)

    def get_ai_summary_status(self, process_number: str) -> dict:
        """Retrieve AI summary generation status.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request status.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        url = "v2/processos/numero_cnj/{process_number}/ia/resumo/status"\
            .format(process_number=process_number)
        return self.get(url=url)

    def get_ai_summary(self, process_number: str) -> dict:
        """Retrieve AI summary.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            dict:
                JSON response returned by the Escavador API with the
                generated AI summary, update date and summary metadata.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        url = "v2/processos/numero_cnj/{process_number}/ia/resumo"\
            .format(process_number=process_number)
        return self.get(url=url)

    def create_monitoring_new_process(self, keyword: str,
                                      keyword_variations: list[str] | None = None, # NOQA
                                      aux_keywords: list[KeywordDict] | None = None,  # NOQA
                                      courts: list[str] | None = None) -> Any:
        """Create monitoring to search for new processes.

        The monitoring will search for the keyword in newly created processes
        and return those which match the main term or informed variations.

        Args:
            keyword (str):
                Keyword to monitor in newly created processes.
            keyword_variations (list, optional):
                List of keyword variations to monitor.
            aux_keywords (list, optional):
                List of terms and conditions to monitor alongside the main
                keyword. Possible conditions are:
                    - `CONTEM`: monitoring will only alert if a process
                    contains all the informed terms.
                    - `NAO_CONTEM`: monitoring will alert only if a process
                    does not contain any of the informed terms.
                    - `CONTEM_ALGUMA`: monitoring will alert if a process
                    contains any of the informed terms.
            courts (list, optional):
                List of courts where new processes should be searched for
                (e.g.: ["TJSP", "TJMG"]).

        Returns:
            dict:
                JSON response returned by the Escavador API with the details
                of the newly created monitoring.

        Raises:
            EscavadorAPIProblemAPIException:
                If keyword_variations has more than two items, if
                aux_keywords is invalid, or if the Escavador API
                returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/novos-processos"

        # Validate json data to be sent
        data = {"termo": keyword}

        if keyword_variations is not None:
            if len(keyword_variations) > 2:
                msg = "keyword_variations must contain at most 2 items"
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={"keyword_variations": keyword_variations})
            data["variacoes"] = keyword_variations

        if aux_keywords is not None:
            for key in aux_keywords:
                if (key['condicao'] not in [
                    'CONTEM', 'NAO_CONTEM', 'CONTEM_ALGUMA']):
                    msg = ("aux_keywords conditions must be " +
                           "CONTEM, NAO_CONTEM or CONTEM_ALGUMA")
                    raise EscavadorAPIProblemAPIException(
                        message=msg, payload=aux_keywords)

                if not isinstance(key['termo'], str):
                    msg = "aux_keywords term must be a string"
                    raise EscavadorAPIProblemAPIException(
                        message=msg, payload=aux_keywords)

            data["termos_auxiliares"] = aux_keywords

        if courts is not None:
            data["tribunais"] = courts

        return self.post(url=url, json=data)

    def list_monitoring_new_process(self) -> Iterator[dict]:
        """Retrieve a list of new process monitorings created.

        Returns:
            Generator:
                Dictionaries representing active monitorings for new
                processes. One item is yielded per API result.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/novos-processos"
        return list(self.fetch_paginated(url=url))

    def get_monitoring_new_process(self, monitoring_id: int) -> dict:
        """Retrieve the details of a monitoring by ID.

        Args:
            monitoring_id (int):
                New process monitoring ID.

        Returns:
            dict:
                JSON response returned by the Escavador API with details of the
                specified monitoring.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/novos-processos/{monitoring_id}"\
            .format(monitoring_id=monitoring_id)
        return self.get(url=url)

    def delete_monitoring_new_process(self, monitoring_id: int
                                      ) -> bool | dict:
        """Delete a monitoring by ID.

        Args:
            monitoring_id (int):
                New process monitoring ID.

        Returns:
            bool | dict:
                True when the API responds with status 204.
                Parsed JSON otherwise.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/novos-processos/{monitoring_id}"\
            .format(monitoring_id=monitoring_id)
        return self.delete(url=url)

    def get_results_monitoring_new_process(self, monitoring_id: int
                                           ) -> Iterator[dict]:
        """Retrieve the results of a new process monitoring.

        Args:
            monitoring_id (int):
                New process monitoring ID.

        Returns:
            Generator:
                Dictionaries representing new processes found by the
                monitoring. One item is yielded per API result.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/novos-processos/{monitoring_id}/resultados"\
            .format(monitoring_id=monitoring_id)
        return list(self.fetch_paginated(url=url))

    def edit_monitoring_new_process(self, monitoring_id: int,
                                    keyword_variations: list[str] | None = None,
                                    aux_keywords: list[KeywordDict] | None = None, # NOQA
                                    courts: list[str] | None = None) -> Any:
        """Edit previously created monitoring. Keyword cannot be edited.

        Args:
            monitoring_id (int):
                New process monitoring ID.
            keyword_variations (list, optional):
                Replaces the list of keyword variations to monitor. To reset
                this filter, pass an empty list `[]`.
            aux_keywords (list, optional):
                Replaces the list of terms and conditions to monitor alongside
                the main keyword. Possible conditions are:
                    - `CONTEM`: monitoring will only alert if a process
                    contains all the informed terms.
                    - `NAO_CONTEM`: monitoring will alert only if a process
                    does not contain any of the informed terms.
                    - `CONTEM_ALGUMA`: monitoring will alert if a process
                    contains any of the informed terms.
                The new auxiliary keywords will substitute the previous list.
                To reset this filter, pass an empty list `[]`.
            courts (list, optional):
                List of courts where new processes should be searched for
                (e.g.: ["TJSP", "TJMG"]). To reset this filter, pass an
                empty list `[]`.

        Returns:
            dict:
                JSON response returned by the Escavador API with the details
                of the updated monitoring.

        Raises:
            EscavadorAPIProblemAPIException:
                If keyword_variations has more than two items, if
                aux_keywords is invalid, or if the Escavador API
                returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/novos-processos/{monitoring_id}"\
            .format(monitoring_id=monitoring_id)

        data = {}
        if keyword_variations is not None:
            if len(keyword_variations) > 2:
                msg = "keyword_variations must contain at most 2 items"
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={"keyword_variations": keyword_variations})
            data["variacoes"] = keyword_variations

        if aux_keywords is not None:
            for key in aux_keywords:
                if (key['condicao'] not in [
                    'CONTEM', 'NAO_CONTEM', 'CONTEM_ALGUMA']):
                    msg = ("aux_keywords conditions must be " +
                           "CONTEM, NAO_CONTEM or CONTEM_ALGUMA")
                    raise EscavadorAPIProblemAPIException(
                        message=msg, payload=aux_keywords)

                if not isinstance(key['termo'], str):
                    msg = "aux_keywords term must be a string"
                    raise EscavadorAPIProblemAPIException(
                        message=msg, payload=aux_keywords)

            data["termos_auxiliares"] = aux_keywords

        if courts is not None:
            data["tribunais"] = courts
        return self.patch(url=url, data=data)

    def create_monitoring_existing_process(self, process_number: str,
                                           court: str | None = None,
                                           frequency: str | None = None) -> Any:
        """Create monitoring to search for new updates on an existing process.

        The monitoring will search and return new publications and updates
        of the informed process.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            court (str, optional):
                Court to be monitored.
            frequency (str, optional):
                Frequency on which the monitoring agent will search for new
                updates. Available frequencies are `DIARIA` (default) and
                `SEMANAL`.

        Returns:
            dict:
                JSON response returned by the Escavador API with the details
                of the newly created monitoring.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        url = "v2/monitoramentos/processos"

        data = {"numero": process_number}
        if court is not None:
            data['tribunal'] = court
        if frequency is not None:
            data['frequencia'] = frequency
        return self.post(url=url, json=data)

    def list_monitoring_existing_process(self) -> Iterator[dict]:
        """Retrieve a list of existing process monitorings created.

        Returns:
            Generator:
                Dictionaries representing active monitorings for
                existing processes. One item is yielded per API result.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/processos"
        return list(self.fetch_paginated(url=url))

    def get_monitoring_existing_process(self, monitoring_id: int) -> dict:
        """Retrieve the details of a monitoring by ID.

        Args:
            monitoring_id (int):
                Existing process monitoring ID.

        Returns:
            dict:
                JSON response returned by the Escavador API with details of
                the specified monitoring.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/processos/{monitoring_id}"\
            .format(monitoring_id=monitoring_id)
        return self.get(url=url)

    def delete_monitoring_existing_process(self, monitoring_id: int
                                          ) -> bool | dict:
        """Delete a monitoring by ID.

        Args:
            monitoring_id (int):
                Existing process monitoring ID.

        Returns:
            bool | dict:
                True when the API responds with status 204.
                Parsed JSON otherwise.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v2/monitoramentos/processos/{monitoring_id}"\
            .format(monitoring_id=monitoring_id)
        return self.delete(url=url)
