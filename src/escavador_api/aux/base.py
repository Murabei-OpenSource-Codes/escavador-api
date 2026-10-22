"""Base module for auxiliary classes."""
import requests
from loguru import logger
from urllib.parse import urljoin
from escavador_api.aux.misc import retry_on_network_errors
from escavador_api.exceptions import (
    EscavadorAPIInvalidDocumentException, EscavadorAPIProblemAPIException,
    EscavadorAPIUnmappedErrorException, EscavadorAPIAuthenticationError)
from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_fixed,)
from typing import Literal, TypedDict, Any

# Local imports
from escavador_api.config import REQUEST_TIMEOUT, PROXY_URL


class BaseMixin:
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

    @retry_on_network_errors
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
        """
        url_with_base = urljoin(self.BASE_URL, url)
        try:
            response = self.session.get(
                url=url_with_base, params=params,
                timeout=REQUEST_TIMEOUT)
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

    @retry_on_network_errors
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
        """
        url_with_base = urljoin(self.BASE_URL, url)
        try:
            response = self.session.get(
                url=url_with_base, params=params,
                timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.content

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

    @retry_on_network_errors
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
        """
        url_with_base = urljoin(self.BASE_URL, url)
        try:
            response = self.session.post(
                url=url_with_base, params=params,
                data=data, json=json, timeout=REQUEST_TIMEOUT)
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

    def fetch_paginated(self, url: str, params: dict | None = None):
        """Fetch data from the API.

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
        while url is not None:
            data = self.get(url=url, params=params)
            for item in data.get("items", []):
                yield item

            # The paginantion of the query does not need the parameters
            # they are send at the first request
            params = None
            url = data.get("links", {}).get("next")
            if url is not None:
                logger.debug(
                    "- Paginating results url[{url}]",
                    url=url)
