"""Process movements, public documents, and file downloads."""
import os
import copy
from slugify import slugify
from escavador_api.fetch.base import FetchBaseMixin
from escavador_api.exceptions import EscavadorAPIProblemAPIException
from escavador_api.utils.process import (
    validate_process_number, format_process_number)


class FetchUpdatesAndDocumentsMixin(FetchBaseMixin):
    """Mixin for process movements and document listing or download."""

    TEMPLATE_FILE_NAME = (
        "{process_number}-{id} {date}__{titulo}.{extension}")
    """Filename pattern for saved public documents."""

    @classmethod
    def build_file_name(cls, process_number: str, document: dict) -> str:
        """Build a slugged filename from one document metadata row.

        Args:
            process_number (str):
                CNJ number used as a filename prefix.
            document (dict):
                Escavador document item with ``data.date``, ``titulo``,
                ``id``, and ``extensao_arquivo``.

        Returns:
            str:
                Local filename without directory path.
        """
        return cls.TEMPLATE_FILE_NAME.format(
            process_number=process_number,
            date=slugify(document["data"]['date']),
            titulo=slugify(document["titulo"]),
            id=document["id"],
            extension=document["extensao_arquivo"])

    def get_process_updates(self, process_number: str) -> list[dict]:
        """Retrieve process updates from Escavador using CNJ number.

        This is a paid request.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            list[dict]:
                One dictionary per movement after pagination.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/movimentacoes"\
            .format(process_number=process_number)
        return list(self.fetch_paginated(url=url))

    def get_documents_public(self, process_number: str,
                             download_files: bool = False,
                             folder_path: str = None,
                             save_files: bool = False) -> list[dict]:
        """List public documents, optionally downloading each file.

        This is a paid request. When ``download_files`` and
        ``save_files`` are both ``True``, each item is downloaded,
        written under ``folder_path``, and returned with
        ``file_path``. When both are ``False``, the method
        returns an empty list (metadata is fetched but not returned).

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            download_files (bool):
                When ``True``, call ``download_file`` for each item.
                Must match ``save_files`` (both ``True`` or both ``False``).
            folder_path (str | None):
                Directory for saved files when ``save_files`` is ``True``.
                Defaults to ``./`` inside ``download_file`` when omitted.
            save_files (bool):
                When ``True`` with ``download_files``, persist PDFs to disk.
                Must match ``download_files``.

        Returns:
            list[dict]:
                Document rows augmented with ``file_path`` when
                ``download_files`` and ``save_files`` are ``True``; otherwise
                an empty list.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If flags are mismatched, the Escavador API returns an HTTP
                error, or download arguments are invalid.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        is_valid_download_args = (
            (download_files and save_files) or
            (not download_files and not save_files))
        if not is_valid_download_args:
            msg = (
                "Either download_files or save_files must be True, "
                "but not both")
            raise EscavadorAPIProblemAPIException(
                message=msg,
                payload={
                    "download_files": download_files,
                    "save_files": save_files})

        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/documentos-publicos"\
            .format(process_number=process_number)
        documents = list(self.fetch_paginated(url=url))
        list_documents_results = []
        if download_files:
            for document in documents:
                # If files are to be saved, build the file name
                # using document information
                file_name = None
                if save_files:
                    file_name = self.build_file_name(
                        process_number=process_number,
                        document=document)

                result_data = self.download_file(
                    process_number=process_number,
                    file_key=document["key"],
                    folder_path=folder_path,
                    file_name=file_name,
                    save_file=save_files)
                temp_document = copy.deepcopy(document)
                if save_files:
                    temp_document["file_path"] = result_data
                else:
                    temp_document["file_content"] = result_data
                list_documents_results.append(temp_document)
        return list_documents_results

    def get_documents_all(self, process_number: str) -> list[dict]:
        """Retrieve all available documents associated with a CNJ number.

        This is a paid request.

        This method includes public and restricted documents (when available
        to the authenticated user).

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.

        Returns:
            list[dict]:
                One dictionary per document after pagination.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/autos"\
            .format(process_number=process_number)
        return list(self.fetch_paginated(url=url))

    def download_file(self, process_number: str, file_key: str,
                      folder_path: str = None, file_name: str = None,
                      save_file: bool = False
                      ) -> bytes | str:
        """Download one process document as binary PDF.

        This is a paid request. The CNJ value is formatted before the
        request. The route is ``GET .../documentos/{file_key}``.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            file_key (str):
                Escavador document key from a list endpoint.
            folder_path (str | None):
                Directory when ``save_file`` is ``True``. Defaults to
                ``./``.
            file_name (str | None):
                Basename when ``save_file`` is ``True``. Defaults to
                ``{file_key}.pdf``.
            save_file (bool):
                When ``True``, write bytes to disk and return the full path.

        Returns:
            bytes | str:
                File content when ``save_file`` is ``False``; otherwise the
                path joined from ``folder_path`` and ``file_name``.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number.
            EscavadorAPIProblemAPIException:
                If ``save_file`` is ``False`` and ``folder_path`` or
                ``file_name`` is missing, or the Escavador API returns an
                HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        if folder_path is None or file_name is None:
            if not save_file:
                msg = (
                    "Folder path and file name must be provided if "
                    "save_file is False")
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={
                        "folder_path": folder_path,
                        "file_name": file_name})
        if save_file:
            if folder_path is None:
                folder_path = "./"
            if file_name is None:
                file_name = "{file_key}.pdf"\
                    .format(file_key=file_key)

        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)

        # Clean special characters from CNJ number and
        # ensure correct punctuation (required for downloads)
        # Format: NNNNNNN-DD.AAAA.J.TR.OOOO
        formatted_process_number = format_process_number(process_number)
        url = (
            "v2/processos/numero_cnj/{formatted_process_number}/"
            "documentos/{file_key}").format(
                formatted_process_number=formatted_process_number,
                file_key=file_key)

        # File content is returned as binary
        content = self.get_binary(url=url)
        if save_file:
            full_file_path = os.path.join(folder_path, file_name)
            with open(full_file_path, "wb") as file:
                file.write(content)
            return full_file_path
        else:
            return content
