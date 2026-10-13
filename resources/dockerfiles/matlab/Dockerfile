# syntax=docker/dockerfile:1
# check=skip=all

# Copyright 2025-2026 The MathWorks, Inc.

## Dockerfile to build MATLAB Container where:
# 1. Base image is Databricks Runtime
# 2. MATLAB R2026b using MATLAB Package Manager & install dependencies from mathworks-ref-arch/container-images repository

### Dockerfile Build Commands:

# By Default the container will be built for Databricks Runtime 17.3-LTS and Ubuntu 24.04.
# docker build -t matlab-on-databricks:R2026b-17.3  .

# To build the container for a different Databricks Runtime version or Ubuntu version, you can use the following commands:
# docker build --build-arg DATABRICKS_RUNTIME_VERSION=15.4 \
#              --build-arg UBUNTU_VERSION=22.04 \
#              -t matlab-on-databricks:R2026b-15.4  .

# The other build arguments can be used to specify the MATLAB release, product list, install location, and license server.
# For example, to build the container with MATLAB R2026b, a specific product list, and a license server, you can use the following command:
# docker build --build-arg MATLAB_RELEASE=R2026b
#              --build-arg MATLAB_PRODUCT_LIST="MATLAB Deep_Learning_Toolbox Symbolic_Math_Toolbox"
#              --build-arg MATLAB_INSTALL_LOCATION="/opt/matlab/R2026b"
#              --build-arg LICENSE_SERVER=12345@hostname.com
#              -t my_matlab_image_name .


# Specify the Databricks Image Runtime Version to use as the base image. Example 16.4, 17.3, 18.3
# Refer https://hub.docker.com/r/databricksruntime/standard/tags for supported tags
ARG DATABRICKS_RUNTIME_VERSION=17.3
# Specify the version of Ubuntu used in the base image.
ARG UBUNTU_VERSION=24.04
# Use the python that is recommended by Databricks: https://docs.databricks.com/aws/en/compute/custom-containers#option-1-use-a-base-built-by-databricks
ARG PYTHON3=/databricks/python3/bin/python3
# Specify the MATLAB release to install.
ARG MATLAB_RELEASE=R2026b
# Specify a MATLAB release update version (for example, U0 for the base release, or U1 for update 1).
# For details, see: https://www.mathworks.com/help/install/ug/mpminstall.html#mw_37e5e202-ecc6-4e61-9fa4-22b81f9931d3
# To install the latest available update, leave this argument empty.
ARG MATLAB_UPDATE=""
# Specify the list of products(toolboxes) to install into MATLAB.
ARG MATLAB_PRODUCT_LIST="MATLAB Database_Toolbox"
# Specify MATLAB Install Location.
ARG MATLAB_INSTALL_LOCATION="/opt/matlab/${MATLAB_RELEASE}"
# Specify license server information using the format: port@hostname
ARG LICENSE_SERVER
# Whether to install Java or use built-in. For R2026b and later, Java is not included in the MATLAB installation,
# so this argument is overridden to 0 for R2026b and later releases.
ARG INCLUDE_JRE=1
# Whether or not to include gpu libraries
ARG INCLUDE_GPU=0
# Specify a custom PyPI index URL (e.g., internal Artifactory) to use for pip installs.
ARG PIP_INDEX_URL
# Specify additional Python packages to install via pip. Example: "numpy==2.1.3 pandas>=2.0"
ARG ADDITIONAL_PIP_PACKAGES=""

#################################################################################################
## Build stage that installs MATLAB and its dependencies.
#################################################################################################

FROM databricksruntime/standard:${DATABRICKS_RUNTIME_VERSION}-LTS AS base
ARG UBUNTU_VERSION
ARG PYTHON3
ARG MATLAB_RELEASE
ARG MATLAB_UPDATE
ARG MATLAB_INSTALL_LOCATION
ARG MATLAB_PRODUCT_LIST
ARG LICENSE_SERVER
ARG INCLUDE_JRE
ARG INCLUDE_GPU
ARG DATABRICKS_RUNTIME_VERSION
ARG PIP_INDEX_URL
ARG ADDITIONAL_PIP_PACKAGES

USER root

# Updates the default shell to bash with pipefail
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN [ -d /usr/share/X11/xkb ] || mkdir -p /usr/share/X11/xkb

# All supported databricksruntime images are linux/amd64 only, so the amd64 dependency file is used.
ARG MATLAB_DEPS_URL="https://raw.githubusercontent.com/mathworks-ref-arch/container-images/refs/heads/main/matlab-deps/${MATLAB_RELEASE}/ubuntu${UBUNTU_VERSION}/base-dependencies-amd64.txt"
ARG MATLAB_DEPENDENCIES="matlab-deps-${MATLAB_RELEASE}-base-dependencies.txt"
ARG ADDITIONAL_PACKAGES="wget curl unzip ca-certificates xvfb git fluxbox"

# Configure Python (>3.12) to allow installing system wide packages.
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

## Install dependencies
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update \
    && apt-get install --no-install-recommends -y ${ADDITIONAL_PACKAGES} \
    && wget -q "$(echo "${MATLAB_DEPS_URL}" | tr "[:upper:]" "[:lower:]")" -O ${MATLAB_DEPENDENCIES} \
    && xargs -a ${MATLAB_DEPENDENCIES} -r apt-get install --no-install-recommends -y \
    && apt-get clean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/* ${MATLAB_DEPENDENCIES}

WORKDIR /matlab-install
ARG MSH_MANAGED_INSTALL_ROOT=/usr/local/MathWorks/ServiceHost/
ARG MSH_DOWNLOAD_LOCATION=/tmp/Downloads/MathWorks/ServiceHost

## Install MATLAB & Administered MathWorks Service Host
# Note: Installation of Support Packages, requires MPM to run as end user.

RUN wget -q https://www.mathworks.com/mpm/glnxa64/mpm \
    && chmod +x mpm \
    && if [[ "${MATLAB_RELEASE}" > "R2026a" ]]; then INCLUDE_JRE="0"; fi \
    && ./mpm install \
    --release=${MATLAB_RELEASE}${MATLAB_UPDATE} \
    --destination=${MATLAB_INSTALL_LOCATION} \
    --products ${MATLAB_PRODUCT_LIST} \
    $(if [ "$INCLUDE_JRE" = "0" ]; then echo "--no-jre"; fi) \
    $(if [ "$INCLUDE_GPU" = "0" ]; then echo "--no-gpu"; fi) \
    || (echo "MPM Installation Failure. See below for more information:" && cat /tmp/mathworks_root.log && false) \
    && mv mpm /usr/local/bin/mpm \
    && rm -rf /tmp/mathworks_root.log \
    && if [ "$INCLUDE_JRE" = "0" ]; then ${MATLAB_INSTALL_LOCATION}/bin/matlab_jenv -allusers $(dirname $(dirname $(readlink -f $(which java)))); fi \
    && ln -s ${MATLAB_INSTALL_LOCATION}/bin/matlab /usr/local/bin/matlab \
    && git clone https://github.com/mathworks-ref-arch/administer-mathworks-service-host.git \
    && cd /matlab-install/administer-mathworks-service-host/admin-scripts/linux/admin-controlled-installation \
    && ./download_msh.sh --destination ${MSH_DOWNLOAD_LOCATION} \
    && ./install_msh.sh --source ${MSH_DOWNLOAD_LOCATION} --destination ${MSH_MANAGED_INSTALL_ROOT} --no-update-environment \
    && ./cleanup_default_msh_installation_location.sh --for-all-users \
    && rm -f ${MATLAB_INSTALL_LOCATION}/sys/os/glnxa64/libstdc++.so.6* \
    && cd / && rm -rf /matlab-install ${MSH_DOWNLOAD_LOCATION}

# Update MATLAB settings
RUN cat >> ${MATLAB_INSTALL_LOCATION}/toolbox/local/matlabrc.m <<'EOF'
    % Added by Reference Architecture for MATLAB on Databricks
    s = settings;
    s.matlab.commandwindow.GettingStarted.PersonalValue = 0;
    s.matlab.commandwindow.WarnIfRoot.PersonalValue = 0;
EOF

# Work dir assumed by Databricks
WORKDIR /root

ENV MATHWORKS_SERVICE_HOST_MANAGED_INSTALL_ROOT=${MSH_MANAGED_INSTALL_ROOT}
# Inform MathWorks Service Host that it is running in an LSF-like workflow
ENV MATHWORKS_SERVICE_HOST_IN_LSF=1

########################################################################
# Install matlab-proxy as root user for all users of the container
########################################################################
## MATLAB Proxy Configuration
ENV MW_CONTEXT_TAGS=MATLAB_PROXY:DATABRICKS:V1
ENV MWI_USE_COOKIE_CACHE=True
ENV MWI_APP_PORT=8888
ENV MWI_BASE_URL="/matlab"
# Disabling Token Authentication, as Databricks already has several layers of authentication built into it.
ENV MWI_ENABLE_TOKEN_AUTH=False
EXPOSE 8888

# Explicit installation of ipywidgets if not already present
# Selecting version 7.8.1 as that is the latest version of ipywidgets supported in Databricks Runtime
RUN ${PYTHON3} -m pip install --no-cache-dir matlab-proxy build ${ADDITIONAL_PIP_PACKAGES} && \
    (${PYTHON3} -m pip show ipywidgets || ${PYTHON3} -m pip install ipywidgets==7.8.1)

#######################################################################
# Install MATLAB Engine for Python
# Installation can fail if, Python Version is incompatible.
# For more information, see https://mathworks.com/support/requirements/python-compatibility.html
#
# Failure to install does not stop the build
########################################################################
RUN echo "Installing MATLAB Engine for Python..." && \
    env LD_LIBRARY_PATH=${MATLAB_INSTALL_LOCATION}/bin/glnxa64 ${PYTHON3} -m pip install --no-cache-dir ${MATLAB_INSTALL_LOCATION}/extern/engines/python || \
    echo "Failed to install MATLAB Engine for Python... skipping ..."

# Reset PIP settings
ENV PIP_BREAK_SYSTEM_PACKAGES=

# This needs to be set for a Docker image based cluster. We need to know the server side version on Databricks Connect workflows.
# This environment variable exists in non-docker based workflows.
ENV DATABRICKS_RUNTIME_VERSION=${DATABRICKS_RUNTIME_VERSION}

# Configure license server
ENV MLM_LICENSE_FILE=${LICENSE_SERVER}

# Required to use MATLAB Runtime
ENV LD_LIBRARY_PATH="${MATLAB_INSTALL_LOCATION}/runtime/glnxa64:${MATLAB_INSTALL_LOCATION}/bin/glnxa64:${MATLAB_INSTALL_LOCATION}/sys/os/glnxa64:${MATLAB_INSTALL_LOCATION}/extern/bin/glnxa64:${MATLAB_INSTALL_LOCATION}/sys/opengl/lib/glnxa64"

# Entrypoint supposed to be ignored in Databricks and can be used for local testing.
# ENTRYPOINT ["/bin/sh", "-c", "su ubuntu -c 'cd $HOME && . /databricks/python3/bin/activate && matlab-proxy-app'" ]