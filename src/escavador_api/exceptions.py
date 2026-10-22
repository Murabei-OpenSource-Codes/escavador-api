"""Custom exceptions for Escavador API."""


class EscavadorAPIException(Exception): # NOQA
    """Custom Escavador API Exception."""

    def __repr__(self):
        """Return the debug representation of the exception.

        Returns:
            str:
                Message and error payload.
        """
        template = "{message}\nerror_payload={payload}"
        return template.format(message=self.message, payload=self.payload)

    def __str__(self):
        """Return the string representation of the exception.

        Returns:
            str:
                Message and error payload.
        """
        template = "{message}\nerror payload={payload}"
        return template.format(message=self.message, payload=self.payload)

    def __init__(self, message: str, payload: dict = {}):
        """Store the error message and payload.

        Args:
            message (str):
                Message associated with error,
            payload (dict):
                Payload of the error, it is parsed when error returned as
                dict.
        """
        self.message = message
        self.payload = payload

    def to_dict(self):
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


class EscavadorAPIInvalidParametersException(EscavadorAPIException):
    """Error when invalid parameters are provided."""
    pass


class EscavadorAPIInvalidDocumentException(EscavadorAPIException):
    """Error when requested document is considered as invalid."""
    pass


class EscavadorAPIProblemAPIException(EscavadorAPIException):
    """Error when requesting information to API."""
    pass


class EscavadorAPIUnmappedErrorException(EscavadorAPIException):
    """Error not mapped related to the API."""
    pass


class EscavadorAPIAuthenticationError(EscavadorAPIException):
    """Error when authentication token is required."""
    pass
