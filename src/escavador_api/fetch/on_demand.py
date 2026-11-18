"""Module to handle processes requests."""
from typing import Any, Iterator, Literal, TypedDict
from escavador_api.exceptions import EscavadorAPIProblemAPIException


# Local imports
from escavador_api.fetch.base import FetchBaseMixin
from escavador_api.utils.process import validate_process_number


class FetchOnDemandMixin(FetchBaseMixin):
    """Mixin to handle on-demand requests."""

    def request_process_public_documents(self, process_number: str) -> dict:
        """Request a public-document update for a CNJ number.

        This is a paid request. The body is JSON
        ``{"documentos_publicos": 1}``.

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
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/solicitar-atualizacao"\
            .format(process_number=process_number)
        data = {"documentos_publicos": 1}
        return self.post(json=data, url=url)

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
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/solicitar-atualizacao"\
            .format(process_number=process_number)

        # Build data payload
        data = {"documentos_publicos": 1}
        return self.post(data=data, url=url)

    def request_process_update_full(self, process_number: str,
                                    auth_username: str | None = None,
                                    auth_password: str | None = None,
                                    certificate_id: int | None = None,
                                    use_certificate: bool = False) -> Any:
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
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If authentication arguments are inconsistent or the
                Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
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
        return self.post(data=data, url=url)

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
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        url = "v2/processos/numero_cnj/{process_number}/status-atualizacao"\
            .format(process_number=process_number)
        return self.get(url=url)