# syntax=docker/dockerfile:1
# check=skip=all

# Copyright 2025-2026 The MathWorks, Inc.

# Dockerfile to add the MATLAB Runtime to the databricksruntime/<version> image

## Dockerfile to build MATLAB Container where:
# 1. Base image is Databricks Runtime
# 2. MATLAB Runtime dependencies are installed from mathworks-ref-arch/container-images repository
# 3. MATLAB Runtime is installed

# Specify the Databricks Image Runtime Version to use as the base image. Example 16.4, 17.3
ARG DATABRICKS_RUNTIME_VERSION=17.3
# Specify the version of Ubuntu used in the base image.
ARG UBUNTU_VERSION=24.04
# Specify the MATLAB release to install.
ARG MATLAB_RELEASE=R2026a
# Specify the MATLAB update to install.
ARG MATLAB_UPDATE=0

#################################################################################################
## Build stage that installs MATLAB Runtime and its dependencies.
#################################################################################################

FROM databricksruntime/standard:${DATABRICKS_RUNTIME_VERSION}-LTS AS base-image
ARG UBUNTU_VERSION
ARG MATLAB_RELEASE
ARG MATLAB_UPDATE
ARG DATABRICKS_RUNTIME_VERSION

USER root

# Updates the default shell to bash with pipefail
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# MATLAB Runtime dependencies to use
ARG MATLAB_DEPS_URL="https://raw.githubusercontent.com/mathworks-ref-arch/container-images/main/matlab-runtime-deps/${MATLAB_RELEASE}/ubuntu${UBUNTU_VERSION}/base-dependencies.txt"
ARG MATLAB_DEPENDENCIES="matlab-deps-${MATLAB_RELEASE}-base-dependencies.txt"
ARG ADDITIONAL_PACKAGES="wget curl unzip ca-certificates"

## Install dependencies
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update \
    && apt-get install --no-install-recommends -y ${ADDITIONAL_PACKAGES} \
    && wget -q "$(echo "${MATLAB_DEPS_URL}" | tr "[:upper:]" "[:lower:]")" -O ${MATLAB_DEPENDENCIES} \
    && xargs -a ${MATLAB_DEPENDENCIES} -r apt-get install --no-install-recommends -y \
    && apt-get clean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/* ${MATLAB_DEPENDENCIES}

WORKDIR /mcr-install
# MATLAB Runtime zip-file URL
ARG MATLAB_RUNTIME_URL=""
ARG MCR_INSTALL_LOCATION=/MATLAB_Runtime
ARG MCR_DOWNLOAD_LOCATION=/tmp/MATLAB_Runtime
# Download & Install MATLAB Runtime
RUN if [ -z "${MATLAB_RUNTIME_URL}" ]; then \
        if [ "${MATLAB_UPDATE}" = "0" ]; then \
            MATLAB_RUNTIME_URL="https://ssd.mathworks.com/supportfiles/downloads/${MATLAB_RELEASE}/Release/0/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_${MATLAB_RELEASE}_glnxa64.zip"; \
        else \
            MATLAB_RUNTIME_URL="https://ssd.mathworks.com/supportfiles/downloads/${MATLAB_RELEASE}/Release/${MATLAB_UPDATE}/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_${MATLAB_RELEASE}_Update_${MATLAB_UPDATE}_glnxa64.zip"; \
        fi \
    fi \
    && wget -q "${MATLAB_RUNTIME_URL}" -O MATLAB_Runtime.zip \
    && unzip -q MATLAB_Runtime.zip \
    && ./install \
    -mode silent \
    -agreeToLicense yes \
    -destinationFolder ${MCR_DOWNLOAD_LOCATION} \
    && mv ${MCR_DOWNLOAD_LOCATION}/R* ${MCR_INSTALL_LOCATION} \
    && rm ${MCR_INSTALL_LOCATION}/sys/os/glnxa64/libstdc++.so.6* \
    && cd / && rm -rf /mcr-install ${MCR_DOWNLOAD_LOCATION}

# Work dir assumed by Databricks
WORKDIR /root

# This needs to be set for a Docker image based cluster. We need to know the server side version on Databricks Connect workflows.
# This environment variable exists in non-docker based workflows.
ENV DATABRICKS_RUNTIME_VERSION=${DATABRICKS_RUNTIME_VERSION}

ENV MCR_VERSION=${MATLAB_RELEASE}

ENV MCRROOT=${MCR_INSTALL_LOCATION}

ENV LD_LIBRARY_PATH="${MCR_INSTALL_LOCATION}/runtime/glnxa64:${MCR_INSTALL_LOCATION}/bin/glnxa64:${MCR_INSTALL_LOCATION}/sys/os/glnxa64:${MCR_INSTALL_LOCATION}/extern/bin/glnxa64:${MCR_INSTALL_LOCATION}/sys/opengl/lib/glnxa64"