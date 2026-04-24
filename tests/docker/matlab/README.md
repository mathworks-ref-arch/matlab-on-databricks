# Docker Tests: MATLAB Image

This suite validates the `matlab-on-databricks` Docker image.

It includes checks for:

- system/user setup inside the container
- MATLAB installation and release/update metadata
- MATLAB licensing behavior
- MATLAB Proxy environment and startup
- MathWorks Service Host (MSH) behavior

## Prerequisites

- Docker Desktop or Docker Engine
- Python dependencies from `tests/docker/requirements.txt`
- A valid MATLAB license file

## Required Configuration

Provide the following values via CLI args or environment variables:

- `IMAGE_NAME` or `--image-name` (for example `matlab-on-databricks:R2026a`)
- `MATLAB_RELEASE` or `--matlab-release` (for example `R2026a`)
- `DB_RUNTIME` or `--db-runtime` (for example `16.4`)
- `MATLAB_LICENSE_FILE` (license file content, not a path)

Optional:

- `MATLAB_UPDATE` or `--matlab-update` (for update-level assertion, for example `U7`)

## Running Tests

From the repository root, using CLI args:

```bash
export MATLAB_LICENSE_FILE="$(cat /path/to/license.lic)"

pytest tests/docker/matlab \
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

pytest tests/docker/matlab
```

Run a single test file:

```bash
pytest tests/docker/matlab/test_matlab.py \
  --image-name="matlab-on-databricks:R2026a" \
  --matlab-release="R2026a" \
  --db-runtime="16.4"
```

---------------

Copyright 2026 The MathWorks, Inc.
