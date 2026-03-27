#!/usr/bin/env bash
# This script is used to install MATLAB toolboxes into a specified MATLAB root directory.
# It supports command-line options to specify the MATLAB root directory, release version,
# and the list of products to install. The script also provides a help message for usage guidance.
#------------------------------------------------------------------------------
# Copyright 2025-2026 The MathWorks, Inc.
#------------------------------------------------------------------------------

set -eu -o pipefail
# exits on an error (-e, equivalent to -o errexit);
# exits on an undefined variable (-u, equivalent to -o nounset);
# exits on an error in piped-together commands (-o pipefail)

# Initialize VERBOSE_OUTPUT, default to 0
: "${VERBOSE_OUTPUT:=0}"

# Checks if verbose output is enabled
is_verbose_enabled() {
	[[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]
}

# Display usage information
print_help() {
	echo "Usage: $0 [OPTIONS]"
	echo ""
	echo "This script installs toolboxes into the specified MATLAB root directory."
	echo ""
	echo "Options:"
	echo "  -d, --destination <path> Specify the MATLAB root directory to install into, or MATLAB on your PATH will be used."
	echo "  -r, --release <string>   Specify the MATLAB release version thats already installed."
	echo "  -p, --products <list>    Specify the products to install (space-separated)."
	echo "  -v, --verbose            Enable verbose output."
	echo "  -h, --help               Display this help message and exit."
	echo ""
}

# Get MATLAB path
mw_get_matlab_root() {
	local MATLAB_PATH=$1
	local MATLAB_ROOT

	if [ -n "$MATLAB_PATH" ]; then
		MATLAB_ROOT="$MATLAB_PATH"
	else
		# If path is not provided, use MATLAB from the system PATH if available.
		local MATLAB_ON_PATH
		MATLAB_ON_PATH=$(which matlab)
		if [ -n "$MATLAB_ON_PATH" ]; then
			MATLAB_ROOT=$(readlink -f "$MATLAB_ON_PATH" | xargs dirname | xargs dirname)
			if is_verbose_enabled; then
				echo "MATLAB found on PATH: $MATLAB_ROOT" >&2
			fi
		else
			echo "Error: MATLAB not found on PATH. Either add MATLAB to the PATH or provide it using the -d flag." >&2
			return 1
		fi
	fi
	# Check if MATLAB_ROOT exists
	if [ ! -d "$MATLAB_ROOT" ]; then
		echo "Error: Directory does not exist: $MATLAB_ROOT" >&2
		return 1
	fi
	echo "$MATLAB_ROOT"
	return 0
}

# Install products using mpm
mw_install_products() {
	local MATLAB_ROOT=$1
	local PRODUCTS=$2
	local RELEASE=$3

	if [ -z "$PRODUCTS" ]; then
		echo "No products specified. Exiting." >&2
		return 1
	fi

	if [ -z "$RELEASE" ]; then
		echo "No MATLAB release specified. Exiting." >&2
		return 1
	fi

	if is_verbose_enabled; then
		echo "Installing products: $PRODUCTS" >&2
	fi

	# Ensure mpm is cleaned up even if script exits unexpectedly
	trap 'rm -f mpm' RETURN

	# Download MPM
	if ! { wget -q https://www.mathworks.com/mpm/glnxa64/mpm && chmod +x mpm; }; then
		echo "Error: Failed to download MPM." >&2
		return 1
	fi

	# Install products
	if ! ./mpm install --destination "$MATLAB_ROOT" --products "$PRODUCTS" --release "$RELEASE"; then
		echo "Error: mpm installation failed." >&2
		return 1
	fi

	echo "Installation complete."
	return 0
}

# Parse command-line arguments and execute product installation
main_install_products() {
	local MATLAB_ROOT_ARG=""
	local PRODUCTS=""
	local RELEASE=""

	while [[ "$#" -gt 0 ]]; do
		case $1 in
		-d | --destination)
			MATLAB_ROOT_ARG="$2"
			shift 2
			;;
		-p | --products)
			PRODUCTS="$2"
			shift 2
			;;
		-r | --release)
			RELEASE="$2"
			shift 2
			;;
		-v | --verbose)
			export VERBOSE_OUTPUT=1
			shift 1
			;;
		-h | --help)
			print_help
			exit 0
			;;
		*)
			echo "Unknown parameter passed: $1" >&2
			print_help
			exit 1
			;;
		esac
	done

	if ! MATLAB_ROOT=$(mw_get_matlab_root "$MATLAB_ROOT_ARG"); then
		exit 1
	fi
	if ! mw_install_products "$MATLAB_ROOT" "$PRODUCTS" "$RELEASE"; then
		exit 1
	fi
}

# Execute main_install_products only when script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
	main_install_products "$@"
fi
