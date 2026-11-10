"""Singlotons for the application."""
from escavador_api.transform.involved.party_role import (
    TransformPartyRole)


transform_process_party_role = TransformPartyRole()
"""Shared ``TransformPartyRole`` instance for custom role mappings.

Call ``set_custom_mapping`` on this object to replace the default
mapping for every ``normalize_role`` use in process transforms."""
