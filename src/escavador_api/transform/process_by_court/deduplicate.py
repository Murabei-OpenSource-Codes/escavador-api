"""Module to deduplicate the process by court data.

For each ``numero_cnj``, keeps the highest ``court_grade`` row and
left-joins first-instance court and class fields prefixed with
``first_court__``.
"""
import pandas as pd


class TransformDeduplicateProcessByCourt:
    """Collapse multi-grade rows and attach first-instance court fields."""

    FIRST_COURT_COLUMNS = [
        'numero_cnj', 'court_id', 'court_name',
        'court_acronym', 'court_state', 'court_category',
        'root_class_code', 'root_class_name', 'class_code',
        'class_name', 'class_name_full', 'subject_code', 'subject_name',
        'subject_name_full']
    """Columns of the first-instance court."""


    @classmethod
    def run(cls, process_by_court: pd.DataFrame) -> pd.DataFrame:
        """Deduplicate process-by-court rows per CNJ number.

        The output row comes from the largest ``court_grade`` for each
        ``numero_cnj``. Grade-1 court and class columns are merged in with
        the ``first_court__`` prefix (except ``numero_cnj``).

        Args:
            process_by_court (pd.DataFrame):
                Rows from ``TransformProcessData.process`` or
                ``process_list``. Must include ``numero_cnj``,
                ``court_grade``, and the first-instance columns read from
                grade 1 (court id/name/acronym/category, class and subject
                codes and names).

        Returns:
            pd.DataFrame:
                One row per ``numero_cnj``: columns from the highest
                ``court_grade`` row, plus ``first_court__*`` columns when
                a grade-1 row exists.

        Raises:
            KeyError:
                If a required column is missing from the input frame.
            pd.errors.MergeError:
                If more than one grade-1 row shares the same
                ``numero_cnj``.
        """
        if process_by_court.empty:
            return process_by_court
        ordered = process_by_court.sort_values(
            by=["numero_cnj", "court_grade"], ascending=[True, True])

        # Keep the last court to save the job and the nodes
        last_court_grade = ordered.drop_duplicates(
            subset=["numero_cnj"], keep="last")

        # Get the first court to save the class and subject to keep the
        # inicial solicitation associated with the process
        is_first_court_grade = ordered['court_grade'] == 1
        first_court_grade = ordered\
            .loc[is_first_court_grade, cls.FIRST_COURT_COLUMNS]

        # Add a prefix to the columns to avoid conflicts with the last court
        rename_map = {
            column: "first_court_{column}".format(column=column)
            for column in first_court_grade.columns
            if column != "numero_cnj"}
        first_court_grade = first_court_grade.rename(columns=rename_map)

        # Merge the last court with the first court to keep the class and
        # subject to keep the inicial solicitation associated with the process
        results = last_court_grade.merge(
            first_court_grade, on="numero_cnj", how="left",
            validate="one_to_one")
        return results
