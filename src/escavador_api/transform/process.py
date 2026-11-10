"""Transform Escavador process payloads into tabular data."""
import pandas as pd

# Local imports
from escavador_api.utils.process import validate_process_number
from escavador_api.transform.involved import (
    TransformProcessInvolvedData, TransformFirstCourtPolarity)
from escavador_api.transform.court import TransformCourtData
from escavador_api.transform.process_by_court import (
    TransformDeduplicateProcessByCourt)
from escavador_api.singletons import transform_process_party_role


class TransformProcessData:
    """Transform Escavador process payloads into tabular data."""

    PROCESS_BY_COURT_COLUMNS = [
        'source_id', 'court_grade', 'confidential',
        'court_id', 'court_name', 'court_acronym', 'court_state',
        'court_category', 'root_class_code', 'root_class_name',
        'class_code', 'class_name', 'class_name_full',
        'subject_code', 'subject_name', 'subject_name_full',
        'predicted_status', 'last_check_date', 'start_date',
        'last_process_update_date', 'number_of_process_updates',
        'number_of_involved', ]
    """Information expected to be present in the process data."""

    PROCESS_COLUMNS = [
        'numero_cnj', 'court_grade', 'confidential', 'court_id', 'court_name',
        'court_acronym', 'court_state', 'court_category', 'root_class_code',
        'root_class_name', 'class_code', 'class_name', 'class_name_full',
        'subject_code', 'subject_name', 'subject_name_full',
        'predicted_status', 'last_check_date', 'start_date',
        'last_process_update_date', 'number_of_process_updates',
        'number_of_involved',

        # First-instance court fields
        'first_court_court_id', 'first_court_court_name',
        'first_court_court_acronym', 'first_court_court_state',
        'first_court_court_category', 'first_court_root_class_code',
        'first_court_root_class_name', 'first_court_class_code',
        'first_court_class_name', 'first_court_class_name_full',
        'first_court_subject_code', 'first_court_subject_name',
        'first_court_subject_name_full']
    """Information expected to be present in the process data."""

    INVOLVED_COLUMNS = [
        'court_grade', 'type_person', 'document_number', 'invalid_document',
        'type_normalized', 'polarity', 'name', 'number_of_processes',
        'oabs', 'court_name', 'court_acronym', 'court_category', 'court_state']
    """Information expected to be present in the process data."""

    SUMMARY_COLUMNS = [
        'last_check_date', 'last_process_update_date', 'class_name', ]
    """Columns of the one-row source summary."""

    @classmethod
    def process_list(cls, process_list: list[dict]) -> dict:
        """Normalize each process and concatenate the results.

        Args:
            process_list (list[dict]):
                Process payloads from the Escavador API.

        Returns:
            dict:
                ``process``: deduplicated rows per ``numero_cnj``.
                ``process_by_court``: one row per court grade.
                ``involved``: parties with role and first-court polarity.
        """
        list_process_by_court = []
        list_process = []
        list_involved = []
        for process_data in process_list:
            transformed_data = TransformProcessData\
                .process(process_data=process_data)
            list_process_by_court.append(transformed_data['process_by_court'])
            list_involved.append(transformed_data['involved'])
            list_process.append(transformed_data['process'])

        # Aggregate all court grades
        all_process_by_court = None
        if len(list_process_by_court) == 0:
            all_process_by_court = pd.DataFrame(
                columns=cls.PROCESS_BY_COURT_COLUMNS)
        else:
            all_process_by_court = pd.concat(list_process_by_court)

        # Aggregate all processes
        all_process = None
        if len(list_process) == 0:
            all_process = pd.DataFrame(
                columns=cls.PROCESS_COLUMNS)
        else:
            all_process = pd.concat(list_process)\
                .loc[:, cls.PROCESS_COLUMNS]

        # Concatenate all involved parties
        all_involved = None
        if len(list_involved) == 0:
            all_involved = pd.DataFrame(columns=cls.INVOLVED_COLUMNS)\
                .pipe(transform_process_party_role.normalize_role)\
                .pipe(TransformFirstCourtPolarity.transform)
        else:
            all_involved = pd.concat(list_involved)\
                .pipe(transform_process_party_role.normalize_role)\
                .pipe(TransformFirstCourtPolarity.transform)
        return {
            "process": all_process,
            "process_by_court": all_process_by_court,
            "involved": all_involved}

    @classmethod
    def process(cls, process_data: dict) -> dict:
        """Loop on all process sources and extract normalized information.

        Args:
            process_data (dict):
                Data from Escavador API.

        Returns:
            dict:
                ``process_by_court``: one row per court grade.
                ``process``: one row per CNJ from
                ``TransformDeduplicateProcessByCourt``.
                ``involved``: unique parties per grade (and
                ``numero_cnj``) after ``aggregate_involved``.
        """
        list_transformed_sources = []
        list_involved_treated = []
        for source_data in process_data.get('fontes', []):
            transformed_source = cls.transform_source_data(
                source_data=source_data)
            involved_list = transformed_source.pop('involved_list')
            list_transformed_sources.append(transformed_source)
            list_involved_treated.extend(involved_list)

        # Aggregate all sources according to the court grade
        pd_grade_aggregated = pd.DataFrame(
            list_transformed_sources,
            columns=cls.PROCESS_BY_COURT_COLUMNS)\
            .pipe(cls.aggregate_sources,
                  numero_cnj=process_data.get('numero_cnj'))

        # Deduplicate the process by court
        unique_process = TransformDeduplicateProcessByCourt\
            .run(process_by_court=pd_grade_aggregated)

        # Get all involved data according to court grade
        pd_involved_treated = pd.DataFrame(
            list_involved_treated,
            columns=['source_id'] + cls.INVOLVED_COLUMNS)\
            .pipe(
                cls.aggregate_involved,
                numero_cnj=process_data.get('numero_cnj'))
        return {
            'involved': pd_involved_treated,
            'process_by_court': pd_grade_aggregated,
            'process': unique_process}

    @classmethod
    def aggregate_sources(cls, pd_transformed_sources: pd.DataFrame,
                          numero_cnj: str) -> pd.DataFrame:
        """Aggregate source rows by court grade.

        Within each grade, rows are ordered by ``last_check_date``
        descending. Columns aggregated with ``first`` come from that
        newest row. Check and movement dates use the maximum.
        ``start_date`` uses the minimum.

        Args:
            pd_transformed_sources (pd.DataFrame):
                One row per Escavador source.
            numero_cnj (str):
                CNJ number stored on every aggregated row.

        Returns:
            pd.DataFrame:
                One row per ``court_grade``, with ``numero_cnj``.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If ``numero_cnj`` is not a valid CNJ number.
        """
        aggregated_sources = pd_transformed_sources\
            .sort_values(
                by=['court_grade', 'last_check_date'],
                ascending=[True, False])\
            .groupby('court_grade', as_index=False)\
            .agg(
                confidential=('confidential', 'any'),
                court_id=('court_id', 'first'),
                court_name=('court_name', 'first'),
                court_acronym=('court_acronym', 'first'),
                court_state=('court_state', 'first'),
                court_category=('court_category', 'first'),
                root_class_code=('root_class_code', 'first'),
                root_class_name=('root_class_name', 'first'),
                class_code=('class_code', 'first'),
                class_name=('class_name', 'first'),
                class_name_full=('class_name_full', 'first'),
                subject_code=('subject_code', 'first'),
                subject_name=('subject_name', 'first'),
                subject_name_full=('subject_name_full', 'first'),
                predicted_status=('predicted_status', 'first'),
                last_check_date=('last_check_date', 'max'),
                start_date=('start_date', 'min'),
                last_process_update_date=('last_process_update_date', 'max'),
                number_of_process_updates=('number_of_process_updates', 'max'),
                number_of_involved=('number_of_involved', 'max'))
        fill_columns = [
            'court_name', 'court_acronym', 'court_category', 'root_class_code',
            'root_class_name', 'class_code', 'class_name', 'class_name_full',
            'subject_code', 'subject_name', 'subject_name_full']
        aggregated_sources.loc[:, fill_columns] = \
            aggregated_sources.loc[:, fill_columns].fillna("Sem informação")

        aggregated_sources.insert(
            0, 'numero_cnj', validate_process_number(numero_cnj))
        return aggregated_sources

    @classmethod
    def aggregate_involved(cls, pd_involved_treated: pd.DataFrame,
                           numero_cnj: str) -> pd.DataFrame:
        """Drop duplicate involved parties within a court grade.

        A party repeats when ``document_number``, ``type_person``,
        and ``court_grade`` match.

        Args:
            pd_involved_treated (pd.DataFrame):
                One row per involved party and source.
            numero_cnj (str):
                CNJ number stored on every remaining row.

        Returns:
            pd.DataFrame:
                Unique parties, without ``source_id``, with
                ``numero_cnj``. When duplicates share the same keys,
                the row with ``invalid_document`` set to ``False``
                is kept.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If ``numero_cnj`` is not a valid CNJ number.
        """
        subset = ['document_number', 'type_person', 'court_grade']
        not_duplicated = pd_involved_treated\
            .sort_values(by=['invalid_document'], ascending=[True])\
            .drop_duplicates(subset=subset, keep='first')\
            .drop(columns=['source_id'])
        not_duplicated\
            .insert(0, 'numero_cnj', validate_process_number(numero_cnj))
        return not_duplicated

    @classmethod
    def transform_source_data(cls, source_data: dict) -> dict:
        """Transform source data into a normalized format.

        Args:
            source_data (dict):
                One fonte from the Escavador API.

        Returns:
            dict:
                Normalized data.
        """
        # Extract the capa information
        process_class_data = cls.extract_capa_info(
            source_data=source_data)
        process_times = cls.extract_count_times_info(
            source_data=source_data)
        court_info = cls.extract_court_info(
            source_data=source_data)
        other_info = cls.extract_other_info(
            source_data=source_data)
        involved_info = cls.extract_involved(
            source_data=source_data,
            court_grade=other_info['court_grade'],
            court_name=court_info['court_name'],
            court_acronym=court_info['court_acronym'],
            court_category=court_info['court_category'],
            court_state=court_info['court_state'],
            source_id=other_info['source_id'])

        # Merge all information
        return_dict = {}
        return_dict.update(process_class_data)
        return_dict.update(process_times)
        return_dict.update(court_info)
        return_dict.update(other_info)
        return_dict['involved_list'] = involved_info
        return return_dict

    @classmethod
    def extract_capa_info(cls, source_data: dict) -> dict:
        """Extract class and subject fields from the process cover.

        The cover is ``capa`` in the source payload.

        Args:
            source_data (dict):
                One fonte from the Escavador API.

        Returns:
            dict:
                Root class, normalized class, and main subject.
        """
        capa_info = source_data.get('capa') or {}

        # Extract the root class
        root_class = capa_info.get('classe_raiz') or {}
        root_class_code = root_class.get('codigo_cnj')
        root_class_name = root_class.get('nome')

        # Extract the process class
        process_class = capa_info.get('classe_normalizada') or {}
        process_class_code = process_class.get('codigo_cnj')
        process_class_name = process_class.get('nome')
        process_class_name_full = process_class.get('path_completo')

        # Extract subject
        process_subject = capa_info.get('assunto_principal_normalizado') or {}
        process_subject_code = process_subject.get('codigo_cnj')
        process_subject_name = process_subject.get('nome')
        process_subject_name_full = process_subject.get('path_completo')
        return {
            'root_class_code': root_class_code,
            'root_class_name': root_class_name,
            'class_code': process_class_code,
            'class_name': process_class_name,
            'class_name_full': process_class_name_full,
            'subject_code': process_subject_code,
            'subject_name': process_subject_name,
            'subject_name_full': process_subject_name_full,
        }

    @classmethod
    def extract_count_times_info(cls, source_data: dict) -> dict:
        """Extract check dates and source counts.

        Args:
            source_data (dict):
                One fonte from the Escavador API.

        Returns:
            dict:
                Naive timestamps for the check, start, and last
                movement, plus update and involved counts.
        """
        data_ultima_verificacao = source_data.get('data_ultima_verificacao')
        data_inicio = source_data.get('data_inicio')
        data_ultima_movimentacao = source_data.get('data_ultima_movimentacao')
        quantidade_movimentacoes = source_data.get('quantidade_movimentacoes')
        quantidade_envolvidos = source_data.get('quantidade_envolvidos')
        return {
            'last_check_date': cls.to_naive_datetime(
                data_ultima_verificacao),
            'start_date': cls.to_naive_datetime(data_inicio),
            'last_process_update_date': cls.to_naive_datetime(
                data_ultima_movimentacao),
            'number_of_process_updates': quantidade_movimentacoes,
            'number_of_involved': quantidade_envolvidos,
        }

    @classmethod
    def to_naive_datetime(cls, value: str | None) -> pd.Timestamp:
        """Parse a timestamp and drop its timezone.

        The clock time stays as sent. ``2024-01-15T10:00:00-03:00``
        becomes ``2024-01-15 10:00:00``.

        Args:
            value (str | None):
                Timestamp from the Escavador API.

        Returns:
            pd.Timestamp:
                Timezone-unaware timestamp, or ``NaT`` when missing.
        """
        parsed = pd.to_datetime(value)
        if getattr(parsed, "tzinfo", None) is None:
            return parsed
        return parsed.tz_localize(None)

    @classmethod
    def extract_court_info(cls, source_data: dict) -> dict:
        """Extract court fields from the source tribunal.

        Args:
            source_data (dict):
                One fonte from the Escavador API.

        Returns:
            dict:
                Court id, name, acronym, category, and ``court_state``
                (UF list from ``TransformCourtData``).
        """
        court_data = source_data.get('tribunal') or {}
        transformed_court = TransformCourtData\
            .run(court_data=court_data)
        return transformed_court

    @classmethod
    def extract_involved(cls, source_data: dict, source_id: int,
                         court_grade: int, court_name: str,
                         court_acronym: str, court_category: str,
                         court_state: str) -> list[dict]:
        """Extract involved parties and attach the source ids.

        Args:
            source_data (dict):
                One fonte from the Escavador API.
            source_id (int):
                Escavador source id stored on each party.
            court_grade (int):
                Court grade stored on each party.
            court_name (str):
                Court name stored on each party.
            court_acronym (str):
                Court acronym stored on each party.
            court_category (str):
                Court category stored on each party.
            court_state (str):
                Court state stored on each party.

        Returns:
            list[dict]:
                Involved parties for this fonte.
        """
        envolvidos = source_data.get('envolvidos') or []
        involved_treated = TransformProcessInvolvedData\
            .run(list_involved=envolvidos)
        for involved_data in involved_treated:
            involved_data['court_grade'] = court_grade
            involved_data['court_name'] = court_name
            involved_data['court_acronym'] = court_acronym
            involved_data['court_category'] = court_category
            involved_data['court_state'] = court_state
            involved_data['source_id'] = source_id
        return involved_treated

    @classmethod
    def extract_other_info(cls, source_data: dict) -> dict:
        """Extract source id, secrecy flag, and court grade.

        Args:
            source_data (dict):
                One fonte from the Escavador API.

        Returns:
            dict:
                ``source_id``, ``confidential``, and ``court_grade``.
        """
        return {
            'source_id': source_data.get('id'),
            'predicted_status': source_data.get('status_previsto'),
            'confidential': source_data.get('segredo_justica', False),
            'court_grade': source_data.get('grau'),
        }
