"""Miscellaneous module for auxiliary classes."""
import requests
from typing import Callable
from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_fixed)


RETRY_ERRORS = (requests.ConnectionError, requests.Timeout)
"""Tuple of errors to retry on."""


def retry_on_network_errors(func: Callable) -> Callable:
    """Decorator to retry on network errors (ConnectionError, Timeout).

    Args:
        func: The function to decorate.

    Returns:
        The decorated function.
    """
    return retry(
        retry=retry_if_exception_type(RETRY_ERRORS),
        stop=stop_after_attempt(5), wait=wait_fixed(3),
        reraise=True)(func)
