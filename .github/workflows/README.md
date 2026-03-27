# MATLAB on Databricks CI/CD Workflows

This directory contains the GitHub Actions workflows used to build, test, and release Docker images for **MATLAB on Databricks**.

The pipeline follows a **Build-Test-Promote** architecture to ensure that the image released to production is identical to the image that passed all tests.

## Workflows

| Workflow File | Description |
| :--- | :--- |
| **`schedule.yml`** | Defines the build matrix (MATLAB releases vs. Databricks Runtimes) and triggers the pipeline on push, schedule, or manual dispatch. |
| **`ci.yml`** | Complete build, test, stage and promote workflow. It ensures the publish job only runs if the build job succeeds. |
| **`build-test-stage.yml`** | Builds the Docker image, runs local tests (using `pytest`), and pushes a temporary "test" tag (e.g., `test-matlab:R2025b-16.4`) to the registry. |
| **`promote.yml`** | Performs a **Server-Side Retag**. It takes the "test" tag (e.g., `test-matlab:R2025b-16.4`) and creates the production tag (e.g., `matlab:R2025b-16.4`) without rebuilding the image. |
| **`run-unit-tests.yml`** | Executes unit tests for python and shell scripts to ensure code correctness. |
| **`lint.yml`** | Runs static analysis on PRs to ensure code quality. |

## Triggers and Scheduled Jobs

- **Weekly Build:** The `schedule` workflow runs every Monday at 00:00 UTC.
- **Push Events**: Triggered when you push changes to directories with Dockerfiles or workflow files.
- **Manual Dispatch:** Can be triggered manually from the GitHub "Actions" tab.

---------------

Copyright 2026 The MathWorks, Inc.

---------------
