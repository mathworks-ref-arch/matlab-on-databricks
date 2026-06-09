# Create MATLAB Runtime Container Image for Databricks

Use this guide to build and customize a Docker&reg; container for using MATLAB&reg; Runtime in Databricks.

You require MATLAB Runtime to run libraries compiled with MATLAB&reg; Compiler&trade;,
MATLAB&reg; Compiler SDK&trade; or Simulink&reg; Compiler&trade;.

By default, the [Dockerfile](./Dockerfile) in this folder:

1. Builds a base image of [databricksruntime/standard:17.3-LTS](https://hub.docker.com/r/databricksruntime/standard/tags).
2. Installs MATLAB Runtime for R2026a.
3. Installs required 3rd party dependencies for MATLAB Runtime.

## Requirements

- Docker

## Build Instructions

### Get Sources

Access the Dockerfile either by directly downloading this repository from GitHub&reg;,
or by cloning this repository and then navigating to the appropriate folder.

```bash
git clone https://github.com/mathworks-ref-arch/matlab-on-databricks.git
cd matlab-on-databricks/resources/dockerfiles/runtime
```

### Build Docker Image

Build container with a name and tag of your choice.

```bash
docker build -t matlab/databricks/runtime:r2026a-dbx17.3 --build-arg MATLAB_UPDATE=2 .
```

To customize your Docker image, you can specify  arguments with the `docker build` command or by directly modifying the [Dockerfile](../runtime/Dockerfile).

| Argument Name | Default value | Description |
| --- | --- | --- |
| DATABRICKS_RUNTIME_VERSION | 17.3 | A valid LTS [Databricks Runtime Version](https://docs.databricks.com/aws/en/release-notes/runtime/). Also see [Databricks Runtime tags on Dockerhub](https://hub.docker.com/r/databricksruntime/standard/tags). |
| MATLAB_RELEASE | R2026a | MATLAB release to install, for example, `R2024b`. |
| MATLAB_UPDATE | *unset* | The update to install for a given MATLAB release (for example, `U1` for update 1 of the specified `MATLAB_RELEASE`). If left unset, it defaults to the initial release (U0). It is recommended to check for the latest available update by referencing the filename of the Linux version of the runtime download. See [MATLAB Runtime Download](https://www.mathworks.com/products/compiler/matlab-runtime.html). |

Example:

```bash
# Build docker image for MATLAB R2024b and Databricks 15.4
docker build \
    -t "matlab/databricks/runtime:r2024b-dbx15.4" \
    --build-arg MATLAB_RELEASE=R2024b \
    --build-arg DATABRICKS_RUNTIME_VERSION="15.4" \
    --build-arg MATLAB_DEPS_URL="https://raw.githubusercontent.com/mathworks-ref-arch/container-images/refs/heads/main/matlab-deps/r2024b/ubuntu22.04/base-dependencies.txt" \
    --build-arg MATLAB_RUNTIME_URL="https://ssd.mathworks.com/supportfiles/downloads/R2024b/Release/6/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2024b_Update_7_glnxa64.zip" \
    --build-arg UBUNTU_VERSION="22.04" \
    -f Dockerfile .
```

----
Copyright 2026 The MathWorks, Inc.
