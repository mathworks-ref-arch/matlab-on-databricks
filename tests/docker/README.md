# Docker Tests

This directory contains pytest-based tests for Docker images used by this
project.

The tests use [pytest](https://docs.pytest.org/) and
[Testinfra](https://testinfra.readthedocs.io/) to validate container
configuration and behavior.

## Suites

- [MATLAB image tests](./matlab/README.md)
- [MATLAB Runtime image tests](./runtime/README.md)
- [Docker integration tests](./integration/README.md)

## Prerequisites

- Docker Desktop or Docker Engine
- Python 3.11+

For MATLAB image tests and Docker integration tests, also provide a valid MATLAB
license file via `MATLAB_LICENSE_FILE`.

## Local Setup

Install Python dependencies from repository root:

```bash
python3 -m pip install -r tests/docker/requirements.txt
```

## Shared Configuration

Tests in this folder accept configuration from either CLI args or environment
variables.

| CLI Argument | Environment Variable | Description |
| :--- | :--- | :--- |
| `--image-name` | `IMAGE_NAME` | Full Docker image tag to test. |
| `--matlab-release` | `MATLAB_RELEASE` | MATLAB release (for example `R2026a`). |
| `--db-runtime` | `DB_RUNTIME` | Databricks Runtime version (for example `16.4`). |
| `--matlab-update` | `MATLAB_UPDATE` | Optional MATLAB update level (for example `U7`). |

Example with environment variables:

```bash
export IMAGE_NAME="matlab-on-databricks:R2026a"
export MATLAB_RELEASE="R2026a"
export DB_RUNTIME="16.4"
```

## Running Tests

> [!NOTE]
> Do not run `pytest tests/docker` as a single command. The suites target different images and require different configuration contexts.

Run each suite separately. If you want to run all Docker suites locally,
execute them sequentially and set the appropriate `IMAGE_NAME` for each run:

```bash
# MATLAB image suite
export MATLAB_LICENSE_FILE="$(cat /path/to/license.lic)"
export IMAGE_NAME="matlab:R2026a-17.3"
export MATLAB_RELEASE="R2026a"
export DB_RUNTIME="17.3"
pytest tests/docker/matlab

# Runtime image suite
export IMAGE_NAME="runtime:R2026a-17.3"
pytest tests/docker/runtime

# Integration suite (MATLAB image)
export IMAGE_NAME="matlab:R2026a-17.3"
pytest tests/docker/integration
```

---------------

Copyright 2026 The MathWorks, Inc.
