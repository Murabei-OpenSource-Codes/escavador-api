"""Custom exceptions for Escavador API."""


class EscavadorAPIException(Exception): # NOQA
    """Custom Tratum API Exception."""

    def __repr__(self):
        """__repr__."""
        template = "{class_name}: {message}"
        return template.format(
            class_name=self.__class__.__name__,
            message=self.message)

    def __str__(self):
        """__str__."""
        return self.__repr__()

    def __init__(self, message: str, payload: dict = {}):
        """__init__.

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
        """to_dict."""
        rv = {
            "payload": self.payload,
            "type": self.__class__.__name__,
            "message": self.message}
        return rv


class EscavadorAPIInvalidDocumentException(EscavadorAPIException):
    """Error when requested document is considered as invalid."""
    pass


class EscavadorAPIProblemAPIException(EscavadorAPIException):
    """Error when requesting information to API."""
    pass


class EscavadorAPIUnmappedErrorException(EscavadorAPIException):
    """Error not mapped related to the API."""
    pass
