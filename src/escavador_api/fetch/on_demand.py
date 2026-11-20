"""On-demand process update requests."""
from escavador_api.exceptions import (
    EscavadorAPIProblemAPIException, EscavadorAPIInvalidParametersException,
    EscavadorAPIProcessUpdateAlreadyRequestedException)


# Local imports
from escavador_api.fetch.base import FetchBaseMixin
from escavador_api.utils.process import validate_process_number


class FetchOnDemandMixin(FetchBaseMixin):
    """Mixin to handle on-demand requests."""

    def request_process_update_public(self, process_number: str) -> dict:
        """Request update to public process information using CNJ number.

        This is a paid request.

        This method requests Escavador to search for new information on the
        process and update it, along with public documents found.

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
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/solicitar-atualizacao"\
            .format(process_number=process_number)

        # Build data payload
        data = {"documentos_publicos": 1}
        try:
            return self.post(json=data, url=url)
        except EscavadorAPIInvalidParametersException as e:
            request_error_code = e.payload.get('request_error_code', -1)
            body_code = e.payload.get('code') or e.payload.get('error')
            is_already_updated = (
                (body_code == 'UNPROCESSABLE_ENTITY') and
                (request_error_code == 422))
            if is_already_updated:
                raise EscavadorAPIProcessUpdateAlreadyRequestedException(
                    message="Process already being monitored.",
                    payload=e.payload)
            raise

    def request_process_update_full(self, process_number: str,
                                    auth_username: str | None = None,
                                    auth_password: str | None = None,
                                    certificate_id: int | None = None,
                                    use_certificate: bool = False) -> dict:
        """Request update to complete process information using CNJ number.

        This is a paid request.

        This method requests Escavador to search for new information on the
        process and update it, along with any public or restricted documents
        found using the credentials provided.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            auth_username (str, optional):
                Username for user authentication.
                Required if use_certificate is not provided.
            auth_password (str, optional):
                Password for user authentication.
                Required if use_certificate is not provided
            certificate_id (int, optional):
                Use specific certificate ID. If not provided, a random
                certificate will be selected.
            use_certificate (bool, optional):
                Use registered certificate for authentication.
                Required if auth_username and auth_password are not provided.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request status.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIProblemAPIException:
                If authentication arguments are inconsistent.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        url = (
            "v2/processos/numero_cnj/{process_number}/solicitar-atualizacao"
            .format(process_number=process_number))

        # Validate authentication
        has_user_auth = (
            auth_username is not None and
            auth_password is not None)

        if not (has_user_auth or use_certificate):
            raise EscavadorAPIProblemAPIException(
                message="Authentication required for restricted documents.")

        if has_user_auth and use_certificate:
            raise EscavadorAPIProblemAPIException(
                message=("Use username/password OR " +
                         "certificate authentication, not both."))

        if certificate_id is not None and not use_certificate:
            raise EscavadorAPIProblemAPIException(
                message=("'certificate_id' provided but " +
                         "'use_certificate' is set to False."))

        # Build payload
        data = {"autos": 1}
        if has_user_auth is True:
            data["usuario"] = auth_username
            data["senha"] = auth_password
        if use_certificate is True:
            data["utilizar_certificado"] = True
        if certificate_id is not None:
            data["certificado_id"] = certificate_id

        try:
            return self.post(json=data, url=url)
        except EscavadorAPIInvalidParametersException as e:
            request_error_code = e.payload.get('request_error_code', -1)
            body_code = e.payload.get('code') or e.payload.get('error')
            is_already_updated = (
                (body_code == 'UNPROCESSABLE_ENTITY') and
                (request_error_code == 422))
            if is_already_updated:
                raise EscavadorAPIProcessUpdateAlreadyRequestedException(
                    message="Process already being monitored.",
                    payload=e.payload)
            raise

    def get_process_update_status(self, process_number: str) -> dict:
        """Retrieve search request status.

        This is a paid request.

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
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY`` when the body
                is not remapped to an update already in progress.
            EscavadorAPIProcessUpdateAlreadyRequestedException:
                HTTP 422 with ``code`` or ``error``
                ``UNPROCESSABLE_ENTITY`` when an update is already
                running for this process.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        url = "v2/processos/numero_cnj/{process_number}/status-atualizacao"\
            .format(process_number=process_number)
        return self.get(url=url)
