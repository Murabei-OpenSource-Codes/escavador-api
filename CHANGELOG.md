# Changelog

All notable changes to this package are documented here.

The format is based on Keep a Changelog. The version is the package
tag produced by `build.sh` (beta tags on branches other than `main`).
Entries start at `0.1.10`. Older tags remain in git only.

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
