"""Python client for the Escavador HTTP API.

Import the client from ``escavador_api.data``::

    from escavador_api.data import EscavadorAPI

    client = EscavadorAPI(escavador_auth_token="token")
    client.get_credit_balance()

The token is required. Request timeout and proxy come from
``escavador_api.config``.
"""
