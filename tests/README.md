# Tests

This directory contains automated test suites for MATLAB on Databricks.

Use this README as an index, then follow the suite-specific README for setup,
execution commands, and development guidelines.

## Table of Contents

- [Test Suites](#test-suites)
- [Shared Linting](#shared-linting)

## Test Suites

### Unit Tests

- [Shell unit tests (`tests/unit/shell/`)](./unit/shell/README.md)
- [Python unit tests (`tests/unit/python/`)](./unit/python/README.md)

### Docker Tests

- [Docker tests overview (`tests/docker/`)](./docker/README.md)
- [MATLAB image tests (`tests/docker/matlab/`)](./docker/matlab/README.md)
- [MATLAB Runtime image tests (`tests/docker/runtime/`)](./docker/runtime/README.md)
- [Docker integration tests (`tests/docker/integration/`)](./docker/integration/README.md)

### System Tests

- [System tests (`tests/system/`)](./system/README.md)

## Shared Linting

This repository uses `pre-commit` to run linters and formatters across test code.

Install hooks:

```bash
pre-commit install
```

Run all configured checks manually:

```bash
pre-commit run --all-files
```

---------------

Copyright 2026 The MathWorks, Inc.

---------------
