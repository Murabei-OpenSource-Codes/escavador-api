"""Base module for auxiliary classes."""
import requests
from loguru import logger
from urllib.parse import urljoin
from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_fixed,
    RetryCallState)
from typing import Any, Iterator

# Local imports
from escavador_api.exceptions import (
    EscavadorAPIProblemAPIException, EscavadorAPIAuthenticationError,
    EscavadorAPIErrorTreatment)
from escavador_api.config import MAX_PAGES, PROXY_URL, REQUEST_TIMEOUT


RETRY_ERRORS = (requests.ConnectionError, requests.Timeout)
"""Tuple of errors to retry on."""

_RETRY_ATTEMPTS = 5
"""Max HTTP attempts before giving up on a network error."""


def _log_retry_before_sleep(retry_state: RetryCallState) -> None:
    """Log a network failure before sleeping for the next attempt."""
    outcome = retry_state.outcome
    if outcome is None or not outcome.failed:
        return
    exc = outcome.exception()
    fn_name = retry_state.fn.__name__
    msg = (
        "Escavador API {fn_name} failed ({error_type}): {error}. "
        "Attempt {attempt}/{max_attempts}, retrying in 3s").format(
            fn_name=fn_name,
            error_type=type(exc).__name__,
            error=exc,
            attempt=retry_state.attempt_number,
            max_attempts=_RETRY_ATTEMPTS)
    logger.warning(msg)


# Five attempts, three seconds apart, on connection errors and timeouts.
_RETRY_ON_NETWORK = retry(
    retry=retry_if_exception_type(RETRY_ERRORS),
    stop=stop_after_attempt(_RETRY_ATTEMPTS),
    wait=wait_fixed(3),
    reraise=True,
    before_sleep=_log_retry_before_sleep)


class FetchBaseMixin:
    """Base mixin for auxiliary classes."""

    session: requests.Session
    """The session object for the API."""

    BASE_URL = "https://api.escavador.com/api/"
    """Base URL for the Escavador API."""

    def __init__(self, escavador_auth_token: str):
        """Open an authenticated session for Escavador requests.

        Args:
            escavador_auth_token (str):
                Authentication token for Escavador API.

        Raises:
            EscavadorAPIAuthenticationError:
                If escavador_auth_token is empty.
        """
        if not escavador_auth_token:
            msg = "Authentication token is required"
            raise EscavadorAPIAuthenticationError(message=msg)

        # Add proxy to the escavador calls if necessary and set a default
        # timeout to all calls
        proxies = None
        if PROXY_URL is not None:
            proxies = {"http": PROXY_URL, "https": PROXY_URL}
        self.session = requests.Session()
        if proxies is not None:
            self.session.proxies.update(proxies)

        # Set the authentication token and headers for session
        self.escavador_auth_token = escavador_auth_token
        self.headers = {
            "Authorization": "Bearer {}".format(self.escavador_auth_token),
            "X-Requested-With": "XMLHttpRequest"}
        self.session.headers.update(self.headers)

    @staticmethod
    def _error_treatment(response: requests.Response) -> None:
        """Raise a domain exception for a failed HTTP response.

        The HTTP status is stored as ``request_error_code`` and
        mapped by ``EscavadorAPIErrorTreatment``.

        Args:
            response (requests.Response):
                HTTP response that failed.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        try:
            request_data = response.json()
        except ValueError:
            request_data = None

        if not isinstance(request_data, dict):
            text = (response.text or "").strip()
            request_data = {
                "request_error_code": response.status_code,
                "body": text[:500]}
        else:
            request_data["request_error_code"] = response.status_code
        EscavadorAPIErrorTreatment.raise_by_code(
            request_data=request_data)

    @_RETRY_ON_NETWORK
    def get(self, url: str, params: dict | None = None) -> Any:
        """GET request, retrying network failures.

        Args:
            url (str):
                URL to get data from.
            params (dict, optional):
                Query parameters for the request.

        Returns:
            dict:
                Data returned by the API.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
        response = None
        try:
            response = self.session.get(
                url=url_with_base, params=params,
                timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            try:
                return response.json()
            except ValueError as e:
                raise EscavadorAPIProblemAPIException(
                    message="Response is not valid JSON",
                    payload={
                        "error": str(e),
                        "request_error_code": response.status_code})

        except RETRY_ERRORS:
            raise

        except Exception:
            if response is None:
                raise
            self._error_treatment(response=response)

    @_RETRY_ON_NETWORK
    def get_binary(self, url: str, params: dict | None = None) -> bytes:
        """GET request returning raw response body.

        Args:
            url (str):
                URL path or absolute URL to fetch.
            params (dict, optional):
                Query parameters for the request.

        Returns:
            bytes:
                Raw response content.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
        response = None
        try:
            response = self.session.get(
                url=url_with_base, params=params,
                timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.content

        except RETRY_ERRORS:
            raise

        except Exception:
            if response is None:
                raise
            self._error_treatment(response=response)

    @_RETRY_ON_NETWORK
    def post(self, url: str, params: dict | None = None,
             data: Any | None = None, json: Any | None = None) -> Any:
        """Send a POST request, retrying network failures.

        Args:
            url (str):
                URL path or absolute URL to call.
            params (dict, optional):
                Query parameters for the request.
            data (Any, optional):
                Form body to be sent in the request.
            json (Any, optional):
                JSON body to be sent in the request.

        Returns:
            dict:
                Data returned by the API.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
        response = None
        try:
            response = self.session.post(
                url=url_with_base, params=params,
                data=data, json=json, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as e:
                raise EscavadorAPIProblemAPIException(
                    message="Response is not valid JSON",
                    payload={
                        "error": str(e),
                        "request_error_code": response.status_code})

        except RETRY_ERRORS:
            raise

        except Exception:
            if response is None:
                raise
            self._error_treatment(response=response)

    @_RETRY_ON_NETWORK
    def delete(self, url: str) -> bool | dict:
        """Send a DELETE request.

        Args:
            url (str):
                URL to delete data from.

        Returns:
            bool | dict:
                True when the API responds with status 204.
                Parsed JSON otherwise.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
        response = None
        try:
            response = self.session.delete(
                url=url_with_base, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Status code 204 means successful deletion, but do not return
            # any data
            if response.status_code == 204:
                return True

            # If status 204 is not indicated then return the data
            else:
                try:
                    return response.json()
                except ValueError as e:
                    raise EscavadorAPIProblemAPIException(
                        message="Response is not valid JSON",
                        payload={
                            "error": str(e),
                            "request_error_code": response.status_code})

        except RETRY_ERRORS:
            raise

        except Exception:
            if response is None:
                raise
            self._error_treatment(response=response)

    @_RETRY_ON_NETWORK
    def patch(self, url: str, data: Any) -> bool | dict:
        """Send a PATCH request.

        Args:
            url (str):
                URL path or absolute URL to update.
            data (Any):
                JSON body to be sent in the request.

        Returns:
            bool | dict:
                True when the API responds with status 204.
                Parsed JSON otherwise.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
        response = None
        try:
            response = self.session.patch(
                url=url_with_base, json=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Status code 204 means successful deletion, but do not return
            # any data
            if response.status_code == 204:
                return True

            # If status 204 is not indicated then return the data
            else:
                try:
                    return response.json()
                except ValueError as e:
                    raise EscavadorAPIProblemAPIException(
                        message="Response is not valid JSON",
                        payload={
                            "error": str(e),
                            "request_error_code": response.status_code})

        except RETRY_ERRORS:
            raise

        except Exception:
            if response is None:
                raise
            self._error_treatment(response=response)

    def fetch_paginated(self, url: str, params: dict | None = None
                        ) -> Iterator[dict]:
        """Fetch data from the API.

        The first page is always requested. Further pages stop at
        ``MAX_PAGES`` (``ESCAVADOR_API__MAX_PAGES``). Reaching the cap
        logs a warning and returns the items already fetched.

        Args:
            url (str):
                Initial request URL.
            params (dict, optional):
                Query parameters for the first request.

        Yields:
            dict:
                Individual items returned by the API.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        pages_fetched = 0
        while url is not None:
            data = self.get(url=url, params=params)
            for item in data.get("items", []):
                yield item

            # The pagination of the query does not need the parameters
            # they are send at the first request
            params = None
            next_url = data.get("links", {}).get("next")
            if next_url is None:
                break
            if MAX_PAGES <= pages_fetched:
                reason = "Page cap of {max_pages} was reached.".format(
                    max_pages=MAX_PAGES)
                logger.warning(
                    "Pagination stopped. reason={reason} "
                    "next_url={next_url} pages_fetched={pages_fetched}",
                    reason=reason, next_url=next_url,
                    pages_fetched=pages_fetched)
                break

            pages_fetched = pages_fetched + 1
            logger.debug(
                "- Paginating results url[{url}]",
                url=next_url)
            url = next_url
