"""General configuration for the Escavador API."""
import os


REQUEST_TIMEOUT = int(os.environ.get("ESCAVADOR_API__REQUEST_TIMEOUT", 60))
"""Timeout for requests to the Escavador API."""
PROXY_URL = os.environ.get("ESCAVADOR_API__PROXY_URL", None)
"""URL of the proxy to use for requests to the Escavador API.

If not set, no proxy will be used.
"""
