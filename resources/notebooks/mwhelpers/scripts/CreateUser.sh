#!/usr/bin/env bash
# This script creates the specified user if it does not exist and returns the user ID.
# If the user does not exist, it will create a new user with the specified username
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
	echo "This script creates the specified user if they do not exist."
	echo ""
	echo "Options:"
	echo "  -u, --user <username>   Specify the username to create."
	echo "  -v, --verbose           Enable verbose output."
	echo "  -h, --help              Display this help message and exit."
	echo ""
}

# Create user with sudo privileges and MATLAB directory structure
mw_create_user() {
	local USERNAME=$1
	local SUDOERS_DIR=${2:-/etc/sudoers.d}
	local VALID_USERNAME_REGEX='^[a-z][-a-z0-9_]*\$?$'

	# Check if USERNAME is provided
	if [ -z "$USERNAME" ]; then
		echo "Error: No username provided. Use -u or --user to specify a username." >&2
		return 1
	fi

	# Validate username format
	if ! [[ "$USERNAME" =~ $VALID_USERNAME_REGEX ]]; then
		echo "Error: Invalid username '$USERNAME'." >&2
		echo "Username must start with a lowercase letter followed by lowercase letters, numbers, hyphens, and underscores." >&2
		return 1
	fi

	# Validate username length
	if [[ ${#USERNAME} -gt 32 ]]; then
		echo "Error: Invalid username '$USERNAME'." >&2
		echo "Username must not be more than 32 characters long." >&2
		return 1
	fi

	# Create user if they don't exist
	if ! getent passwd "$USERNAME" >/dev/null; then
		if is_verbose_enabled; then
			echo "User '$USERNAME' not found. Creating..." >&2
		fi
		# Create user, configure sudo access, and set up MATLAB directories
		{
			adduser --shell /bin/bash --disabled-password --gecos "" "$USERNAME" >/dev/null &&
				echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" >"$SUDOERS_DIR/$USERNAME" &&
				chmod 0440 "$SUDOERS_DIR/$USERNAME" &&
				mkdir -p "/home/$USERNAME/Documents/MATLAB" &&
				ln -s "/home/$USERNAME/.gitconfig" "/home/$USERNAME/Documents/MATLAB/.gitconfig" &&
				chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/Documents" &&
				if [ -d "/local_disk0" ]; then
					mkdir -p "/local_disk0/$USERNAME" &&
						chown "$USERNAME:$USERNAME" "/local_disk0/$USERNAME"
				fi
		} || {
			echo "Error: Failed to create user '$USERNAME'." >&2
			return 1
		}
	fi

	# Output user information
	USER_UID=$(id -u "$USERNAME")
	echo "USERNAME: $USERNAME"
	echo "UID: $USER_UID"
	return 0
}

# Parse command-line arguments and execute user creation
main_create_user() {
	local USERNAME=""

	# Process command-line arguments
	while [[ "$#" -gt 0 ]]; do
		case $1 in
		-u | --user)
			USERNAME="$2"
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

	# Create the user
	if ! mw_create_user "$USERNAME"; then
		exit 1
	fi
}

# Execute main_create_user only when script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
	main_create_user "$@"
fi
