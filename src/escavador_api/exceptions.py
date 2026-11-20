"""Custom exceptions for Escavador API."""
from typing import Any


class EscavadorAPIException(Exception): # NOQA
    """Custom Escavador API Exception."""

    ESCAVADOR_ERROR_CODES: tuple[int | str, ...] = ()
    """HTTP status or Escavador ``code`` values this class handles.

    Match ``request_error_code`` for a status, or the JSON
    ``code`` string. An empty tuple matches nothing.
    """

    def __repr__(self) -> str:
        """Return the debug representation of the exception.

        Returns:
            str:
                Message and error payload.
        """
        template = "{message}\nerror_payload={payload}"
        return template.format(message=self.message, payload=self.payload)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        Returns:
            str:
                Message and error payload.
        """
        template = "{message}\nerror payload={payload}"
        return template.format(message=self.message, payload=self.payload)

    def __init__(self, message: str, payload: dict | None = None):
        """Store the error message and payload.

        Args:
            message (str):
                Message associated with error,
            payload (dict | None):
                Payload of the error. A new dict is used when omitted.
        """
        if payload is None:
            payload = {}
        self.message = message
        self.payload = payload

    def to_dict(self) -> dict:
        """Serialize the exception to a dictionary.

        Returns:
            dict:
                Payload, exception type name, and message.
        """
        rv = {
            "payload": self.payload,
            "type": self.__class__.__name__,
            "message": self.message}
        return rv

    @classmethod
    def raise_by_code(cls, request_data: dict | Any) -> None:
        """Raise when this class owns the status or ``code``.

        A named ``code`` is raised only by the class that lists it.
        The HTTP status is used when the body has no ``code``.

        Args:
            request_data (dict | Any):
                JSON body from an Escavador error response.
                ``request_error_code`` is the HTTP status.

        Raises:
            EscavadorAPIException:
                When this class lists the ``code``, or the status
                and the body has no ``code``.
        """
        if not isinstance(request_data, dict):
            return None

        # A named code belongs to one class. The status is only
        # used when the body does not name a code.
        codes = cls.ESCAVADOR_ERROR_CODES or ()
        status_code = request_data.get("request_error_code")
        body_code = request_data.get("code")
        if body_code is not None:
            if body_code not in codes:
                return None
        elif status_code not in codes:
            return None

        error_message = request_data.get("message")
        if error_message is None:
            error_message = request_data.get("error")
        if not error_message:
            error_message = request_data.get("body")
        if not error_message:
            msg = "HTTP {status_code}".format(status_code=status_code)
            raise cls(message=msg, payload=request_data)
        if body_code is None:
            msg = "{message} (HTTP {status_code})".format(
                message=error_message, status_code=status_code)
        else:
            msg = (
                "{message} (HTTP {status_code}, code `{code}`)")\
                .format(
                    message=error_message,
                    status_code=status_code,
                    code=body_code)
        raise cls(message=msg, payload=request_data)


class EscavadorAPIInvalidParametersException(EscavadorAPIException):
    """Error when the request fails business validation."""

    ESCAVADOR_ERROR_CODES = (422, "UNPROCESSABLE_ENTITY")
    """HTTP 422. Field errors arrive under ``errors``."""


class EscavadorAPIInvalidDocumentException(EscavadorAPIException):
    """Error when the process number is not a CNJ number."""

    ESCAVADOR_ERROR_CODES = ("NUMERO_CNJ_INVALIDO",)
    """Escavador ``code`` for an invalid CNJ on HTTP 422."""


class EscavadorAPIProblemAPIException(EscavadorAPIException):
    """Error when requesting information to API."""

    ESCAVADOR_ERROR_CODES = ()
    """No status of its own. Used when the body is not mapped."""


class EscavadorAPIUnmappedErrorException(EscavadorAPIException):
    """Error not mapped related to the API."""

    ESCAVADOR_ERROR_CODES = ()
    """Fallback when no class lists the status or ``code``."""


class EscavadorAPIAuthenticationError(EscavadorAPIException):
    """Error when the token is missing or rejected."""

    ESCAVADOR_ERROR_CODES = (401,)
    """HTTP 401. The body is ``{"error": "Unauthenticated"}``."""


class EscavadorAPIInsufficientCreditsException(EscavadorAPIException):
    """Error when the account has no API credit."""

    ESCAVADOR_ERROR_CODES = (402,)
    """HTTP 402. The body reports an empty credit balance."""


class EscavadorAPINotFoundException(EscavadorAPIException):
    """Error when the requested resource does not exist."""

    ESCAVADOR_ERROR_CODES = (404, "NOT_FOUND")
    """HTTP 404, or JSON ``code`` ``NOT_FOUND``."""


class EscavadorAPIRateLimitException(EscavadorAPIException):
    """Error when the account exceeds the request rate."""

    ESCAVADOR_ERROR_CODES = (429,)
    """HTTP 429. The message includes how long to wait."""


class EscavadorAPIProcessUpdateAlreadyRequestedException(EscavadorAPIException):
    """Raised when a process update is already in progress."""

    ESCAVADOR_ERROR_CODES = (422, "UNPROCESSABLE_ENTITY")
    """HTTP 422, or JSON ``code`` ``UNPROCESSABLE_ENTITY``."""


class EscavadorAPIErrorTreatment:
    """Map an Escavador error body onto a domain exception."""

    EXCEPTION_CLASSES = [
        EscavadorAPIAuthenticationError,
        EscavadorAPIInsufficientCreditsException,
        EscavadorAPINotFoundException,
        EscavadorAPIInvalidDocumentException,
        EscavadorAPIInvalidParametersException,
        EscavadorAPIRateLimitException,
    ]
    """Checked in order. The CNJ code is before generic HTTP 422."""

    ERROR_TEXT_CLASSES = {
        "Unauthenticated": EscavadorAPIAuthenticationError,
        "NotFound": EscavadorAPINotFoundException,
    }
    """``error`` strings from bodies that have no ``code`` field."""

    @classmethod
    def raise_by_code(cls, request_data: dict | Any) -> None:
        """Raise the exception that owns this error body.

        Args:
            request_data (dict | Any):
                JSON body from an Escavador error response.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401, or ``error`` ``Unauthenticated``.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404, code ``NOT_FOUND``, or ``error``
                ``NotFound``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``. Not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        if isinstance(request_data, dict):
            for exception_class in cls.EXCEPTION_CLASSES:
                exception_class.raise_by_code(
                    request_data=request_data)
            error_text = request_data.get("error")
            text_class = cls.ERROR_TEXT_CLASSES.get(error_text)
            if text_class is not None:
                raise text_class(
                    message=str(error_text),
                    payload=request_data)

        msg = "Unmapped error"
        raise EscavadorAPIUnmappedErrorException(
            message=msg,
            payload={"error": str(request_data)})
