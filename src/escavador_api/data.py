"""Escavador API."""
import requests
from escavador_api.exceptions import (
    EscavadorAPIInvalidDocumentException,
    EscavadorAPIProblemAPIException,
    EscavadorAPIUnmappedErrorException,
)


class EscavadorAPI:
    """Python API to interact with Escavador endpoints."""

    BASE_URL = "https://api.escavador.com/api/"

    def __init__(self, escavador_auth_token: str):
        """__init__.

        Args:
            escavador_auth_token (str):
                Authentication token for Escavador API.
        """
        self.escavador_auth_token = escavador_auth_token

        self.headers = {
            "Authorization": "Bearer {}".format(self.escavador_auth_token),
            "X-Requested-With": "XMLHttpRequest"}

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _validate_process_number(self, process_number: str):
        """Check process number validation.

        - Must have exactly 20 digits.
        - First 7 digits must follow a specific sequence.
        - Last 2 digits (verification digits) must be validated based on
        initial sequence.

        Args:
            process_number (str):
                process number to be validated.

        Returns:
            bool: Whether process number is valid.
        """
        digits = [int(digit) for digit in process_number if digit.isdigit()]

        if len(digits) != 20:
            msg = "O número do processo não está no formato CNJ."
            raise EscavadorAPIInvalidDocumentException(message=msg)

        digits = "".join(str(num) for num in digits)

        sequence = digits[:7]
        verification_digits = digits[7:9]
        remaining_digits = digits[9:]

        # Calculate expected verification digits
        number_without_vd = sequence + remaining_digits
        remainder = int(number_without_vd) * 100 % 97
        calculated_vd = 98 - remainder
        calculated_vd_str = f"{calculated_vd:02d}"

        if verification_digits != calculated_vd_str:
            msg = "Número do processo inválido."
            raise EscavadorAPIInvalidDocumentException(message=msg)

        return True

    def get_credit_balance(self):
        """Returns current credit balance.

        Returns:
            dict:
                JSON response returned by the Escavador API with current
                credit balance and monthly limit.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = self.BASE_URL + "v1/quantidade-creditos"

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def get_process_info(self, process_number: str):
        """Retrieve process information from Escavador using CNJ number.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.

        Returns:
            dict:
                JSON response returned by the Escavador API containing
                information about the process.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}"
               .format(process_number=process_number))

        try:
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def get_process_movements(self, process_number: str, limit: int = 50):
        """Retrieve process movements from Escavador using CNJ number.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.
            limit (int):
                Limit items per page. Parameter is passed through requests.
                Default is 50.

        Returns:
            dict:
                JSON response returned by the Escavador API.
                The response contains the following keys:

                - `items`: List of dictionaries representing public documents
                associated with the process.
                - `links`: Pagination links, including the URL for the
                next page.
                - `paginator`: Metadata describing pagination information
                such as page number and total items.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/movimentacoes"
               .format(process_number=process_number))

        # TODO: validate how pagination is done.
        # response has 'links' key with a url for the next page.
        # new requests to this next url should not be charged.

        try:
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.get(
                url=url, params={"limit": limit}, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def get_process_public_documents(
        self, process_number: str, limit: int = 50):
        """Retrieve available public documents associated with a CNJ number.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.
            limit (int):
                Limit items per page. Parameter is passed through requests.
                Default is 50.

        Returns:
            dict:
                JSON response returned by the Escavador API.
                The response contains the following keys:

                - `items`: List of dictionaries representing public documents
                associated with the process.
                - `links`: Pagination links, including the URL for the
                next page.
                - `paginator`: Metadata describing pagination information
                such as page number and total items.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/" +
               "{process_number}/documentos-publicos"
               .format(process_number=process_number))

        # TODO: validate how pagination is done.
        # response has 'links' key with a url for the next page.
        # new requests to this next url should not be charged.

        try:
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.get(
                url=url, params={"limit": limit}, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def get_process_all_documents(self, process_number: str, limit: int = 50):
        """Retrieve all available documents associated with a CNJ number.

        This method includes public and restricted documents (when available
        to the authenticated user).

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.
            limit (int):
                Limit items per page. Parameter is passed through requests.
                Default is 50.

        Returns:
            dict:
                JSON response returned by the Escavador API.
                The response contains the following keys:

                - `items`: List of dictionaries representing public documents
                associated with the process.
                - `links`: Pagination links, including the URL for the
                next page.
                - `paginator`: Metadata describing pagination information
                such as page number and total items.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/autos"
               .format(process_number=process_number))

        # TODO: validate how pagination is done. currently page has 50 items.
        # response has 'links' key with a url for the next page.
        # new requests to this next url should not be charged.

        try:
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.get(
                url=url, params={"limit": limit}, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def request_process_update_public(self, process_number: str):
        """Request update to public process information using CNJ number.

        This method requests Escavador to search for new information on the
        process and update it, along with public documents found.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request status.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/" +
               "{process_number}/solicitar-atualizacao"
               .format(process_number=process_number))

        # Build data payload
        data = {
            "documentos_publicos": 1}

        try:
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.post(
                data=data, url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def request_process_update_full(
        self,
        process_number: str,
        auth_username: str = None,
        auth_password: str = None,
        certificate_id: int = None,
        use_certificate: bool = False):
        """Request update to complete process information using CNJ number.

        This method requests Escavador to search for new information on the
        process and update it, along with any public or restricted documents
        found using the credentials provided.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.
            auth_username (str):
                Username for user authentication.
                Required if use_certificate is not provided.
            auth_password (str):
                Password for user authentication.
                Required if use_certificate is not provided
            use_certificate (bool):
                Use registered certificate for authentication.
                Required if auth_username and auth_password is not provided.
            certificate_id (int):
                Use specific certificate ID. If not provided, a random
                certificate will be selected.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request status.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/" +
               "{process_number}/solicitar-atualizacao"
               .format(process_number=process_number))

        # Validate authentication
        has_user_auth = (auth_username is not None and
                         auth_password is not None)

        if not (has_user_auth or use_certificate):
            raise EscavadorAPIProblemAPIException(
                message="Authentication required for restricted documents."
            )

        if has_user_auth and use_certificate:
            raise EscavadorAPIProblemAPIException(
                message=("Use username/password OR " +
                         "certificate authentication, not both.")
            )

        if certificate_id is not None and not use_certificate:
            raise EscavadorAPIProblemAPIException(
                message=("'certificate_id' provided but " +
                         "'use_certificate' is set to False.")
            )

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
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.post(
                data=data, url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    def get_process_update_status(self, process_number: str):
        """Retrieve search request status.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits), with or
                without punctuation.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request status.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.

            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.

            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/status-atualizacao"
               .format(process_number=process_number))

        try:
            # Checks if process number is valid before sending request
            self._validate_process_number(process_number)

            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except EscavadorAPIInvalidDocumentException:
            raise

        except requests.HTTPError as e:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"error": str(e)})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})
