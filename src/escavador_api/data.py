"""Escavador API."""
import re
import requests
from escavador_api.exceptions import (
    EscavadorAPIInvalidDocumentException,
    EscavadorAPIProblemAPIException,
    EscavadorAPIUnmappedErrorException,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)
from typing import Literal, TypedDict


def _retry_on_network_errors(func):
    """Decorator to retry on network errors (ConnectionError, Timeout)."""
    return retry(
        retry=retry_if_exception_type(
            (requests.ConnectionError, requests.Timeout)),
        stop=stop_after_attempt(5),
        wait=wait_fixed(3),
        reraise=True)(func)


# Special type for aux_keyword parameter
class KeywordDict(TypedDict):
    """Special type for parameter in `create_monitoring_new_process`."""
    condicao: Literal["CONTEM", "NAO_CONTEM", "CONTEM_ALGUMA"]
    termo: str


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
        """Validate process number.

        - Must have exactly 20 digits.
        - First 7 digits must follow a specific sequence.
        - Last 2 digits (verification digits) must be validated based on
        initial sequence.

        Args:
            process_number (str):
                process number to be validated.

        Returns:
            bool: Whether process number is valid.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If the provided process number is not a valid CNJ number.
        """
        # Checks if process_number is a string or int
        if not isinstance(process_number, (str, int)):
            msg = "Process number must be a string or an integer"
            raise EscavadorAPIInvalidDocumentException(
                message=msg,
                payload={"process_number": process_number})

        process_number = str(process_number)
        digits = [int(digit) for digit in process_number if digit.isdigit()]

        if len(digits) != 20:
            msg = "Process number is not in a valid CNJ format"
            raise EscavadorAPIInvalidDocumentException(
                message=msg,
                payload={"process_number": process_number})

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
            msg = "Invalid process number"
            raise EscavadorAPIInvalidDocumentException(
                message=msg,
                payload={"process_number": process_number})

        return True

    @_retry_on_network_errors
    def _paginate(self, url: str, params: dict | None = None):
        """Helper function to iterate through paginated responses.

        Args:
            url (str):
                Initial request URL.
            params (dict, optional):
                Query parameters for the first request.

        Yields:
            dict:
                Individual items returned by the API.
        """
        while url is not None:
            response = self.session.get(
                url=url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                yield item

            params = None
            url = data.get("links", {}).get("next")

    @_retry_on_network_errors
    def get_credit_balance(self):
        """Returns current credit balance.

        Returns:
            dict:
                JSON response returned by the Escavador API with current
                credit balance and monthly limit.

        Raises:
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

    @_retry_on_network_errors
    def get_courts(self):
        """List all available courts for searches in Escavador.

        Returns:
            dict:
                JSON response returned by the Escavador API with current
                credit balance and monthly limit.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = self.BASE_URL + "v2/tribunais"

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

    @_retry_on_network_errors
    def get_process_info(self, process_number: str):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}"
               .format(process_number=process_number))

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def get_process_updates(self, process_number: str):
        """Retrieve process updates from Escavador using CNJ number.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            list:
                List of dictionaries representing updates associated with
                the process.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/movimentacoes"
               .format(process_number=process_number))

        try:
            return list(self._paginate(url))

        except requests.HTTPError as e:
            msg = e.response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def get_process_public_documents(self, process_number: str):
        """Retrieve available public documents associated with a CNJ number.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            list:
                List of dictionaries representing public documents
                associated with the process.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        self._validate_process_number(process_number)
        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/documentos-publicos"
               .format(process_number=process_number))

        try:
            return list(self._paginate(url))

        except requests.HTTPError as e:
            msg = e.response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def get_process_all_documents(self, process_number: str):
        """Retrieve all available documents associated with a CNJ number.

        This is a paid request.

        This method includes public and restricted documents (when available
        to the authenticated user).

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            list:
                List of dictionaries representing all documents
                associated with the process.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/autos"
               .format(process_number=process_number))

        try:
            return list(self._paginate(url))

        except requests.HTTPError as e:
            msg = e.response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def request_process_update_public(self, process_number: str):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/" +
               "{process_number}/solicitar-atualizacao"
               .format(process_number=process_number))

        # Build data payload
        data = {"documentos_publicos": 1}

        try:
            response = self.session.post(
                data=data, url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number,
                         "data": data})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number,
                         "data": data})

    @_retry_on_network_errors
    def request_process_update_full(
        self,
        process_number: str,
        auth_username: str | None = None,
        auth_password: str | None = None,
        certificate_id: int | None = None,
        use_certificate: bool = False):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/" +
               "{process_number}/solicitar-atualizacao"
               .format(process_number=process_number))

        # Validate authentication
        has_user_auth = (auth_username is not None and
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
            response = self.session.post(
                data=data, url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number,
                         "data": data})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number,
                         "data": data})

    @_retry_on_network_errors
    def get_process_update_status(self, process_number: str):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/status-atualizacao"
               .format(process_number=process_number))

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def download_process_file(self, process_number: str, file_key: str):
        """Download PDF file of process documents.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            file_key (str):
                Key used to download the document from Escavador database.

        Returns:
            bytes:
                Binary content of the PDF document returned by the
                Escavador API.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        # Clean special characters from CNJ number and
        # ensure correct punctuation (required for downloads)
        # Format: NNNNNNN-DD.AAAA.J.TR.OOOO
        process_number = re.sub(r'\D', '', process_number)
        formatted_process_number = (
            f"{process_number[0:7]}-"
            f"{process_number[7:9]}."
            f"{process_number[9:13]}."
            f"{process_number[13]}."
            f"{process_number[14:16]}."
            f"{process_number[16:20]}")

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/" +
               "{formatted_process_number}/documentos/{file_key}"
               .format(formatted_process_number=formatted_process_number,
                       file_key=file_key))

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            if response.headers.get('Content-Type') == 'application/pdf':
                return response.content

            else:
                msg = "Failed to download document"
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={
                        "formatted_process_number": formatted_process_number,
                        "file_key": file_key})

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def request_ai_summary(self, process_number: str):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/"
               .format(process_number=process_number) +
               "ia/resumo/solicitar-atualizacao")

        try:
            response = self.session.post(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def get_ai_summary_status(self, process_number: str, summary_id: int):
        """Retrieve AI summary generation status.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            summary_id (int):
                Summary ID returned from generation request.

        Returns:
            dict:
                JSON response returned by the Escavador API with
                the search request status.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/" +
               "ia/resumo/status").format(process_number=process_number)

        try:
            response = self.session.get(
                url=url, params={"id": summary_id}, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number,
                         "summary_id": summary_id})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number,
                         "summary_id": summary_id})

    @_retry_on_network_errors
    def get_ai_summary(self, process_number: str):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL +
               "v2/processos/numero_cnj/{process_number}/ia/resumo"
               .format(process_number=process_number))

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"process_number": process_number})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "process_number": process_number})

    @_retry_on_network_errors
    def create_monitoring_new_process(
        self,
        keyword: str,
        keyword_variations: list[str] | None = None,
        aux_keywords: list[KeywordDict] | None = None,
        courts: list[str] | None = None):
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
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL + "v2/monitoramentos/novos-processos")

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

        try:
            response = self.session.post(
                url=url, json=data, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"data": data})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "data": data})

    @_retry_on_network_errors
    def list_monitoring_new_process(self):
        """Retrieve a list of new process monitorings created.

        Returns:
            list:
                List of dictionaries representing active monitorings
                for new processes.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL + "v2/monitoramentos/novos-processos")

        try:
            return list(self._paginate(url))

        except requests.HTTPError as e:
            msg = e.response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg)

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    @_retry_on_network_errors
    def get_monitoring_new_process(self, monitoring_id: int):
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
        url = (self.BASE_URL +
               "v2/monitoramentos/novos-processos/{monitoring_id}"
               .format(monitoring_id=monitoring_id))

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"monitoring_id": monitoring_id})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "monitoring_id": monitoring_id})

    @_retry_on_network_errors
    def delete_monitoring_new_process(self, monitoring_id: int):
        """Delete a monitoring by ID.

        Args:
            monitoring_id (int):
                New process monitoring ID.

        Returns:
            bool:
                True if deletion is successful.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/monitoramentos/novos-processos/{monitoring_id}"
               .format(monitoring_id=monitoring_id))

        try:
            response = self.session.delete(
                url=url, timeout=60)
            response.raise_for_status()

            if response.status_code == 204:
                return True

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"monitoring_id": monitoring_id})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "monitoring_id": monitoring_id})

    @_retry_on_network_errors
    def get_results_monitoring_new_process(self, monitoring_id: int):
        """Retrieve the results of a new process monitoring.

        Args:
            monitoring_id (int):
                New process monitoring ID.

        Returns:
            list:
                List of dictionaries representing new processes
                found by the monitoring.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/monitoramentos/novos-processos/{monitoring_id}/resultados"
               .format(monitoring_id=monitoring_id))

        try:
            return list(self._paginate(url))

        except requests.HTTPError as e:
            msg = e.response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"monitoring_id": monitoring_id})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "monitoring_id": monitoring_id})

    @_retry_on_network_errors
    def edit_monitoring_new_process(
        self,
        monitoring_id: int,
        keyword_variations: list[str] | None = None,
        aux_keywords: list[KeywordDict] | None = None,
        courts: list[str] | None = None):
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
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/monitoramentos/novos-processos/{monitoring_id}"
               .format(monitoring_id=monitoring_id))

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

        try:
            response = self.session.patch(
                url=url, json=data, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"data": data})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "data": data})

    @_retry_on_network_errors
    def create_monitoring_existing_process(
        self,
        process_number: str,
        court: str | None = None,
        frequency: str | None = None):
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        self._validate_process_number(process_number)

        url = (self.BASE_URL + "v2/monitoramentos/processos")

        data = {"numero": process_number}
        if court is not None:
            data['tribunal'] = court
        if frequency is not None:
            data['frequencia'] = frequency

        try:
            response = self.session.post(
                url=url, json=data, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"data": data})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "data": data})

    @_retry_on_network_errors
    def list_monitoring_existing_process(self):
        """Retrieve a list of existing process monitorings created.

        Returns:
            list:
                List of dictionaries representing active monitorings
                for existing processes.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL + "v2/monitoramentos/processos")

        try:
            return list(self._paginate(url))

        except requests.HTTPError as e:
            msg = e.response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg)

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    @_retry_on_network_errors
    def get_monitoring_existing_process(self, monitoring_id: int):
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
        url = (self.BASE_URL +
               "v2/monitoramentos/processos/{monitoring_id}"
               .format(monitoring_id=monitoring_id))

        try:
            response = self.session.get(
                url=url, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"monitoring_id": monitoring_id})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "monitoring_id": monitoring_id})

    @_retry_on_network_errors
    def delete_monitoring_existing_process(self, monitoring_id: int):
        """Delete a monitoring by ID.

        Args:
            monitoring_id (int):
                Existing process monitoring ID.

        Returns:
            bool:
                True if deletion is successful.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = (self.BASE_URL +
               "v2/monitoramentos/processos/{monitoring_id}"
               .format(monitoring_id=monitoring_id))

        try:
            response = self.session.delete(
                url=url, timeout=60)
            response.raise_for_status()

            if response.status_code == 204:
                return True

        except requests.HTTPError:
            msg = response.json().get("message")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={"monitoring_id": monitoring_id})

        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e),
                         "monitoring_id": monitoring_id})
