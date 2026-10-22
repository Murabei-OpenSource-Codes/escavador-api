"""Escavador API."""
from escavador_api.aux import (
    BaseMixin, GeneralMixin, ProcessMixin, RelatedProcessMixin)


class EscavadorAPI(GeneralMixin, ProcessMixin, RelatedProcessMixin):
    """Main class to interact with Escavador endpoints."""

    def __init__(self, escavador_auth_token: str):
        """Initialize the Escavador API client.

        Args:
            escavador_auth_token (str):
                Authentication token for Escavador API.
        """
        super().__init__(escavador_auth_token=escavador_auth_token)
