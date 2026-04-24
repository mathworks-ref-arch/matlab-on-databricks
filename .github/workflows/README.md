# MATLAB on Databricks CI/CD Workflows

This directory contains the GitHub Actions workflows used to build, test, and release Docker images for **MATLAB on Databricks**.

The CI/CD setup is split into lightweight orchestration workflows and reusable workflows.

- **PR validation:** Runs code quality checks and only the required test/build jobs based on changed paths.
- **Release:** Builds matrix images, runs docker and integration tests, then promotes tested images to GHCR. Triggered by version tags, weekly schedule, or manual dispatch.
- **Manual validation:** Allows targeted developer-triggered build/test checks for a specific image config.

## Workflows

| Workflow File | Description |
| :--- | :--- |
| **`dev-pr.yml`** | Private-repo PR checks with path-based routing. Runs only relevant jobs and cancels stale runs on newer PR commits. |
| **`dev-manual.yml`** | Manual private-repo validation for build, build-and-test, or test scenarios. |
| **`run-precommit.yml`** | Reusable `pre-commit` workflow. |
| **`run-unit-tests.yml`** | Reusable shell and python unit tests for `mwhelpers`. |
| **`run-integration-tests.yml`** | Reusable integration tests workflow for `mwhelpers` against a Docker image pulled from GHCR. |
| **`docker-pipeline.yml`** | Reusable single-job workflow that builds a Docker image, runs docker and integration tests, and optionally promotes to GHCR. |
| **`release-public.yml`** | Release workflow triggered by version tags, weekly schedule, or manual dispatch. Runs full image matrix build, test, and promote. |

---------------

Copyright 2026 The MathWorks, Inc.

---------------
