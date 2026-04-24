# Docker Integration Tests

This suite runs higher-level integration checks against the MATLAB Docker image
by executing Python test functions inside the running container.

The tests validate behavior of modules in `resources/notebooks/mwhelpers/`
against a real containerized environment.

## What Is Tested

- `matlab` module behavior in-container
- `matlab_proxy` lifecycle behavior in-container
- `user` module user-creation behavior in-container

In-container test scripts are in `tests/docker/integration/python_tests/`.

## Prerequisites

- Docker Desktop or Docker Engine
- Python dependencies from `tests/docker/requirements.txt`
- A valid MATLAB license file

## Required Configuration

Provide the following values via CLI args or environment variables:

- `IMAGE_NAME` or `--image-name` (for example `matlab-on-databricks:R2026a`)
- `MATLAB_RELEASE` or `--matlab-release` (for example `R2026a`)
- `DB_RUNTIME` or `--db-runtime` (for example `16.4`)
- `MATLAB_LICENSE_FILE` (license file content)

## Running Tests

Using CLI args:

```bash
export MATLAB_LICENSE_FILE="$(cat /path/to/license.lic)"

pytest tests/docker/integration \
  --image-name="matlab-on-databricks:R2026a" \
  --matlab-release="R2026a" \
  --db-runtime="16.4"
```

Using environment variables:

```bash
export MATLAB_LICENSE_FILE="$(cat /path/to/license.lic)"
export IMAGE_NAME="matlab-on-databricks:R2026a"
export MATLAB_RELEASE="R2026a"
export DB_RUNTIME="16.4"

pytest tests/docker/integration
```

## Notes

- The suite mounts `resources/` and integration test files into the container as read-only volumes.
- `PYTHONPATH` is set to include both `/opt` (for `resources.notebooks.mwhelpers`) and `/opt/python_tests` (for direct test module imports).

---------------

Copyright 2026 The MathWorks, Inc.
