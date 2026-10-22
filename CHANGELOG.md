# Changelog

All notable changes to this package are documented here.

The format is based on Keep a Changelog. The version is the package
tag produced by `build.sh` (beta tags on branches other than `main`).
Entries start at `0.1.10-b.0`. Older tags remain in git only.

## [0.1.12-b.0] - 2026-10-22

### Changed
- README import path is `escavador_api.data.EscavadorAPI`
- README retry text matches GET and POST: 5 attempts, 3 seconds,
  `ConnectionError` and `Timeout`
- README lists `get_related_processes`, config variables, and generator
  returns from paginated process and monitoring methods

## [0.1.11-b.0] - 2026-10-22

### Changed
- Public docstrings and optional parameter types on `BaseMixin`,
  `ProcessMixin`, `get_related_processes`, and `EscavadorAPIException`

## [0.1.10-b.0] - 2026-10-22

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
