"""Process movements, public documents, and file downloads."""
import os
import copy
from urllib.parse import quote
from slugify import slugify
from escavador_api.fetch.base import FetchBaseMixin
from escavador_api.exceptions import (
    EscavadorAPIException, EscavadorAPIProblemAPIException)
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

    @staticmethod
    def _note_download_failure(exc: EscavadorAPIException,
                               file_key: str | None,
                               written_paths: list[str]) -> None:
        """Record the failed key and files already saved.

        Args:
            exc (EscavadorAPIException):
                Exception raised for the current document.
            file_key (str | None):
                Escavador key of the document that failed.
            written_paths (list[str]):
                Paths saved before this failure.
        """
        payload = {}
        if isinstance(exc.payload, dict):
            payload.update(exc.payload)
        payload["file_key"] = file_key
        payload["written_paths"] = list(written_paths)
        exc.payload = payload
        exc.message = (
            "{message}. file_key={file_key}; "
            "written_paths={written_paths}").format(
                message=exc.message,
                file_key=file_key,
                written_paths=written_paths)

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
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/movimentacoes"\
            .format(process_number=process_number)
        return list(self.fetch_paginated(url=url))

    def get_documents_public(self, process_number: str,
                             download_files: bool = False,
                             folder_path: str | None = None,
                             save_files: bool = False) -> list[dict]:
        """List public documents, optionally downloading each file.

        This is a paid request. When ``download_files`` is
        ``False``, the method returns the document rows. When it
        is ``True`` and ``save_files`` is ``False``, each item is
        downloaded and returned with ``file_content``. When both
        are ``True``, each item is written under ``folder_path``
        and returned with ``file_path``. A failure keeps the
        original exception and adds ``file_key`` and
        ``written_paths`` to its payload.

        Args:
            process_number (str):
                Process number following CNJ format (20 digits). Punctuation
                is optional.
            download_files (bool):
                When ``True``, call ``download_file`` for each item.
            folder_path (str | None):
                Directory for saved files when ``save_files`` is ``True``.
                Defaults to ``./`` inside ``download_file`` when omitted.
            save_files (bool):
                When ``True``, persist each download to disk. Requires
                ``download_files``.

        Returns:
            list[dict]:
                Document rows. ``file_content`` is set when files are
                downloaded and not saved. ``file_path`` is set when
                both flags are ``True``.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIProblemAPIException:
                If ``save_files`` is ``True`` without ``download_files``,
                or a document row has no ``key``. The payload lists
                ``written_paths``.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        if save_files and not download_files:
            msg = "save_files requires download_files"
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
        if not download_files:
            return documents

        list_documents_results = []
        written_paths = []
        for document in documents:
            file_key = document.get("key")
            if not file_key:
                msg = "Document row has no key"
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={
                        "file_key": file_key,
                        "written_paths": list(written_paths)})
            try:
                # If files are to be saved, build the file name
                # using document information
                file_name = None
                if save_files:
                    file_name = self.build_file_name(
                        process_number=process_number,
                        document=document)

                result_data = self.download_file(
                    process_number=process_number,
                    file_key=file_key,
                    folder_path=folder_path,
                    file_name=file_name,
                    save_file=save_files)
            except EscavadorAPIException as exc:
                self._note_download_failure(
                    exc=exc,
                    file_key=file_key,
                    written_paths=written_paths)
                raise
            except Exception as exc:
                msg = (
                    "Download failed for file_key `{file_key}`")\
                    .format(file_key=file_key)
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={
                        "file_key": file_key,
                        "written_paths": list(written_paths),
                        "error": str(exc)}) from exc

            temp_document = copy.deepcopy(document)
            if save_files:
                temp_document["file_path"] = result_data
                written_paths.append(result_data)
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
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        # Checks if process number is valid before sending request
        process_number = validate_process_number(process_number)
        url = "v2/processos/numero_cnj/{process_number}/autos"\
            .format(process_number=process_number)
        return list(self.fetch_paginated(url=url))

    def download_file(self, process_number: str, file_key: str,
                      folder_path: str | None = None,
                      file_name: str | None = None,
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
                Escavador document key from a list endpoint. Quoted
                in the request URL.
            folder_path (str | None):
                Directory when ``save_file`` is ``True``. Defaults to
                ``./``.
            file_name (str | None):
                Basename when ``save_file`` is ``True``. A missing
                name defaults to ``{file_key}.pdf``. Slashes in the
                key are replaced. A path is rejected.
            save_file (bool):
                When ``True``, write bytes to disk and return the full path.
                The directory is created when missing. Bytes go to a
                ``.part`` file, then that file is renamed into place.

        Returns:
            bytes | str:
                File content when ``save_file`` is ``False``; otherwise the
                path joined from ``folder_path`` and ``file_name``.

        Raises:
            EscavadorAPIInvalidDocumentException:
                If process_number is not a valid CNJ number, or
                the API code is ``NUMERO_CNJ_INVALIDO``.
            EscavadorAPIProblemAPIException:
                If ``file_name`` is not a basename.
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        if save_file:
            if folder_path is None:
                folder_path = "./"
            if file_name is None:
                safe_key = str(file_key).replace("/", "_")\
                    .replace("\\", "_")
                file_name = "{file_key}.pdf".format(file_key=safe_key)
            name_is_basename = os.path.basename(file_name) == file_name
            if (
                    not file_name
                    or file_name in (".", "..")
                    or not name_is_basename):
                msg = "file_name must be a basename"
                raise EscavadorAPIProblemAPIException(
                    message=msg,
                    payload={"file_name": file_name})

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
                file_key=quote(str(file_key), safe=""))

        # File content is returned as binary
        content = self.get_binary(url=url)
        if save_file:
            os.makedirs(folder_path, exist_ok=True)
            full_file_path = os.path.join(folder_path, file_name)
            temporary_path = "{path}.part".format(path=full_file_path)
            try:
                with open(temporary_path, "wb") as file:
                    file.write(content)
                os.replace(temporary_path, full_file_path)
            except Exception:
                try:
                    if os.path.exists(temporary_path):
                        os.remove(temporary_path)
                except OSError:
                    pass
                raise
            return full_file_path
        else:
            return content
