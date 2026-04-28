#!/usr/bin/env bash

# This script installs MATLAB and its dependencies on a Linux system.
# It is designed to be run as a root user.
# Usage: ./SetupCluster.sh [OPTIONS]


# Script requires access to the internet, WGET, GIT

# Helper function to check if verbose output is enabled
is_verbose_enabled() {
    [[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]
}

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script installs MATLAB and its dependencies."
    echo ""
    echo "Options:"
    echo "  -p, --products <list>   Specify the products to install (space-separated)."
    echo "  -r, --release <string>  Specify the MATLAB release version (default: R2024b)."
    echo "  -v                      Enable verbose output."
    echo "  -h                      Display this help message and exit."
    echo ""
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p|--products) PRODUCTS="$2"; shift 2;;
        -r|--release) RELEASE="$2"; shift 2;;
        -v|--verbose) VERBOSE_OUTPUT=1; shift 1 ;;
        -h|--help) 
            print_help
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Validate required arguments
if [[ -z "$PRODUCTS" ]]; then
    if is_verbose_enabled; then
        echo "No products specified. Defaulting to MATLAB."
    fi
    PRODUCTS="MATLAB"
fi

if [[ -z "$RELEASE" ]]; then
    if is_verbose_enabled; then
        echo "Defaulting to Latest available MATLAB Release."
    fi
    RELEASE="R2026a"
fi

echo "Installing MATLAB with the following parameters:"
echo "Products: $PRODUCTS"
echo "Release: $RELEASE"

mkdir -p /matlab-install && cd /matlab-install

export DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC" 

export UBUNTU_VERSION=24.04
export MATLAB_RELEASE=${RELEASE}
export MATLAB_DEPS_URL="https://raw.githubusercontent.com/mathworks-ref-arch/container-images/main/matlab-deps/${MATLAB_RELEASE}/ubuntu${UBUNTU_VERSION}/base-dependencies.txt"
export MATLAB_DEPENDENCIES="matlab-deps-${MATLAB_RELEASE}-base-dependencies.txt"
# Specify the list of products(toolboxes) to install into MATLAB.
export MATLAB_PRODUCT_LIST=${PRODUCTS}
# Specify MATLAB Install Location.
export MATLAB_INSTALL_LOCATION="/opt/matlab/${MATLAB_RELEASE}"

export ADDITIONAL_PACKAGES="wget curl unzip ca-certificates xvfb git vim fluxbox"
export PIP_BREAK_SYSTEM_PACKAGES=1

export DEBIAN_FRONTEND=noninteractive && apt-get update \
    && apt-get install --no-install-recommends -y ${ADDITIONAL_PACKAGES}\
    && wget $(echo ${MATLAB_DEPS_URL} | tr "[:upper:]" "[:lower:]") -O ${MATLAB_DEPENDENCIES} \
    && xargs -a ${MATLAB_DEPENDENCIES} -r apt-get install --no-install-recommends -y \
    && apt-get clean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*


mkdir -p /matlab-install && cd /matlab-install


#### Install MATLAB using MathWorks Product Manager (MPM)
echo "Installing MATLAB ${MATLAB_RELEASE} with products: ${MATLAB_PRODUCT_LIST} ..."
wget -q https://www.mathworks.com/mpm/glnxa64/mpm \
    && chmod +x mpm \
    && ./mpm install \
    --release=${MATLAB_RELEASE} \
    --destination=${MATLAB_INSTALL_LOCATION} \
    --products ${MATLAB_PRODUCT_LIST} \
    || (echo "MPM Installation Failure. See below for more information:" && cat /tmp/mathworks_root.log && false) \
    && mv mpm /usr/local/bin/mpm \
    && rm -rf /tmp/mathworks_root.log \
    && ln -s ${MATLAB_INSTALL_LOCATION}/bin/matlab /usr/local/bin/matlab

# verify installation
if [ ! -f "${MATLAB_INSTALL_LOCATION}/bin/matlab" ]; then
    echo "MATLAB installation failed. Exiting."
    exit 1
fi
echo "MATLAB installation completed successfully."


#### Install Administered MathWorks Service Host
echo "Installing Administered MathWorks Service Host..."

export MSH_MANAGED_INSTALL_ROOT=/usr/local/MathWorks/ServiceHost/
export TMP_MSH_DOWNLOAD_LOCATION=/tmp/Downloads/MathWorks/ServiceHost
export MATHWORKS_SERVICE_HOST_MANAGED_INSTALL_ROOT=${MSH_MANAGED_INSTALL_ROOT}

git clone https://github.com/mathworks-ref-arch/administer-mathworks-service-host.git \
    && cd /matlab-install/administer-mathworks-service-host/admin-scripts/linux/admin-controlled-installation \
    && ./download_msh.sh --destination ${TMP_MSH_DOWNLOAD_LOCATION} \
    && ./install_msh.sh --source ${TMP_MSH_DOWNLOAD_LOCATION} --destination ${MSH_MANAGED_INSTALL_ROOT} --no-update-environment \
    && ./cleanup_default_msh_installation_location.sh --for-all-users \
    
echo "Administered MathWorks Service Host installation complete."
cd /root && rm -rf /matlab-install ${TMP_MSH_DOWNLOAD_LOCATION}


#### Install matlab-proxy
echo "Installing matlab-proxy..."
export PYTHON3=/databricks/python3/bin/python3
${PYTHON3} -m pip install --no-cache-dir matlab-proxy
echo "matlab-proxy installation completed..."

#### Set environment variables for all users
export MATLAB_ENV_FILE="/etc/bash.bashrc"
echo "export MSH_MANAGED_INSTALL_ROOT=/usr/local/MathWorks/ServiceHost/" > ${MATLAB_ENV_FILE}
echo "export MATHWORKS_SERVICE_HOST_MANAGED_INSTALL_ROOT=${MSH_MANAGED_INSTALL_ROOT}" >> ${MATLAB_ENV_FILE}
echo "export MWI_ENABLE_TOKEN_AUTH=False MWI_USE_COOKIE_CACHE=True MWI_BASE_URL=/matlab" >> ${MATLAB_ENV_FILE}

#### save environment variables into /etc/profile.d/matlab.sh
echo "Saving MATLAB environment variables..."