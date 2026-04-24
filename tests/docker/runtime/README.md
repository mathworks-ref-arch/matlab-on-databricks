# Docker Tests: MATLAB Runtime Image

This suite validates the `matlab-runtime-on-databricks` Docker image.

It verifies base packages, users, runtime environment variables, and image
runtime metadata.

## Prerequisites

- Docker Desktop or Docker Engine
- Python dependencies from `tests/docker/requirements.txt`

## Required Configuration

Provide the following values via CLI args or environment variables:

- `IMAGE_NAME` or `--image-name` (for example `matlab-runtime-on-databricks:R2026a`)
- `MATLAB_RELEASE` or `--matlab-release` (for example `R2026a`)
- `DB_RUNTIME` or `--db-runtime` (for example `16.4`)

No MATLAB license is required for this suite.

## Running Tests

Using CLI args:

```bash
pytest tests/docker/runtime \
  --image-name="matlab-runtime-on-databricks:R2026a" \
  --matlab-release="R2026a" \
  --db-runtime="16.4"
```

Using environment variables:

```bash
export IMAGE_NAME="matlab-runtime-on-databricks:R2026a"
export MATLAB_RELEASE="R2026a"
export DB_RUNTIME="16.4"

pytest tests/docker/runtime
```

---------------

Copyright 2026 The MathWorks, Inc.
