"""Module to nomilize the party role on the process."""
import pandas as pd
from dataclasses import dataclass
from typing import Literal
from slugify import slugify
from loguru import logger


@dataclass
class PartyRole:
    """One source slug and its normalized role and polarity."""

    key: str
    normalized_role: Literal[
        "judge", "court", "lawyer", "party", "third_party",
        "auxiliary", "fiscal", "representative", "unknown",
        "other"]
    normalized_polarity: Literal[
        "active", "passive", "neutral", "other"]


class TransformPartyRole:
    """Transform the party role on the process."""

    ROLE_MAPPING_DEFAULT: list[PartyRole] = [
        # ----------------------------------------------------
        # Judge & Court Offices (Neutral)
        # ----------------------------------------------------
        PartyRole(
            key="juiz",
            normalized_role="judge",
            normalized_polarity="neutral"),
        PartyRole(
            key="desembargador",
            normalized_role="judge",
            normalized_polarity="neutral"),
        PartyRole(
            key="conciliador_juiz_leigo",
            normalized_role="judge",
            normalized_polarity="neutral"),
        PartyRole(
            key="juizo_deprecante",
            normalized_role="court",
            normalized_polarity="neutral"),
        PartyRole(
            key="juizo_recorrente",
            normalized_role="court",
            normalized_polarity="neutral"),
        PartyRole(
            key="deprecado",
            normalized_role="court",
            normalized_polarity="neutral"),
        PartyRole(
            key="juizo_deprecado",
            normalized_role="court",
            normalized_polarity="neutral"),
        PartyRole(
            key="remetente",
            normalized_role="court",
            normalized_polarity="neutral"),
        # ----------------------------------------------------
        # Lawyers & Prosecutors
        # ----------------------------------------------------
        PartyRole(
            key="advogado",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        PartyRole(
            key="defensor_publico",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        PartyRole(
            key="defensor",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        PartyRole(
            key="procurador",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        PartyRole(
            key="advogado_procurador",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        PartyRole(
            key="promotor_de_justica",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        PartyRole(
            key="procurador_de_justica",
            normalized_role="lawyer",
            normalized_polarity="neutral"),
        # ----------------------------------------------------
        # Active Parties (Claimants, Prosecutors, Appellants, Beneficiaries)
        # ----------------------------------------------------
        PartyRole(
            key="autor",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="coautor",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="beneficiario",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="requerente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="reclamante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="demandante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="exequente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="credor",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="cessionario",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="impetrante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="paciente_impetrante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="suscitante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="investigante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="ordenante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="litisconsorte_ativo",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="opoente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="recorrente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="apelante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="agravante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="embargante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="impugnante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="notificante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="excipiente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="agravante_recorrente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="querelante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="promovente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="inventariante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="confrontante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="reconvinte",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="arguente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="liquidante",
            normalized_role="auxiliary",
            normalized_polarity="active"),
        PartyRole(
            key="arrematante",
            normalized_role="third_party",
            normalized_polarity="active"),
        PartyRole(
            key="terceiro_depositante",
            normalized_role="third_party",
            normalized_polarity="active"),
        PartyRole(
            key="vitima",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="consulente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="assistente_de_acusacao",
            normalized_role="third_party",
            normalized_polarity="active"),
        PartyRole(
            key="representante_notificante",
            normalized_role="representative",
            normalized_polarity="active"),
        PartyRole(
            key="interpelante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="consignante",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="corrigente",
            normalized_role="party",
            normalized_polarity="active"),
        PartyRole(
            key="relatante",
            normalized_role="party",
            normalized_polarity="active"),
        # ----------------------------------------------------
        # Passive Parties (Defendants, Respondents, Targets)
        # ----------------------------------------------------
        PartyRole(
            key="reu",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="relatado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="revel",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="correu",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="requerido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="reclamado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="demandado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="executado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="devedor",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="reconvido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="impetrado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="autoridade",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="acusado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="denunciado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="notificado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="rogado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="interpelado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="falido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="concordataria",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="inventariado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="querelado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="promovido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="autor_do_fato",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="ofensor",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="indiciado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="investigado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="flagranteado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="paciente",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="interditado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="representado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="suscitado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="arguido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="ordenado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="oposto",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="recorrido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="apelado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="agravado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="embargado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="impugnado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="excepto",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="litisconsorte_passivo",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="agravado_recorrido",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="recorrido_agravado",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="consignatario",
            normalized_role="party",
            normalized_polarity="passive"),
        PartyRole(
            key="corrigido",
            normalized_role="party",
            normalized_polarity="passive"),
        # ----------------------------------------------------
        # Neutral / Auxiliary / Third Parties
        # ----------------------------------------------------
        PartyRole(
            key="perito",
            normalized_role="auxiliary",
            normalized_polarity="neutral"),
        PartyRole(
            key="administrador",
            normalized_role="auxiliary",
            normalized_polarity="neutral"),
        PartyRole(
            key="fiel_depositario",
            normalized_role="auxiliary",
            normalized_polarity="neutral"),
        PartyRole(
            key="leiloeiro",
            normalized_role="auxiliary",
            normalized_polarity="neutral"),
        PartyRole(
            key="amicus_curiae",
            normalized_role="auxiliary",
            normalized_polarity="neutral"),
        PartyRole(
            key="testemunha",
            normalized_role="auxiliary",
            normalized_polarity="neutral"),
        PartyRole(
            key="ministerio_publico",
            normalized_role="fiscal",
            normalized_polarity="neutral"),
        PartyRole(
            key="assistente",
            normalized_role="third_party",
            normalized_polarity="neutral"),
        PartyRole(
            key="interessado",
            normalized_role="third_party",
            normalized_polarity="neutral"),
        PartyRole(
            key="representante",
            normalized_role="representative",
            normalized_polarity="neutral"),
        PartyRole(
            key="curador",
            normalized_role="representative",
            normalized_polarity="neutral"),
        PartyRole(
            key="litisconsorte",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="espolio",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="autor_da_heranca",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="testador",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="interessado_querelante",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="herdeiro",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="legatario",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="crianca_ou_adolescente",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="entidade",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="outro",
            normalized_role="unknown",
            normalized_polarity="neutral"),
        # ----------------------------------------------------
        # Cross Appeals (Dual Role -> Mapped to Neutral)
        # ----------------------------------------------------
        PartyRole(
            key="apelante_apelado",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="apelado_apelante",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="agravante_recorrido",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="agravado_recorrente",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="agravado_recorrente_recorrido",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="agravante_agravado",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="agravante_agravado_recorrido",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="agravante_agravado_recorrente",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="recorrente_recorrido",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="recorrido_recorrente",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="apelante_recorrido",
            normalized_role="party",
            normalized_polarity="neutral"),
        PartyRole(
            key="apelado_recorrente",
            normalized_role="party",
            normalized_polarity="neutral"),
    ]
    """List of default mappings, it will be used according to the list order.
       reflecting the priority."""

    ROLE_MAPPING_CUSTOM: list[PartyRole] | None = None
    """When set, ``normalize_role`` uses this list instead of
    ``ROLE_MAPPING_DEFAULT``. The default list is not merged."""

    def set_custom_mapping(self, mapping: list[PartyRole]
                           ) -> list[PartyRole]:
        """Replace the mapping used by ``normalize_role``.

        Args:
            mapping (list[PartyRole]):
                Ordered role mappings. ``key`` must be a slug.
                List order is the priority.

        Returns:
            list[PartyRole]:
                The mapping stored on ``ROLE_MAPPING_CUSTOM``.

        Raises:
            ValueError:
                If an entry is not a ``PartyRole`` or its key
                is not a slug.
        """
        for map_entry in mapping:
            if type(map_entry) is not PartyRole:
                raise ValueError(
                    "The mapping entry must be a PartyRole instance")

            key_slug = slugify(map_entry.key, separator="_")
            if map_entry.key != key_slug:
                raise ValueError(
                    "The key must be a slug. Got {key}.".format(
                        key=map_entry.key))

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
                if type_slugified == entry.key:
                    normalized_fields = {
                        "normalized_role": entry.normalized_role,
                        "normalized_polarity":
                            entry.normalized_polarity}

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
