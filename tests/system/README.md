# System Tests

This directory contains end-to-end system tests that deploy a MATLAB Docker image
to a Databricks workspace and run verification jobs on a live cluster.

**Note:** These tests apply only to MATLAB Docker images (custom container images that include a full MATLAB installation).

Tests use [Databricks Asset Bundles (DABs)](https://docs.databricks.com/en/dev-tools/bundles/index.html)
to provision infrastructure, execute notebook tasks, and tear down resources.

## What Is Tested

- License verification on the cluster
- Installation of the MATLAB interface for Databricks
- MATLAB test execution in-cluster (via MATLAB Engine for Python)

## MATLAB Engine & Python Compatibility

The system tests use [MATLAB Engine for Python](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html) to connect to a shared MATLAB session. The Engine must be compatible with the Python version bundled in the Databricks Runtime (DBR).

**R2024a is incompatible** with both DBR 16.4 and 17.3 because its MATLAB Engine does not support Python 3.12. For more information, see <https://mathworks.com/support/requirements/python-compatibility.html>.

## Prerequisites

- [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/install.html)
- A Databricks workspace with valid credentials (personal access token, OAuth,
  or CLI profile for local runs; service principal for CI)
- A Docker image pushed to a registry accessible from the workspace
- A MATLAB license uploaded to Databricks secrets (scope: `matlab`, key: `license`)

## Required Configuration

Provide the following values via environment variables:

| Environment Variable | Description |
| :--- | :--- |
| `DATABRICKS_HOST` | Databricks workspace URL |
| `DATABRICKS_CLIENT_ID` | Service principal client ID |
| `DATABRICKS_CLIENT_SECRET` | Service principal OAuth secret |
| `BUNDLE_VAR_docker_image` | Full Docker image URL (e.g., `ghcr.io/org/repo/matlab:R2026a-17.3`) |
| `BUNDLE_VAR_docker_username` | Username for image pull authentication (e.g., `github.actor`) |
| `BUNDLE_VAR_docker_password` | Token for image pull authentication (e.g., `GITHUB_TOKEN`) |

Optional:

| Environment Variable | Description |
| :--- | :--- |
| `BUNDLE_VAR_matlab_release` | MATLAB release (defaults to `R2026a`) |
| `BUNDLE_VAR_databricks_runtime` | Databricks Runtime version (defaults to `17.3`) |
| `BUNDLE_VAR_node_type_id` | Cloud-specific node type (defaults to `Standard_DS3_v2`) |
| `BUNDLE_VAR_run_id` | Unique identifier for the deployment (e.g., CI run ID) |
| `MATLAB_LICENSE` | MATLAB license file content (for `upload-license` target) |

## Running Tests

Run the full pipeline (deploy, test, destroy):

```bash
make all
```

Run individual stages:

```bash
make deploy     # Deploy DAB bundle (creates job + cluster)
make test       # Run verification job on Databricks
make destroy    # Tear down all DAB resources
```

Upload a MATLAB license to Databricks secrets:

```bash
export MATLAB_LICENSE="$(cat /path/to/license.lic)"
make upload-license
```

## Notes

- The `node_type_id` bundle variable defaults to Azure (`Standard_DS3_v2`); override for other clouds.
- The `destroy` target always runs in CI to avoid leaving resources behind, even when tests fail.
- Bundle variables are passed via the `BUNDLE_VAR_<name>` convention; the Databricks CLI maps these to bundle variables automatically.

---------------

Copyright 2026 The MathWorks, Inc.

---------------
