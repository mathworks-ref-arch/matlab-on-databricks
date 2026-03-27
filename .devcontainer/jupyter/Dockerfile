# Copyright 2026 The MathWorks, Inc.

# Light weight image only to test Jupyter Notebook UI

ARG PYTHON_VERSION=3.11

FROM ubuntu:24.04

ARG PYTHON_VERSION

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

# Installs UV for all users
RUN curl -LsSf https://astral.sh/uv/install.sh | \
    UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh

COPY requirements.txt /tmp/requirements.txt
# Install Jupyter using UV as a tool accessible to all users
RUN UV_PYTHON_INSTALL_DIR=/opt/uv-python UV_TOOL_BIN_DIR=/usr/local/bin UV_TOOL_DIR=/opt/uv-tools \
    uv tool install jupyter-core --with-requirements /tmp/requirements.txt --force --python ${PYTHON_VERSION} && \
    chmod -R 755 /opt/uv-tools && chmod -R 755 /opt/uv-python

USER ubuntu

WORKDIR /home/ubuntu
