#!/usr/bin/env bash
##
# @file ListInstalledProducts.sh
# @brief Script to list all installed MATLAB toolboxes and products.
#
# This script mimics the algorithm used by the MATLAB Command VER and
# searches for `Contents.m` files in the specified MATLAB root directory
# to identify installed MATLAB toolboxes and products. It excludes certain directories
# and ensures that MATLAB itself is listed as the top result if applicable.
#
# The script supports the following features:
# - Excludes directories such as `toolbox/local`, `toolbox/matlab`, and `mcr/`.
# - Skips folders containing `+` or `@` symbols in their paths.
# - Allows specifying a custom MATLAB root directory using the `--root` or `-r` flag.
# - Displays a summary of the results, including the number of toolboxes found, the time taken, and the root location searched.
# - Provides a help option (`-h`) to display usage information.
#
# @usage
#   ./ListInstalledProducts.sh [OPTIONS]
#
# @options
#   -r, --root <path>   Specify the MATLAB root directory to search.
#   -h                  Display help information and exit.
#
# @example
#   ./ListInstalledProducts.sh --root /path/to/matlab
#
# @note
#   Ensure that the script has execute permissions before running:
#   `chmod +x ListInstalledProducts.sh`
#
# @see
#   MATLAB documentation for the function `VER`.
##
#------------------------------------------------------------------------------
# Copyright 2025 The MathWorks, Inc.
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
	echo "This script lists all toolboxes installed in the specified MATLAB root directory."
	echo "It excludes certain directories and ensures MATLAB is listed as the top result if applicable."
	echo ""
	echo "Options:"
	echo "  -r, --root <path>   Specify the MATLAB root directory to search."
	echo "  -v, --verbose       Enable verbose output."
	echo "  -h, --help          Display this help message and exit."
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

mw_get_matlab_version_info() {
	local MATLAB_ROOT=$1
	local version_info_file="$MATLAB_ROOT/VersionInfo.xml"
	local matlab_version="Unknown"

	if [ ! -f "$version_info_file" ]; then
		if is_verbose_enabled; then
			echo "Warning: VersionInfo.xml not found in $MATLAB_ROOT" >&2
		fi
		echo "$matlab_version"
		return 0
	fi

	local version
	version=$(grep -oP '(?<=<version>).*?(?=</version>)' "$version_info_file")
	local release
	release=$(grep -oP '(?<=<release>).*?(?=</release>)' "$version_info_file")
	local description
	description=$(grep -oP '(?<=<description>).*?(?=</description>)' "$version_info_file")

	if [ -n "$release" ]; then
		matlab_version="$release"
		if [ -n "$description" ]; then
			matlab_version="$matlab_version $description"
		fi
		if [ -n "$version" ]; then
			matlab_version="$matlab_version ($version)"
		fi
	fi

	echo "$matlab_version"
	return 0
}

mw_get_installed_products() {
	local MATLAB_ROOT=$1

	# Check if MATLAB's Contents.m exists
	local matlab_contents="$MATLAB_ROOT/toolbox/matlab/general/Contents.m"
	local matlab_result=""
	if [ -f "$matlab_contents" ]; then
		matlab_result="MATLAB"
	fi

	# Helper function to process a single Contents.m file.
	# shellcheck disable=SC2317
	# shellcheck disable=SC2329
	_process_contents_file() {
		local file="$1"
		# Read the second line of the file
		local second_line
		second_line=$(sed -n "2p" "$file")
		# Check if the second line starts with "% Version"
		if [[ $second_line == "% Version"* ]]; then
			# Read the first line, strip the "%" character, and trim whitespace
			sed -n "1p" "$file" | sed "s/^%//;s/^[[:space:]]*//;s/[[:space:]]*$//"
		fi
	}
	export -f _process_contents_file

	# Recursively search for Contents.m files, excluding specific directories and paths with + or @ symbols
	local results
	results=$(find "$MATLAB_ROOT" -type f -name "Contents.m" \
		! -path "$MATLAB_ROOT/toolbox/local/*" \
		! -path "$MATLAB_ROOT/toolbox/matlab/*" \
		! -path "$MATLAB_ROOT/mcr/*" \
		! -path "*/+*" \
		! -path "*/@*" -print0 | xargs -0 -P "$(nproc)" -I {} bash -c '_process_contents_file "$@"' _ {} | sort -u)

	unset -f _process_contents_file

	# Combine MATLAB as the top result if it exists
	if [ -n "$matlab_result" ]; then
		results=$(echo -e "$matlab_result\n$results")
	fi

	echo "$results"
	return 0
}

mw_list_installed_products() {
	local MATLAB_ROOT_ARG=$1

	# Record the start time
	local start_time
	start_time=$(date +%s)

	local MATLAB_ROOT
	if ! MATLAB_ROOT=$(mw_get_matlab_root "$MATLAB_ROOT_ARG"); then
		return 1
	fi

	local matlab_version
	matlab_version=$(mw_get_matlab_version_info "$MATLAB_ROOT")

	local results
	results=$(mw_get_installed_products "$MATLAB_ROOT")

	# Record the end time and calculate duration
	local end_time
	end_time=$(date +%s)
	local elapsed_time
	elapsed_time=$((end_time - start_time))

	# Count the number of unique results
	local num_results
	if [ -z "$results" ]; then
		num_results=0
	else
		num_results=$(echo "$results" | wc -l)
	fi

	# Print the summary
	echo "----------------------"
	if is_verbose_enabled; then
		echo "Summary:"
		echo "Number of Installed Products: $num_results"
		echo "Search Time: ${elapsed_time} seconds"
	fi
	echo "MATLAB Root: $MATLAB_ROOT"
	echo "MATLAB Version: $matlab_version"
	echo "----------------------"

	# Print the unique results
	if [ -n "$results" ]; then
		echo "$results"
	fi

	return 0
}

main_list_installed_products() {
	local MATLAB_ROOT_ARG=""

	while [[ "$#" -gt 0 ]]; do
		case $1 in
		-r | --root)
			MATLAB_ROOT_ARG="$2"
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

	if ! mw_list_installed_products "$MATLAB_ROOT_ARG"; then
		exit 1
	fi
}

# Execute main_list_installed_products only when script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
	main_list_installed_products "$@"
fi
