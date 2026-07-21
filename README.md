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
Import `EscavadorAPI`, pass an Escavador auth token, and call methods for
process lookup, documents, updates, monitoring, and credits. Typical
consumers are ETL workers and internal tools that need structured process
data.

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
- **Credit Management**: Check API usage credits and limits
- **Court Data Refresh**: Request fresh data updates from court sources
- **Retry Logic**: Automatic retry with 5-second delays for network
  failures (max 5 retries)

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

## Quick Start

```python
from escavador_api import EscavadorAPI

# Initialize with your API token
api = EscavadorAPI("your_auth_token_here")

# Check credit balance
balance = api.get_credit_balance()
print(balance)

# Get process information
process_info = api.get_process_info("12345678901234567890")
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
get_process_updates(process_number: str) -> list
```
Get all updates for a process. **(paid)**

```python
get_process_public_documents(process_number: str) -> list
```
Get publicly available documents. **(paid)**

```python
get_process_all_documents(process_number: str) -> list
```
Get all documents (public and restricted, if authorized). **(paid)**

#### Process Updates

```python
request_process_update_public(process_number: str) -> dict
```
Request update of public process information. **(paid)**

```python
request_process_update_full(
    process_number: str,
    auth_username: str = None,
    auth_password: str = None,
    certificate_id: int = None,
    use_certificate: bool = False
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

### Monitoring

#### New Process Monitoring

```python
create_monitoring_new_process(
    keyword: str,
    keyword_variations: list[str] = None,
    aux_keywords: list[KeywordDict] = None,
    courts: list[str] = None
) -> dict
```
Create monitoring for new processes matching criteria.

```python
list_monitoring_new_process() -> list
```
List all new process monitorings.

```python
get_monitoring_new_process(monitoring_id: int) -> dict
```
Get details of a specific monitoring.

```python
edit_monitoring_new_process(
    monitoring_id: int,
    keyword_variations: list[str] = None,
    aux_keywords: list[KeywordDict] = None,
    courts: list[str] = None
) -> dict
```
Edit an existing monitoring.

```python
delete_monitoring_new_process(monitoring_id: int) -> bool
```
Delete a monitoring.

```python
get_results_monitoring_new_process(monitoring_id: int) -> list
```
Get results from a monitoring.

#### Existing Process Monitoring

```python
create_monitoring_existing_process(
    process_number: str,
    court: str = None,
    frequency: str = None
) -> dict
```
Monitor updates to an existing process.

```python
list_monitoring_existing_process() -> list
```
List existing process monitorings.

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

- `EscavadorAPIInvalidDocumentException`: Invalid process number format
- `EscavadorAPIProblemAPIException`: API-specific errors (authentication,
  insufficient credits, etc.)
- `EscavadorAPIUnmappedErrorException`: Unexpected errors or network
  issues

## Retry Logic

All API calls include automatic retry logic:

- **Maximum retries**: 5 attempts
- **Retry delay**: 5 seconds between attempts
- **Retry conditions**: Network errors (connection failures, timeouts,
  chunked encoding errors)
- **Non-retryable errors**: Validation errors, HTTP errors (4xx/5xx),
  and API-specific exceptions

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
pytest

# Build package
./build.sh
```

### Testing

Tests require environment variables:

- `ESCAVADOR_AUTH_TOKEN`: Your API token
- `TEST_PROCESS_NUMBER`: A valid CNJ process number for testing

```bash
export ESCAVADOR_AUTH_TOKEN="your_token"
export TEST_PROCESS_NUMBER="process_number"
pytest
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
