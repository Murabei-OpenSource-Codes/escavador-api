"""General configuration for the Escavador API."""
import os


def _positive_int(name: str, default: int) -> int:
    """Read a positive integer from the environment.

    A missing or blank value returns ``default``.

    Args:
        name (str):
            Environment variable name.
        default (int):
            Value used when the variable is missing or blank.

    Returns:
        int:
            Parsed positive integer.

    Raises:
        ValueError:
            If the value is not a positive integer.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(
            "{name} must be a positive integer. Got {raw}.".format(
                name=name, raw=raw)) from None
    if value < 1:
        raise ValueError(
            "{name} must be a positive integer. Got {raw}.".format(
                name=name, raw=raw))
    return value


REQUEST_TIMEOUT: int = _positive_int(
    "ESCAVADOR_API__REQUEST_TIMEOUT", 60)
"""Timeout for requests to the Escavador API."""

PROXY_URL = os.environ.get("ESCAVADOR_API__PROXY_URL", None)
"""URL of the proxy to use for requests to the Escavador API."""

MAX_PAGES: int = _positive_int(
    "ESCAVADOR_API__MAX_PAGES", 200)
"""Max extra pages fetched after the first response."""