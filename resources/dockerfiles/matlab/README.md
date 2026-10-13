# Create MATLAB Container Image for Databricks

Use this guide to build and customize a Docker&reg; container for using the MATLAB&reg; desktop and its toolboxes in Databricks environments.

By default, the [Dockerfile](./Dockerfile) in this folder:

1. Builds a base image using [Databricksruntime/Standard:17.3-LTS (Docker Hub)](https://hub.docker.com/r/databricksruntime/standard/tags).
2. Installs MATLAB, MATLAB dependencies, and Database_Toolbox for R2026b.
3. Installs Python packages for [matlab-proxy](https://github.com/mathworks/matlab-proxy) & [matlabengine](https://github.com/mathworks/matlab-engine-for-python).

- Docker

## Build Instructions

### Get Sources

Access the Dockerfile either by directly downloading this repository from GitHub&reg;,
or by cloning this repository and then navigating to the appropriate folder.

```bash
git clone https://github.com/mathworks-ref-arch/matlab-on-databricks.git
cd matlab-on-databricks/resources/dockerfiles/matlab
```

### Build and Run Docker Image

Build container with a name and tag of your choice.

```bash
docker build -t matlab/databricks/desktop:R2026b-dbx17.3 .
```

Execute the following to test the built image locally:

```bash
docker run -it --rm -p 8888:8888 -u ubuntu --entrypoint /databricks/python3/bin/matlab-proxy-app matlab/databricks/desktop:R2026b-dbx17.3

# Click on the printed URL on the terminal to launch the MATLAB Desktop in your browser
```

## Customize the Image

By default, this [Dockerfile](../../../resources/dockerfiles/matlab/Dockerfile) installs the latest available MATLAB release as well as `Database_Toolbox`, but no other toolboxes or products, in the `/opt/matlab/${MATLAB_RELEASE}` folder.

Use the options below to customize your build.

### Customize MATLAB Release, MATLAB Product List, MATLAB Install Location, and License Server

The [Dockerfile](../../../resources/dockerfiles/matlab/Dockerfile) supports these Docker build-time variables:

| Argument Name | Default value | Description |
| --- | --- | --- |
| DATABRICKS_RUNTIME_VERSION | 17.3 | A valid LTS [Databricks Runtime Version](https://docs.databricks.com/aws/en/release-notes/runtime/). Also see [Databricks Runtime tags on Dockerhub](https://hub.docker.com/r/databricksruntime/standard/tags). |
| [MATLAB_RELEASE](#build-an-image-for-a-different-matlab-release) | R2026b | MATLAB release to install, for example, `R2024b`. |
| [MATLAB_UPDATE](#build-an-image-for-a-specific-matlab-update) | *unset* | The update to install for a given MATLAB release (for example, `U1` for update 1 of the specified `MATLAB_RELEASE`). To install the latest available update, leave this argument unset. For details, see [MATLAB Release Name (MathWorks)](https://www.mathworks.com/help/install/ug/mpminstall.html#mw_37e5e202-ecc6-4e61-9fa4-22b81f9931d3). |
| [MATLAB_PRODUCT_LIST](#build-an-image-with-a-specific-set-of-products) | MATLAB | Space-separated list of products to install, for example, `MATLAB Simulink Deep_Learning_Toolbox Fixed-Point_Designer`. For more information, see [MPM.md](https://github.com/mathworks-ref-arch/matlab-dockerfile/blob/main/MPM.md). |
| [MATLAB_INSTALL_LOCATION](#build-an-image-with-matlab-installed-to-a-specific-location) | /opt/matlab/R2026b | Path to install MATLAB. |
| [LICENSE_SERVER](#build-an-image-configured-to-use-a-license-server) | *unset* | Port and hostname of the machine that is running the network license manager, using the `port@hostname` syntax. For example: `27000@MyServerName`. |
| [PIP_INDEX_URL](#build-an-image-using-a-custom-pypi-index) | *unset* | Custom PyPI index URL for pip installs (e.g., an internal Artifactory). This value is only used during the build and is not stored in the final image. |
| [ADDITIONAL_PIP_PACKAGES](#build-an-image-with-additional-python-packages) | *unset* | Space-separated list of additional Python packages to install via pip. Supports version specifiers (e.g., `"numpy==2.1.3 pandas>=2.0"`). |

Use these arguments with the `docker build` command to customize your image.
Alternatively, you can change the default values for these arguments directly in the [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/Dockerfile).

#### Build an Image for a Different MATLAB Release

You may need to have a number of combinations of MATLAB releases and Databricks runtime versions over time.
For example, to build an image for MATLAB R2024b, use this command.

```bash
docker build --build-arg MATLAB_RELEASE=R2024b -t matlab/databricks/desktop:r2024b-dbx17.3 .
```

> [!NOTE]
> The images for MATLAB R2026b and later do not include the Java® Runtime Environment (JRE) that ships with MATLAB. Instead, MATLAB is configured to use the system Java available in the Databricks base image, which is Java 17 on Databricks Runtime 17.3 LTS.

#### Build an Image for a Specific MATLAB Update

Each MATLAB release can have multiple updates (for example, update 1 or update 2). By default, the Dockerfile installs the latest available update for the specified release. To install a specific update, use the `MATLAB_UPDATE` build argument.

The value has the format `U<number>`, where `U0` refers to the base release with no updates applied. For details, see [MATLAB Release Name (MathWorks)](https://www.mathworks.com/help/install/ug/mpminstall.html#mw_37e5e202-ecc6-4e61-9fa4-22b81f9931d3) documentation.

#### Build an Image with a Specific Set of Products

For example, to build an image with MATLAB and Simulink&reg;, use this command.

```bash
docker build --build-arg MATLAB_PRODUCT_LIST='MATLAB Simulink' -t matlab/databricks/desktop:R2026b-dbx17.3 .
```

#### Build an Image with MATLAB Installed to a Specific Location

For example, to build an image with MATLAB installed at /opt/matlab, use this command.

```bash
docker build --build-arg MATLAB_INSTALL_LOCATION='/opt/matlab' -t matlab/databricks/desktop:R2026b-dbx17.3 .
```

#### Build an Image Configured to Use a License Server

Including the license server information with the `docker build` command means you do not have to pass it when running the container.

```bash
# Build container with the license server.
docker build --build-arg LICENSE_SERVER=27000@MyServerName -t matlab/databricks/desktop:R2026b-dbx17.3 .

# Run the container without needing to pass license information.
```

If you did not provide the license server information when building the image, then provide it when running the container. Set the environment variable `MLM_LICENSE_FILE` using the `-e` flag, with the  network license manager's location in the format `port@hostname`.

```bash
# Start MATLAB, print version information, and exit (local testing).
docker run --init --rm -e MLM_LICENSE_FILE=27000@MyServerName --entrypoint=matlab matlab/databricks/desktop:R2026b-dbx17.3 -batch ver
```

On Databricks, you can set the `MLM_LICENSE_FILE` environment variable when creating the compute cluster. For instructions on setting environment variables in Databricks, see [Databricks Cluster Configuration](https://docs.databricks.com/aws/en/compute/configure#environment-variables).

#### Build an Image Using a Custom PyPI Index

If your network restricts access to the public PyPI registry, you can specify a custom PyPI index URL (for example, an internal Artifactory instance). This value is only used during the build and is not stored in the final image.

```bash
docker build --build-arg PIP_INDEX_URL=https://my-artifactory.example.com/api/pypi/pypi-remote/simple -t matlab/databricks/desktop:R2026b-dbx17.3 .
```

#### Build an Image with Additional Python Packages

To install additional Python packages into the image at build time, use the `ADDITIONAL_PIP_PACKAGES` argument. Provide a space-separated list of packages, with optional version specifiers.

```bash
docker build --build-arg ADDITIONAL_PIP_PACKAGES="numpy==2.1.3 pandas>=2.0" -t matlab/databricks/desktop:R2026b-dbx17.3 .
```

The build fails if any specified package cannot be installed, ensuring the resulting image always contains the packages you requested.

## More MATLAB Docker Resources

- To view Dockerfiles for various MATLAB releases and platforms, see [MATLAB Container Images (GitHub)]. To view the Dockerfile for R2026b, see [MATLAB R2026b Container Image (GitHub)](https://github.com/mathworks-ref-arch/container-images/blob/main/matlab-deps/r2026b/ubuntu22.04/Dockerfile).

----

Copyright 2026 The MathWorks, Inc.
