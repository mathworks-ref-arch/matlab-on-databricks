# Tests

This directory contains unit tests for the MATLAB on Databricks integration.

## Table of Contents

- [Unit Tests](#unit-tests)
  - [Shell Scripts](#shell-scripts)
  - [Python Scripts](#python-scripts)
- [Docker Tests](#docker-tests)

## Unit Tests

### Shell Scripts

Unit tests for shell scripts are located in `tests/unit/shell/` and use [Bats (Bash Automated Testing System)](https://github.com/bats-core/bats-core).

#### Prerequisites

To run tests and linting locally, you will need:

- [Bats](https://bats-core.readthedocs.io/en/stable/installation.html)
- [Pre-commit](https://pre-commit.com/#install) (manages linters)
- [ShellCheck](https://github.com/koalaman/shellcheck#installing) (managed via pre-commit, but useful to have installed)
- [shfmt](https://github.com/mvdan/sh) (managed via pre-commit)

#### Local Setup

The tests rely on helper libraries (`bats-support` and `bats-assert`). You must download these libraries and configure your environment to locate them.

1. **Create a directory for Bats libraries:**

    ```bash
    mkdir -p .bats
    ```

2. **Clone the required libraries:**

    ```bash
    git clone https://github.com/bats-core/bats-support.git .bats/bats-support
    git clone https://github.com/bats-core/bats-assert.git .bats/bats-assert
    ```

#### Running Tests

To run the tests, you must set the `SOURCE_SCRIPTS_DIR` environment variable to point to the scripts being tested, and `BATS_LIB_PATH` to point to the directory containing the helper libraries.

Run the following command from the root of the repository:

```bash
SOURCE_SCRIPTS_DIR="$(pwd)/resources/notebooks/mwhelpers/scripts" \
BATS_LIB_PATH="$(pwd)/.bats" \
bats tests/unit/shell/
```

#### Linting

This project uses `pre-commit` to ensure code quality. This runs `shellcheck` and `shfmt` with the specific configurations defined in `.pre-commit-config.yaml`.

**Install the git hooks:**

```bash
pre-commit install
```

**Run linters manually on all files:**

```bash
pre-commit run --all-files
```

#### Developing Tests

- **Location:** Add new shell script tests to `tests/unit/shell/`.
- **Naming:** Test files should end with `.bats`.
- **Structure:**
  - Use `setup_file()` and `teardown_file()` for environment preparation.
  - Use mocks to isolate tests from the actual system.
  - Ensure `SOURCE_SCRIPTS_DIR` is used when loading the script under test.

### Python Scripts

Unit tests for Python scripts are located in `tests/unit/python/` and use [pytest](https://docs.pytest.org/).

#### Prerequisites

To run tests locally, you will need:

- Python 3.11
- Dependencies listed in `tests/unit/python/requirements.txt`

#### Local Setup

Install the required Python dependencies:

```bash
python3 -m pip install -r tests/unit/python/requirements.txt
```

#### Running Tests

To run the tests and generate a coverage report:

```bash
python3 -m pytest --cov=resources/notebooks/ tests/unit/python
```

#### Linting

Python code is linted and formatted using [Ruff](https://docs.astral.sh/ruff/), managed via `pre-commit`.

**Run linters manually:**

```bash
pre-commit run --all-files
```

#### Developing Tests

- **Location:** Add new Python tests to `tests/unit/python/`.
- **Naming:** Test files should start with `test_`.
- **Structure:**
  - Use `pytest` fixtures for setup.
  - Use `pytest-mock` (the `mocker` fixture) to mock external dependencies.

## Docker Tests

Integration tests for the Docker images are located in `tests/docker/`.
These tests use [Testinfra](https://testinfra.readthedocs.io/) and [pytest](https://docs.pytest.org/) to verify the built images.

### Prerequisites

- Docker Desktop or Engine.
- A valid MATLAB License file (required for licensing MATLAB inside `matlab` image).

### Local Setup

Install the required Python dependencies for Docker testing:

```bash
python3 -m pip install -r tests/docker/requirements.txt
```

### Configuration

To run the tests, you must provide the target image and version details. These can be specified via **Command Line Arguments** or **Environment Variables**.

| CLI Argument | Environment Variable | Description |
| :--- | :--- | :--- |
| `--image-name` | `IMAGE_NAME` | The full tag of the Docker image to test (e.g., `matlab-on-databricks:R2025b`). |
| `--matlab-release` | `MATLAB_RELEASE` | The MATLAB release version (e.g., `R2025b`). |
| `--db-runtime` | `DB_RUNTIME` | The Databricks Runtime version (e.g., `16.4`). |

### Running Tests

The tests are split into two categories: `matlab` (MATLAB) and `runtime` (MATLAB Runtime).

#### 1. Testing the MATLAB Image

> [!IMPORTANT]
> To license MATLAB, you must provide the content of a valid license via the `MATLAB_LICENSE_FILE` environment variable.

*Using CLI Arguments:*

```bash
export MATLAB_LICENSE_FILE=$(cat /path/to/license.lic)

pytest tests/docker/matlab \
    --image-name="matlab-on-databricks:R2025b" \
    --matlab-release="R2025b" \
    --db-runtime="16.4"
```

*Using Environment Variables:*

```bash
export MATLAB_LICENSE_FILE=$(cat /path/to/license.lic)
export IMAGE_NAME="matlab-on-databricks:R2025b"
export MATLAB_RELEASE="R2025b"
export DB_RUNTIME="16.4"

pytest tests/docker/matlab
```

#### Testing the Runtime Image

The Runtime image does not require a license file.

```bash
pytest tests/docker/runtime \
    --image-name="matlab-runtime-on-databricks:R2025b" \
    --matlab-release="R2025b" \
    --db-runtime="16.4"
```

### Linting

Dockerfiles are linted using [Hadolint](https://github.com/hadolint/hadolint), managed via `pre-commit`.

```bash
pre-commit run hadolint-docker --all-files
```

### Developing Tests

- **Location:** `tests/docker/matlab/` or `tests/docker/runtime/`.
- **Naming:** Test files should start with `test_`.
- **Structure:**
  - Use `testinfra` to execute commands inside the running container.

---------------

Copyright 2026 The MathWorks, Inc.

---------------
