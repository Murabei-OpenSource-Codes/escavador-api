# Changelog

All notable changes to this package are documented here.

The format is based on Keep a Changelog. The version is the package
tag produced by `build.sh` (beta tags on branches other than `main`).
Entries start at `0.1.10`. Older tags remain in git only.

## [0.1.20] - 2026-11-16

### Added
- `ROLE_MAPPING_DEFAULT` — lawyer / `neutral`: `advogado_procurador`,
  `defensor`
- `ROLE_MAPPING_DEFAULT` — active: `assistente_de_acusacao`, `consulente`,
  `interpelante`, `consignante`, `corrigente`, `relatante`,
  `representante_notificante`; `terceiro_depositante`
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
