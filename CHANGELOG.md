# Changelog

All notable changes to this package are documented here.

The format is based on Keep a Changelog. The version is the package
tag produced by `build.sh` (beta tags on branches other than `main`).
Entries start at `0.1.10`. Older tags remain in git only.

## [0.1.26] - 2026-11-20

### Added
- `EscavadorAPIInsufficientCreditsException`, `EscavadorAPINotFoundException`,
  and `EscavadorAPIRateLimitException` for HTTP 402, 404, and 429
- `EscavadorAPIProcessUpdateAlreadyRequestedException` — raised when
  `request_process_update_public` or `request_process_update_full`
  get HTTP 422 ``UNPROCESSABLE_ENTITY`` for a duplicate update request

### Changed
- `get_documents_public` — returns paged rows when download flags are
  false. Download without save sets ``file_content``. Failures add
  ``file_key`` and ``written_paths`` to the exception payload
- `download_file` — bytes when ``save_file`` is false without path
  args. Quotes ``file_key``. Rejects a non-basename ``file_name``.
  Writes via a ``.part`` file, then renames into place
- HTTP error payloads use ``request_error_code``. Status 401, 402, 404,
  422, and 429 raise dedicated classes. ``NUMERO_CNJ_INVALIDO`` stays
  on ``EscavadorAPIInvalidDocumentException``
- `get`, `get_binary`, `post`, `delete`, and `patch` re-raise when the
  failure happens before a response exists. Retries log a loguru
  warning before each 3s sleep
- `TransformProcessData.process_list` with an empty list returns empty
  frames. ``involved`` keeps the first-court polarity columns
- `EscavadorAPIException` uses a new payload dict when none is passed
- Method docstrings list status-specific exceptions instead of only
  ``EscavadorAPIProblemAPIException``

### Removed
- `request_process_public_documents` — same route as
  ``request_process_update_public`` (``{"documentos_publicos": 1}``)

## [0.1.25] - 2026-11-18

### Added
- `TransformUpdateData.merge_documents` — maps `andamento` to
  `update` and `publicacao` to `publication`, then left-joins
  `file_path`
- `get_documents_public` — pages public documents. `download_files`
  and `save_files` must both be true (saved rows include
  `file_path`) or both false (returns `[]`)
- `download_file` — one document as bytes, or a path when
  `save_file` is true

### Changed
- `get_documents_all` replaces `get_process_all_documents`
  (`GET .../autos`, still `list[dict]`)
- `get_process_updates` moved to `FetchUpdatesAndDocumentsMixin`.
  `EscavadorAPI` still exposes it
- `request_process_public_documents`,
  `request_process_update_public`, `request_process_update_full`,
  and `get_process_update_status` moved from `FetchProcessMixin`
  to `FetchOnDemandMixin`. `EscavadorAPI` still exposes them
- `delete` and `patch` retry connection errors and timeouts
  (5 attempts, 3 seconds apart), same as `get` and `post`
- HTTP error payloads include `status_code`. A non-JSON body
  raises `EscavadorAPIProblemAPIException`
- `TransformProcessData.process` applies role normalization and
  first-court polarity per process. `process_list` concatenates
  those frames
- `TransformProcessData.process_list` with an empty process list
  raises `ValueError` from `pandas.concat` on `involved`
- `TransformPartyRole.normalize_role` fills `NORMALIZED_COLUMNS`
  when the input has no rows

### Removed
- `get_process_public_documents` and `get_process_documents`
  (both read `GET .../documentos-publicos`)
- `download_process_file` — no PDF header check. Use
  `download_file`
- `escavador_api.fetch.misc.retry_on_network_errors`

## [0.1.24] - 2026-11-16

### Changed
- Package version tag only. Behavior matches `0.1.23`.

## [0.1.23] - 2026-11-16

### Changed
- Package version tag only. Behavior matches `0.1.22`.

## [0.1.22] - 2026-11-16

### Changed
- `get_process_updates`, `get_process_public_documents`,
  `get_process_documents`, `get_process_all_documents`,
  `list_monitoring_new_process`,
  `get_results_monitoring_new_process`, and
  `list_monitoring_existing_process` — return `list[dict]` after
  paging (previously lazy generators from `fetch_paginated`)

## [0.1.21] - 2026-11-16

### Changed
- Package version tag only. Behavior matches `0.1.20` after README,
  CHANGELOG, and public docstring updates in the prior commit.

## [0.1.20] - 2026-11-16

### Added
- `ROLE_MAPPING_DEFAULT` — lawyer / `neutral`: `advogado_procurador`,
  `defensor`
- `ROLE_MAPPING_DEFAULT` — active: `assistente_de_acusacao`, `consulente`,
  `interpelante`, `consignante`, `corrigente`, `relatante`
  (`party` / `active`), `representante_notificante`; `terceiro_depositante`
  (`third_party` / `active`)
- `ROLE_MAPPING_DEFAULT` — passive: `revel`, `ofensor`, `interpelado`,
  `consignatario`, `corrigido`, `recorrido_agravado`, `rogado`,
  `relatado`
- `ROLE_MAPPING_DEFAULT` — `conciliador_juiz_leigo` (`judge` / `neutral`),
  `fiel_depositario` (`auxiliary` / `neutral`),
  `agravado_recorrente_recorrido` (`party` / `neutral`)

### Changed
- `ROLE_MAPPING_DEFAULT` and `set_custom_mapping` — when a slug appears
  more than once, the later entry is used
- `TransformPartyRole.normalize_role` — documents `Args`, `Returns`, and
  `KeyError` when `type_normalized` is missing
- `TransformProcessData.process_list` and `process` — document
  `EscavadorAPIInvalidDocumentException` on invalid `numero_cnj`
- `TransformCourtData.__init__` — docstring for stored process payload
- `config.PROXY_URL` — typed as `str | None`

## [0.1.19] - 2026-11-15

### Changed
- `ROLE_MAPPING_DEFAULT` entries are `PartyRole` values (`key`,
  `normalized_role`, `normalized_polarity`), not dicts
- Default `normalized_role` values are `judge`, `court`, `lawyer`,
  `party`, `third_party`, `auxiliary`, `fiscal`, `representative`,
  and `unknown`. Unmapped types stay `other` / `other`
- Court offices `juizo_deprecante`, `juizo_recorrente`,
  `juizo_deprecado`, `deprecado`, and `remetente` map to `court` /
  `neutral` (previously `judge` / `neutral`)
- `advogado`, `defensor_publico`, `procurador`,
  `promotor_de_justica`, and `procurador_de_justica` map to
  `lawyer` / `neutral`
- `ministerio_publico` maps to `fiscal` / `neutral` (previously
  `party` / `active`)
- `assistente` and `interessado` map to `third_party` / `neutral`
- `representante` and `curador` map to `representative` / `neutral`
- `vitima` maps to `party` / `active` (previously `party` /
  `passive`). `liquidante` maps to `auxiliary` / `active`
  (previously `auxiliary` / `neutral`)
- `outro` maps to `unknown` / `neutral` (previously `other` /
  `other`)
- Dual-role appeal slugs, plus `autor_da_heranca`, `espolio`,
  `interessado_querelante`, `legatario`, `litisconsorte`, and
  `testador`, stay `party` and use polarity `neutral` (previously
  `other`)

### Added
- `ROLE_MAPPING_DEFAULT` — `desembargador` (`judge` / `neutral`)
- `ROLE_MAPPING_DEFAULT` — active `party`: `agravante_recorrente`,
  `cessionario`, `confrontante`, `credor`, `inventariante`,
  `opoente`, `promovente`, `querelante`
- `ROLE_MAPPING_DEFAULT` — `arrematante` (`third_party` / `active`)
- `ROLE_MAPPING_DEFAULT` — passive `party`: `agravado_recorrido`,
  `autor_do_fato`, `devedor`, `inventariado`, `oposto`,
  `promovido`, `querelado`, `reconvido`
- `ROLE_MAPPING_DEFAULT` — neutral `party`: `agravado_recorrente`,
  `agravante_agravado`, `agravante_agravado_recorrente`,
  `agravante_agravado_recorrido`, `agravante_recorrido`,
  `crianca_ou_adolescente`, `entidade`, `herdeiro`

### Removed
- `PartyRoleEntry` — dict wrapper around `PartyRole`
- `averiguado` from `ROLE_MAPPING_DEFAULT`. That source type now
  falls through to `other` / `other`

## [0.1.18] - 2026-11-15

### Added
- `TransformPartyRole.ROLE_MAPPING_DEFAULT` — 24 court roles that
  previously warned and fell through to `other` / `other`
- Judge / neutral: `juizo_deprecado`
- Lawyer / other: `defensor_publico`
- Party / active: `reconvinte`, `impugnante`, `arguente`,
  `excipiente`
- Party / passive: `impugnado`, `arguido`, `excepto`, `falido`,
  `concordataria`
- Party / other: `recorrente_recorrido`, `recorrido_recorrente`,
  `apelante_recorrido`, `apelado_recorrente`,
  `interessado_querelante`, `testador`, `autor_da_heranca`,
  `legatario`, `curador`
- Auxiliary / neutral: `amicus_curiae`, `leiloeiro`,
  `administrador`, `liquidante`

## [0.1.17] - 2026-11-11

### Changed
- `pyproject.toml` — declare `loguru`, `pandas`, and `python-slugify`
  as package dependencies; list `requests` and `tenacity` without
  pinned ranges
- README Requirements — dependency list matches `pyproject.toml`

## [0.1.16] - 2026-11-10

### Changed
- README ETL section, transform feature bullet, and installation notes
  for pandas and `python-slugify`

## [0.1.15] - 2026-11-10

### Added
- `request_process_public_documents` — POST update with
  `{"documentos_publicos": 1}` on `solicitar-atualizacao`
- `get_process_documents` — paginated `GET .../documentos-publicos`
- `test__public_documents` integration tests

### Changed
- README API reference and pagination list for the new document routes

## [0.1.13] - 2026-11-10

### Added
- HTTP client mixins under `escavador_api.fetch` (`FetchBaseMixin`,
  `FetchGeneralMixin`, `FetchProcessMixin`, `FetchRelatedProcessMixin`)
- `escavador_api.transform.TransformProcessData` — normalize Escavador
  process payloads into `process`, `process_by_court`, and `involved`
  DataFrames (`process_list`, `process`)
- `TransformCourtData` — tribunal acronym normalization and UF mapping
- `TransformDeduplicateProcessByCourt` — one row per CNJ with highest
  `court_grade` and `first_court_*` fields from grade 1
- `TransformProcessInvolvedData`, `TransformPartyRole`,
  `TransformFirstCourtPolarity` — involved parties, role mapping, and
  first-instance polarity
- `escavador_api.utils.process` — `validate_process_number` and
  `format_process_number`
- Package export `EscavadorAPI` from `escavador_api`
- `test__transform` live API test scaffold

### Changed
- `EscavadorAPI` uses `fetch` mixins; `escavador_api.aux` removed
- `get`, `get_binary`, and `post` re-raise `ConnectionError` and
  `Timeout` so tenacity retries apply
- README documents transforms, CNJ length check, and runtime deps for
  the transform path

### Removed
- `escavador_api.aux` mixin package (replaced by `escavador_api.fetch`)

## [0.1.12] - 2026-10-26

### Added
- `ESCAVADOR_API__MAX_PAGES` on `escavador_api.config` — extra pages
  after the first response in `BaseMixin.fetch_paginated` (default
  200). Reaching the cap logs a warning and keeps items already
  fetched

### Changed
- README import path is `escavador_api.data.EscavadorAPI`
- README retry text matches GET and POST: 5 attempts, 3 seconds,
  `ConnectionError` and `Timeout`
- README lists `get_related_processes`, config variables (including
  `ESCAVADOR_API__MAX_PAGES`), generator returns, and the `loguru`
  import used for pagination warnings
- `ESCAVADOR_API__REQUEST_TIMEOUT` and `ESCAVADOR_API__MAX_PAGES`
  must be positive integers. A missing or blank value keeps the
  default. Any other value raises `ValueError` when
  `escavador_api.config` is imported
- Public docstrings and optional parameter types on `BaseMixin`,
  `ProcessMixin`, `get_related_processes`, and `EscavadorAPIException`

## [0.1.10] - 2026-10-22

### Added
- `get_related_processes` for processes linked to a CPF, CNPJ, or name
- `get_courts`
- `EscavadorAPIInvalidParametersException` and
  `EscavadorAPIAuthenticationError`
- `ESCAVADOR_API__REQUEST_TIMEOUT` and `ESCAVADOR_API__PROXY_URL`

### Changed
- Client implementation moved from `data.py` into mixins under
  `escavador_api.aux`
- `validate_process_number` is public
