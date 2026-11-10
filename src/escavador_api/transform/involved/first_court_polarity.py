"""Procedural polarity normalization and first-instance role mapping.

Throughout a lawsuit's lifecycle across varying judicial tiers and appellate
courts (e.g., TJ, TRF, STJ, STF), procedural polarity frequently shifts. In
appellate and interlocutory proceedings, the party filing the appeal is
designated as the active party (e.g., Apelante, Agravante, Recorrente), even
when they originated as the defendant or respondent (Réu, Reclamado, Executado)
in the first-instance court.

This module provides tools to normalize, track, and reconcile circumstantial
appellate postures back to the foundational first-instance polarity, preserving
the core distinction between the party prosecuting the substantive claim and the
party defending against it across all procedural stages.
"""
import pandas as pd


class TransformFirstCourtPolarity:
    """Transform the first court polarity on the process."""

    OUTPUT_COLUMNS = [
        'numero_cnj', 'court_grade', 'court_name', 'court_acronym',
        'court_category', 'court_state', 'type_person', 'document_number',
        'invalid_document', 'type_normalized', 'polarity', 'name',
        'number_of_processes', 'oabs', 'normalized_role',
        'normalized_polarity', 'first_court_polarity']
    """Columns to output."""

    @classmethod
    def transform(cls, involved: pd.DataFrame) -> pd.DataFrame:
        """Attach ``first_court_polarity`` and return ``OUTPUT_COLUMNS``.

        Grade-1 rows supply ``first_court_polarity`` via
        ``normalized_polarity``. The column is left-merged on
        ``numero_cnj``, ``type_person``, and ``document_number``.
        Rows with a null document are dropped from the grade-1 side
        before the merge.

        Args:
            involved (pd.DataFrame):
                Involved parties with ``normalized_role`` and
                ``normalized_polarity``, one row per party and
                court grade.

        Returns:
            pd.DataFrame:
                Merged rows limited to ``OUTPUT_COLUMNS``, including
                ``first_court_polarity``.

        Raises:
            ValueError:
                If duplicate merge keys multiply rows so the row
                count differs from ``involved``.
            KeyError:
                If a column in ``OUTPUT_COLUMNS`` is missing after
                the merge.
        """
        is_first_court = involved['court_grade'] == 1
        loc_columns = [
            'numero_cnj', 'type_person', 'document_number',
            'normalized_polarity']
        first_court_data = involved\
            .loc[is_first_court, loc_columns]\
            .rename(columns={
                'normalized_polarity': 'first_court_polarity'})\
            .dropna()

        # Merge the first court data with the involved data
        involved_with_first_court_polarity = involved.merge(
            first_court_data,
            on=['numero_cnj', 'type_person', 'document_number'],
            how='left')

        if len(involved) != len(involved_with_first_court_polarity):
            raise ValueError(
                "The number of rows in the involved data and the "
                "involved data with the first court polarity do not match")
        return involved_with_first_court_polarity.loc[:, cls.OUTPUT_COLUMNS]
