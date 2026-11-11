# Changelog

All notable changes to this package are documented here.

The format is based on Keep a Changelog. The version is the package
tag produced by `build.sh` (beta tags on branches other than `main`).
Entries start at `0.1.10`. Older tags remain in git only.

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
