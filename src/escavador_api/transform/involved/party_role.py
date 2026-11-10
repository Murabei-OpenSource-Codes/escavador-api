"""Module to nomilize the party role on the process."""
import pandas as pd
from dataclasses import dataclass
from typing import Literal, TypedDict
from slugify import slugify
from loguru import logger


@dataclass
class PartyRole:
    """Class to represent the party role."""

    normalized_role: Literal[
        "judge", "lawyer", "party", "auxiliary",
        "other"]
    normalized_polarity: Literal[
        "active", "passive", "neutral", "other"]


class PartyRoleEntry(TypedDict):
    """One source role and its normalized role."""

    key: str
    value: PartyRole


class TransformPartyRole:
    """Transform the party role on the process."""

    ROLE_MAPPING_DEFAULT: list[PartyRoleEntry] = [
        {
            "key": "juiz",
            "value": PartyRole(
                normalized_role="judge",
                normalized_polarity="neutral"),
        },
        {
            "key": "juizo_deprecante",
            "value": PartyRole(
                normalized_role="judge",
                normalized_polarity="neutral"),
        },
        {
            "key": "juizo_recorrente",
            "value": PartyRole(
                normalized_role="judge",
                normalized_polarity="neutral"),
        },

        ###########
        # Lawyers #
        # Active
        {
            "key": "promotor_de_justica",
            "value": PartyRole(
                normalized_role="lawyer",
                normalized_polarity="active"),
        },
        {
            "key": "procurador_de_justica",
            "value": PartyRole(
                normalized_role="lawyer",
                normalized_polarity="active"),
        },
        {
            "key": "procurador",
            "value": PartyRole(
                normalized_role="lawyer",
                normalized_polarity="active"),
        },

        # Not possible to determine
        {
            "key": "advogado",
            "value": PartyRole(
                normalized_role="lawyer",
                normalized_polarity="other"),
        },

        ###########
        # Parties #
        # Active (Attack / Enforcement / Appeals) #
        {
            "key": "ministerio_publico",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "autor",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "coautor",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "requerente",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "reclamante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "demandante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "exequente",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "impetrante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "suscitante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "investigante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "ordenante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "litisconsorte_ativo",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "notificante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "recorrente",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "apelante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "agravante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "embargante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        {
            "key": "paciente_impetrante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },
        # Normally associated with a beneficiary role of free law
        # in Brazil, it is active asking for the benefit of the law
        {
            "key": "beneficiario",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="active"),
        },

        # Passive (Defense / Targets)
        {
            "key": "reu",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "correu",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "requerido",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "notificado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "reclamado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "demandado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "executado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "impetrado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "autoridade",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "acusado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "denunciado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "investigado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "averiguado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "flagranteado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "interditado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "representado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "suscitado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "ordenado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "recorrido",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "apelado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "agravado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "embargado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "vitima",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "indiciado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "paciente",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },
        {
            "key": "litisconsorte_passivo",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="passive"),
        },

        # Other party
        {
            "key": "litisconsorte",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="other"),
        },
        {
            "key": "espolio",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="other"),
        },
        {
            "key": "apelante_apelado",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="other"),
        },
        {
            "key": "apelado_apelante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="other"),
        },


        ########################################
        # Auxiliary, Witnesses & Third Parties #
        {
            "key": "perito",
            "value": PartyRole(
                normalized_role="auxiliary",
                normalized_polarity="neutral"),
        },
        {
            "key": "testemunha",
            "value": PartyRole(
                normalized_role="auxiliary",
                normalized_polarity="neutral"),
        },
        {
            "key": "assistente",
            "value": PartyRole(
                normalized_role="other",
normalized_polarity="neutral"),
        },
        {
            "key": "interessado",
            "value": PartyRole(
                normalized_role="other",
normalized_polarity="other"),
        },
        {
            "key": "outro",
            "value": PartyRole(
                normalized_role="other",
                normalized_polarity="other"),
        },

        # Representatives
        {
            "key": "representante",
            "value": PartyRole(
                normalized_role="party",
                normalized_polarity="other"),
        },

        # Other special types of judges with more generical names
        {
            "key": "deprecado",
            "value": PartyRole(
                normalized_role="judge",
                normalized_polarity="neutral"),
        },
        {
            "key": "remetente",
            "value": PartyRole(
                normalized_role="judge",
                normalized_polarity="neutral"),
        },
    ]
    """List of default mappings, it will be used according to the list order.
       reflecting the priority."""

    ROLE_MAPPING_CUSTOM: list[PartyRoleEntry] | None = None
    """When set, ``normalize_role`` uses this list instead of
    ``ROLE_MAPPING_DEFAULT``. The default list is not merged."""

    def set_custom_mapping(self, mapping: list[dict[str, PartyRole]]
                          ) -> list[PartyRoleEntry]:
        """Replace the mapping used by ``normalize_role``.

        Args:
            mapping (list[dict[str, PartyRole]]):
                List of ``PartyRoleEntry``-shaped dicts with slug keys.

        Returns:
            list[PartyRoleEntry]:
                The mapping stored on ``ROLE_MAPPING_CUSTOM``.

        Raises:
            ValueError:
                If an entry is not a dict, the key is not a slug, or the
                value is not a ``PartyRole`` instance.
        """
        for map_entry in mapping:
            if type(map_entry) is not dict:
                raise ValueError(
                    "The mapping must be a dictionary")

            key = map_entry["key"]
            key_slug = slugify(key, separator="_")
            if key != key_slug:
                raise ValueError(
                    "The key must be a slug. Got {key}.".format(
                        key=key))

            value = map_entry["value"]
            if type(value) is not PartyRole:
                raise ValueError(
                    "The value must be a PartyRole instance")

        # Set the custom mapping
        self.ROLE_MAPPING_CUSTOM = mapping
        return self.ROLE_MAPPING_CUSTOM

    def normalize_role(self, involved: pd.DataFrame) -> pd.DataFrame:
        """Add ``normalized_role`` and ``normalized_polarity`` to each row.

        Uses ``ROLE_MAPPING_CUSTOM`` when set; otherwise
        ``ROLE_MAPPING_DEFAULT``. Unmapped types become ``other`` / ``other``
        and log a warning.
        """
        # Custom mapping replaces the default; it is not merged with it.
        role_mapping = self.ROLE_MAPPING_CUSTOM or self.ROLE_MAPPING_DEFAULT

        list_of_entries = []
        for row_data in involved.to_dict(orient="records"):
            # Slugify the type and try to match with the mapping
            type_slugified = slugify(
                row_data["type_normalized"], separator="_")
            normalized_fields = None
            for entry in role_mapping:
                if type_slugified == entry["key"]:
                    normalized_fields = {
                        "normalized_role":
                            entry["value"].normalized_role,
                        "normalized_polarity":
                            entry["value"].normalized_polarity}

            # If no match, than set the role to other and warn to add to
            # mapping
            if normalized_fields is None:
                logger.warning(
                    "No mapping found for type [{type_normalized}], "
                    "expecting slug [{key_slug}] on mapping.",
                    type_normalized=row_data["type_normalized"],
                    key_slug=type_slugified)
                normalized_fields = {
                    "normalized_role": "other",
                    "normalized_polarity": "other",
                }

            # Add the fields to the row data
            row_data.update(normalized_fields)
            list_of_entries.append(row_data)

        # Return the DataFrame
        return pd.DataFrame(list_of_entries)
