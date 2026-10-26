# escavador-api

A Python library for interacting with the Escavador API, providing access
to Brazilian legal process data, documents, and monitoring services.

## Objective and motivation

Python client for the Escavador HTTP API: Brazilian legal process data,
documents, AI summaries and monitoring services.

### Why this exists
Escavador exposes court and process endpoints over HTTP with auth tokens
and credit billing. This library wraps those calls with CNJ validation,
pagination, retries, and typed exceptions so Murabei (and other) services
do not reimplement the same client logic.

### How it is used
Import `EscavadorAPI` from `escavador_api.data`, pass an Escavador auth
token, and call methods for process lookup, documents, updates,
monitoring, related parties, and credits. Typical consumers are ETL
workers and internal tools that need structured process data.

### Scope
In scope: Escavador REST client behavior (requests, retries, error
mapping). Out of scope: Escavador account management, credit purchase,
and downstream storage or ETL orchestration.

## Features

- **Process Information**: Retrieve detailed information about legal
  processes using CNJ numbers
- **Process Updates**: Get chronological update history of legal processes
- **Court Listing**: List available courts for searches
- **Document Access**: Download public and restricted process documents
- **AI Summaries**: Generate and retrieve AI-powered process summaries
- **Process Monitoring**: Set up monitoring for new processes or updates
  to existing processes
- **Related Processes**: List processes linked to a person or a company
  by CPF, CNPJ, or name
- **Credit Management**: Check API usage credits and limits
- **Court Data Refresh**: Request fresh data updates from court sources
- **Retry Logic**: GET and POST retry connection errors and timeouts
  (5 attempts, 3 seconds apart)
- **Pagination cap**: Paginated calls fetch the first page, then at
  most `ESCAVADOR_API__MAX_PAGES` further pages (default 200)

## Installation

### From Source

```bash
git clone https://github.com/Murabei-OpenSource-Codes/escavador-api.git
cd escavador-api
pip install .
```

## Requirements

- Python >= 3.12
- requests >= 2.32.5
- tenacity >= 9.1.4
- loguru (pagination warnings in `BaseMixin.fetch_paginated`)

## Configuration

Read when `escavador_api.config` is imported (the first import of
`EscavadorAPI`). Later environment changes apply only after the
process restarts.

- `ESCAVADOR_API__REQUEST_TIMEOUT`: request timeout in seconds.
  Defaults to 60.
- `ESCAVADOR_API__PROXY_URL`: proxy URL for HTTP and HTTPS. If unset,
  no proxy is used.
- `ESCAVADOR_API__MAX_PAGES`: extra pages after the first response
  on paginated calls. Defaults to 200. The first page is always
  requested. Hitting the cap logs a warning and keeps items already
  fetched.

`ESCAVADOR_API__REQUEST_TIMEOUT` and `ESCAVADOR_API__MAX_PAGES` must
be positive integers. A missing or blank value keeps the default.
Any other value raises `ValueError` at import.

Paginated calls are `get_process_updates`,
`get_process_public_documents`, `get_process_all_documents`,
`get_related_processes`, `list_monitoring_new_process`,
`get_results_monitoring_new_process`, and
`list_monitoring_existing_process`.

The auth token is an argument of `EscavadorAPI`. The library does not
read it from the environment.

## Quick Start

```python
from escavador_api.data import EscavadorAPI

# Initialize with your API token
api = EscavadorAPI("your_auth_token_here")

# Check credit balance
balance = api.get_credit_balance()
print(balance)

# Get process information. The number must be a valid CNJ.
process_info = api.get_process_info("00000016620260000001")
print(process_info)
```

## API Reference

### Initialization

```python
EscavadorAPI(escavador_auth_token: str)
```

**Parameters:**
- `escavador_auth_token` (str): Your Escavador API authentication token

### Core Methods

Methods marked **(paid)** consume Escavador API credits.

#### Credit Management

```python
get_credit_balance() -> dict
```
Returns current credit balance and monthly limits.

#### Courts

```python
get_courts() -> dict
```
List all available courts for searches in Escavador.

#### Process Information

```python
get_process_info(process_number: str) -> dict
```
Retrieve basic process information. **(paid)**

**Parameters:**
- `process_number` (str): CNJ process number (20 digits, punctuation
  optional)

```python
get_process_updates(process_number: str)
```
Yields one dictionary per process update. **(paid)**

```python
get_process_public_documents(process_number: str)
```
Yields one dictionary per public document. **(paid)**

```python
get_process_all_documents(process_number: str)
```
Yields one dictionary per document, including restricted documents
when the caller is authorized. **(paid)**

#### Process Updates

```python
request_process_update_public(process_number: str) -> dict
```
Request update of public process information. **(paid)**

```python
request_process_update_full(
    process_number: str,
    auth_username: str | None = None,
    auth_password: str | None = None,
    certificate_id: int | None = None,
    use_certificate: bool = False,
) -> dict
```
Request full update including restricted documents. **(paid)**

```python
get_process_update_status(process_number: str) -> dict
```
Check the status of an update request. **(paid)**

#### Document Downloads

```python
download_process_file(process_number: str, file_key: str) -> bytes
```
Download a specific document as PDF bytes. **(paid)**

#### AI Summaries

```python
request_ai_summary(process_number: str) -> dict
```
Request generation of an AI summary. **(paid)**

```python
get_ai_summary_status(process_number: str) -> dict
```
Check AI summary generation status.

```python
get_ai_summary(process_number: str) -> dict
```
Retrieve the generated AI summary. **(paid)**

### Related processes

```python
get_related_processes(
    cpf_cnpj: str | None = None,
    nome: str | None = None,
    ordena_por: str = "data_inicio",
    ordem: str = "desc",
    limit: Literal[20, 50, 100] = 100,
    tribunais: list[str] | None = None,
    incluir_homonimos: bool | None = None,
    incluir_mesma_raiz_cnpj: bool | None = None,
    polo: Literal["ATIVO", "PASSIVO", "ADVOGADO", "OUTROS"] | None = None,
    status: Literal["ATIVO", "INATIVO"] | None = None,
    data_minima: str | None = None,
    data_maxima: str | None = None,
    assuntos_codigos_cnj: list[int] | None = None,
    classes_codigos_cnj: list[int] | None = None,
    materias_codigos_cnj: list[int] | None = None,
    valor_causa_minimo: float | None = None,
    valor_causa_maximo: float | None = None,
    envolvidos_relacionados: list[str] | None = None,
) -> list[dict]
```

List processes for a person or a company. `cpf_cnpj` or `nome` is
required. Other arguments are optional filters. Raises
`EscavadorAPIInvalidParametersException` when both identifiers are
missing.

### Monitoring

#### New Process Monitoring

```python
create_monitoring_new_process(
    keyword: str,
    keyword_variations: list[str] | None = None,
    aux_keywords: list[KeywordDict] | None = None,
    courts: list[str] | None = None,
) -> dict
```
Create monitoring for new processes matching criteria.

```python
list_monitoring_new_process()
```
Yields one dictionary per new-process monitoring.

```python
get_monitoring_new_process(monitoring_id: int) -> dict
```
Get details of a specific monitoring.

```python
edit_monitoring_new_process(
    monitoring_id: int,
    keyword_variations: list[str] | None = None,
    aux_keywords: list[KeywordDict] | None = None,
    courts: list[str] | None = None,
) -> dict
```
Edit an existing monitoring.

```python
delete_monitoring_new_process(monitoring_id: int) -> bool
```
Delete a monitoring.

```python
get_results_monitoring_new_process(monitoring_id: int)
```
Yields one dictionary per process found by the monitoring.

#### Existing Process Monitoring

```python
create_monitoring_existing_process(
    process_number: str,
    court: str | None = None,
    frequency: str | None = None,
) -> dict
```
Monitor updates to an existing process.

```python
list_monitoring_existing_process()
```
Yields one dictionary per existing-process monitoring.

```python
get_monitoring_existing_process(monitoring_id: int) -> dict
```
Get monitoring details.

```python
delete_monitoring_existing_process(monitoring_id: int) -> bool
```
Delete monitoring.

## Error Handling

The library provides specific exception types:

- `EscavadorAPIException`: Base error. Carries `message` and `payload`.
- `EscavadorAPIAuthenticationError`: The auth token is empty.
- `EscavadorAPIInvalidDocumentException`: The process number is not a
  valid CNJ number.
- `EscavadorAPIInvalidParametersException`: A call is missing a required
  argument, such as both `cpf_cnpj` and `nome`.
- `EscavadorAPIProblemAPIException`: The Escavador API returned an HTTP
  error, or a monitoring call failed local checks.
- `EscavadorAPIUnmappedErrorException`: An unexpected error during a
  request.

## Retry Logic

`get`, `get_binary`, and `post` retry network failures. `delete` and
`patch` do not.

- **Attempts**: 5 (`stop_after_attempt`)
- **Delay**: 3 seconds between attempts
- **Retried errors**: `requests.ConnectionError` and `requests.Timeout`
- **Not retried**: Validation errors and HTTP error responses

## Process Number Format

Process numbers must follow the Brazilian CNJ
(Conselho Nacional de Justiça) format:

- 20 digits total
- Format: NNNNNNN-DD.AAAA.J.TR.OOOO

The library automatically validates process numbers and accepts them
with or without punctuation.

## Authentication

To use the Escavador API, you need:

1. An Escavador account
2. An API authentication token
3. Sufficient credits for API calls

For restricted documents, additional authentication may be required
(username/password or digital certificate).

## Development

### Setup

```bash
# Install dependencies
pip install -e .

# Run tests
python -m unittest discover -s src/escavador_api/tests

# Build package
./build.sh
```

### Testing

Tests use `unittest` and call the live Escavador API. Set:

- `ESCAVADOR_AUTH_TOKEN`: API token passed into `EscavadorAPI`
- `TEST_PROCESS_NUMBER`: A valid CNJ number for process tests
- `TEST_CPF_NUMBER`: A CPF for related-process tests

```bash
export ESCAVADOR_AUTH_TOKEN="your_token"
export TEST_PROCESS_NUMBER="process_number"
export TEST_CPF_NUMBER="cpf"
python -m unittest discover -s src/escavador_api/tests
```

## License

BSD 3-Clause License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:

- Check the [Escavador API documentation](https://api.escavador.com/)
- Open an issue on GitHub
- Contact Murabei Data Science at a.baceti@murabei.com
