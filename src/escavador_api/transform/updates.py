"""Module to transform updates data from Escavador API."""
import pandas as pd
from loguru import logger
from slugify import slugify


class TransformUpdateData:
    """Transform updates data from Escavador API."""

    NORM_UPDATES_COLUMNS = [
        'movimentacao_id', 'date', 'court_grade', 'type', 'content',
        'extra_info']
    """Columns produced for one movement."""

    NORM_DOCUMENT_COLUMNS = [
        'movimentacao_id', 'file_path']
    """Columns produced for one document-to-movement link."""

    UPDATE_TYPE_MAP = {
        'andamento': 'update',
        'publicacao': 'publication',
    }
    """Slug of Escavador ``tipo`` to the normalized ``type``.

    ``ANDAMENTO`` and ``PUBLICAÇÃO`` (also ``PUBLICACAO``) are the
    values returned by ``GET .../movimentacoes``.
    """

    @classmethod
    def merge_documents(cls, updates: list[dict],
                        documents: list[dict]) -> pd.DataFrame:
        """Left-join document paths onto normalized movements.

        Args:
            updates (list[dict]):
                Raw movement payloads passed to
                ``normalize_updates``.
            documents (list[dict]):
                Raw document payloads passed to
                ``normalize_documents``. After that step,
                ``movimentacao_id`` must be unique.

        Returns:
            pd.DataFrame:
                Movements with ``file_path`` from the matching
                document.

        Raises:
            pandas.errors.MergeError:
                If one movement id maps to more than one document
                row.
        """
        pd_updates = cls.normalize_updates(updates=updates)
        pd_documents = cls.normalize_documents(documents=documents)
        return pd_updates.merge(
            pd_documents, on='movimentacao_id', how='left',
            validate='many_to_one')

    @classmethod
    def normalize_updates(cls, updates: list[dict]) -> pd.DataFrame:
        """Map each movement onto ``NORM_UPDATES_COLUMNS``.

        Unmapped ``tipo`` values are logged and skipped.

        Args:
            updates (list[dict]):
                Raw Escavador movement payloads. The day of the
                movement is the field ``data`` (``YYYY-MM-DD``).

        Returns:
            pd.DataFrame:
                One row per movement whose ``tipo`` is in
                ``UPDATE_TYPE_MAP``.
        """
        list_norm_updates = []
        for data in updates:
            tipo = data.get('tipo')
            tipo_slug = slugify(tipo) if isinstance(tipo, str) else ''
            norm_type = cls.UPDATE_TYPE_MAP.get(tipo_slug)
            if norm_type is None:
                logger.warning(
                    "Update type {tipo} not found in the map",
                    tipo=tipo)
                continue

            fonte = data['fonte']
            extra_info = {
                'fonte': fonte,
                'classificacao_predita': data['classificacao_predita'],
                'texto_categoria': data['texto_categoria'],
                'escavador_id': data['id'],
                'tipo_publicacao': data['tipo_publicacao'],
                'pagina': data['pagina']}

            normalized_data = {
                'movimentacao_id': data['id'],
                'date': data['data'],
                'court_grade': fonte['grau'],
                'type': norm_type,
                'content': data['conteudo'],
                'extra_info': extra_info}
            list_norm_updates.append(normalized_data)
        return pd.DataFrame(
            list_norm_updates, columns=cls.NORM_UPDATES_COLUMNS)

    @classmethod
    def normalize_documents(cls, documents: list[dict]) -> pd.DataFrame:
        """Build one row per related movement on a document.

        Args:
            documents (list[dict]):
                Public-document payloads. ``file_path`` is set when
                the file was saved locally.

        Returns:
            pd.DataFrame:
                ``movimentacao_id`` and ``file_path``. Repeated links
                with the same path are dropped.
        """
        list_norm_documents = []
        for data in documents:
            related = data.get('movimentacoes_relacionadas') or []
            file_path = data.get('file_path')
            for mov in related:
                normalized_data = {
                    'movimentacao_id': mov['id'],
                    'file_path': file_path}
                list_norm_documents.append(normalized_data)
        frame = pd.DataFrame(
            list_norm_documents,
            columns=cls.NORM_DOCUMENT_COLUMNS)
        return frame.drop_duplicates(
            subset=['movimentacao_id', 'file_path'])
