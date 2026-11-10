"""Module to extract information about the involveds from the source data."""


class TransformProcessInvolvedData:
    """Extract information about the involveds from the process data."""

    TEMPLATE_OAB = "{uf}|{numero}"
    """Template to create the OAB number string."""

    @classmethod
    def run(cls, list_involved: list[dict]) -> list[dict]:
        """Extract one record per involved party.

        Args:
            list_involved (list[dict]):
                Involved parties from one fonte.

        Returns:
            list[dict]:
                Normalized party records.
        """
        list_involved_data = []
        for involved_data in list_involved:
            list_involved_data.append(
                cls.extract_involved_data(involved_data))
        return list_involved_data

    @classmethod
    def extract_involved_data(cls, involved_data: dict) -> dict:
        """Extract identity and role fields for one party.

        Args:
            involved_data (dict):
                One involved party from the Escavador API.

        Returns:
            dict:
                Person type, document, role, name, process count,
                OAB registrations, and ``invalid_document`` when CPF/CNPJ
                length does not match ``type_person``.

        Raises:
            NotImplementedError:
                If ``tipo_pessoa`` is set to an unsupported value.
        """
        # Extract information about the involved
        name = involved_data.get('nome')
        number_of_processes = involved_data.get('quantidade_processos')
        type_person = involved_data.get('tipo_pessoa')
        invalid_document = False
        document_number = None
        if type_person == 'JURIDICA':
            document_number = involved_data.get('cnpj')

            # Seems that in some cases, Escavador does not classify the
            # correctly and lead to a invalid document number.
            if document_number is not None:
                if len(document_number) != 14:
                    invalid_document = True
        elif type_person == 'FISICA':
            document_number = involved_data.get('cpf')

            # Seems that in some cases, Escavador does not classify the
            # correctly and lead to a invalid document number.
            if document_number is not None:
                if len(document_number) != 11:
                    invalid_document = True
        else:
            # If the type of person is not known, it is an error.
            # It would be necessary to review the implementation.
            if type_person is not None:
                msg = (
                    "Invalid type of person [{type_person}], add document "
                    "type to package implementation.")\
                    .format(type_person=type_person)
                raise NotImplementedError(msg)

        oabs = cls.extract_oabs(oabs=involved_data.get('oabs', []))

        # Extract information how it is involved at the process
        type_normalized = involved_data.get('tipo_normalizado')
        polarity = involved_data.get('polo')
        return {
            'type_person': type_person,
            'document_number': document_number,
            'type_normalized': type_normalized,
            'polarity': polarity,
            'name': name,
            'number_of_processes': number_of_processes,
            'oabs': oabs,
            'invalid_document': invalid_document}

    @classmethod
    def extract_oabs(cls, oabs: list[dict]) -> str | None:
        """Extract the information about the OABs from the involved.

        OAB is the Brazilian Advoacy Association, it is a mandatory
        registration for lawyers in Brazil.

        Args:
            oabs (list[dict]):
                OAB records with ``uf`` and ``numero``.

        Returns:
            str | None:
                ``UF|number`` values separated by commas, or
                ``None`` when the list is empty.
        """
        list_oabs_str = []
        for oab_doc in oabs:
            list_oabs_str.append(cls.TEMPLATE_OAB.format(
                uf=oab_doc.get('uf'),
                numero=oab_doc.get('numero')))
        if len(list_oabs_str) != 0:
            return ','.join(list_oabs_str)
        return None
