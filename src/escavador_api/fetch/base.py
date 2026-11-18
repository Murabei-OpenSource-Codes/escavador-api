"""Base module for auxiliary classes."""
import requests
from loguru import logger
from urllib.parse import urljoin
from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_fixed)
from escavador_api.exceptions import (
    EscavadorAPIProblemAPIException, EscavadorAPIUnmappedErrorException,
    EscavadorAPIAuthenticationError)
from typing import Any, Iterator

# Local imports
from escavador_api.config import MAX_PAGES, PROXY_URL, REQUEST_TIMEOUT


RETRY_ERRORS = (requests.ConnectionError, requests.Timeout)
"""Tuple of errors to retry on."""


# Five attempts, three seconds apart, on connection errors and timeouts.
_RETRY_ON_NETWORK = retry(
    retry=retry_if_exception_type(RETRY_ERRORS),
    stop=stop_after_attempt(5),
    wait=wait_fixed(3),
    reraise=True)


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
    def _response_api_message(response: requests.Response) -> str:
        """Read an error message from an HTTP error response body.

        Binary and empty bodies skip JSON parsing.
        """
        try:
            body = response.json()
            if isinstance(body, dict):
                message = body.get("message")
                if message:
                    return str(message)
        except ValueError:
            pass
        text = (response.text or "").strip()
        if text:
            return text[:500]
        return "HTTP {status_code}".format(
            status_code=response.status_code)

    @_RETRY_ON_NETWORK
    def get(self, url: str, params: dict | None = None) -> Any:
        """Aux fuction to allow retry on get requests.

        Args:
            url (str):
                URL to get data from.
            params (dict, optional):
                Query parameters for the request.

        Returns:
            dict:
                Data returned by the API.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
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
                    payload={"error": str(e)})

        except requests.HTTPError as e:
            msg = self._response_api_message(response)
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={
                    "status_code": response.status_code,
                    "error": str(e)})
        except RETRY_ERRORS:
            raise
        except EscavadorAPIProblemAPIException:
            raise
        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
        try:
            response = self.session.get(
                url=url_with_base, params=params,
                timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.content

        except requests.HTTPError as e:
            msg = self._response_api_message(response)
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={
                    "status_code": response.status_code,
                    "error": str(e)})
        except RETRY_ERRORS:
            raise
        except EscavadorAPIProblemAPIException:
            raise
        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
            requests.ConnectionError:
                If the connection still fails after 5 attempts.
            requests.Timeout:
                If the request still times out after 5 attempts.
        """
        url_with_base = urljoin(self.BASE_URL, url)
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
                    payload={"error": str(e)})

        except requests.HTTPError as e:
            msg = self._response_api_message(response)
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={
                    "status_code": response.status_code,
                    "error": str(e)})
        except RETRY_ERRORS:
            raise
        except EscavadorAPIProblemAPIException:
            raise
        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    @_RETRY_ON_NETWORK
    def delete(self, url: str) -> Any:
        """Send a DELETE request.

        Args:
            url (str):
                URL to delete data from.

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
        url_with_base = urljoin(self.BASE_URL, url)
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
                        payload={"error": str(e)})

        except requests.HTTPError as e:
            msg = self._response_api_message(response)
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={
                    "status_code": response.status_code,
                    "error": str(e)})
        except RETRY_ERRORS:
            raise
        except EscavadorAPIProblemAPIException:
            raise
        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

    @_RETRY_ON_NETWORK
    def patch(self, url: str, data: Any) -> Any:
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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url_with_base = urljoin(self.BASE_URL, url)
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
                        payload={"error": str(e)})

        except requests.HTTPError as e:
            msg = self._response_api_message(response)
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={
                    "status_code": response.status_code,
                    "error": str(e)})
        except RETRY_ERRORS:
            raise
        except EscavadorAPIProblemAPIException:
            raise
        except Exception as e:
            msg = "Unmapped error"
            raise EscavadorAPIUnmappedErrorException(
                message=msg,
                payload={"error": str(e)})

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
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        pages_fetched = 0
        while url is not None:
            data = self.get(url=url, params=params)
            for item in data.get("items", []):
                yield item

            # The paginantion of the query does not need the parameters
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
