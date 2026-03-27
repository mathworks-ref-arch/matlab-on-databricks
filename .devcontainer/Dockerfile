# Copyright 2025 The MathWorks, Inc.

# Light weight image only to test Jupyter Notebook UI

# Using the default python version in Databricks Runtime 17.3-LTS
ARG PYTHON_VERSION=3.12
ARG MATLAB_RELEASE="R2025b"
ARG UBUNTU_VERSION="24.04"
# Default installation directory for MATLAB
ARG MATLAB_INSTALL_LOCATION="/opt/matlab"
ARG MATLAB_PRODUCT_LIST="MATLAB"

FROM ubuntu:24.04

ARG PYTHON_VERSION
ARG MATLAB_RELEASE
ARG UBUNTU_VERSION
ARG MATLAB_INSTALL_LOCATION
ARG MATLAB_PRODUCT_LIST 

ENV DEBIAN_FRONTEND=noninteractive
# Install build dependencies, install UV (for python) and NVM (for nodejs)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    unzip \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install MATLAB dependencies and MATLAB using MPM
ARG MATLAB_DEPS_URL="https://raw.githubusercontent.com/mathworks-ref-arch/container-images/main/matlab-deps/${MATLAB_RELEASE}/ubuntu${UBUNTU_VERSION}/base-dependencies.txt"
ARG MATLAB_DEPENDENCIES="matlab-deps-${MATLAB_RELEASE}-base-dependencies.txt"
ARG ADDITIONAL_PACKAGES="wget curl unzip ca-certificates xvfb git vim fluxbox"
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update \
    && apt-get install --no-install-recommends -y ${ADDITIONAL_PACKAGES}\
    && wget $(echo ${MATLAB_DEPS_URL} | tr "[:upper:]" "[:lower:]") -O ${MATLAB_DEPENDENCIES} \
    && xargs -a ${MATLAB_DEPENDENCIES} -r apt-get install --no-install-recommends -y \
    && apt-get clean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/* ${MATLAB_DEPENDENCIES}

RUN echo "Installing MATLAB using MPM..."
RUN wget -q https://www.mathworks.com/mpm/glnxa64/mpm && \ 
    chmod +x mpm \
    && ./mpm install --release=${MATLAB_RELEASE} --destination=${MATLAB_INSTALL_LOCATION} \
    --products ${MATLAB_PRODUCT_LIST} \
    || (echo "MPM Installation Failure. See below for more information:" && cat /tmp/mathworks_root.log && false)\
    && rm -f /tmp/mathworks_root.log \
    && ln -s ${MATLAB_INSTALL_LOCATION}/bin/matlab /usr/local/bin/matlab \
    && mv mpm /usr/local/bin


# Installs UV for all users
RUN curl -LsSf https://astral.sh/uv/install.sh | \
    UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh

# Create a python environment for the ROOT user
COPY requirements.txt /tmp/requirements.txt
RUN uv venv /local-dev-env --python ${PYTHON_VERSION} && uv pip install -r /tmp/requirements.txt --python /local-dev-env/bin/python
RUN UV_PYTHON_INSTALL_DIR=/opt/uv-python UV_TOOL_BIN_DIR=/usr/local/bin UV_TOOL_DIR=/opt/uv-tools \
uv tool install matlab-proxy --force --python ${PYTHON_VERSION} && \
chmod -R 755 /opt/uv-tools && chmod -R 755 /opt/uv-python
