#!/usr/bin/env bats
# shellcheck disable=SC2317,SC2329
#------------------------------------------------------------------------------
# Copyright 2025-2026 The MathWorks, Inc.
#------------------------------------------------------------------------------

load "${SOURCE_SCRIPTS_DIR}/CreateUser.sh"

bats_load_library bats-support
bats_load_library bats-assert

# Create temporary workspace before all tests
setup_file() {
	export BATS_TEST_TMPDIR="$BATS_FILE_TMPDIR/test_workspace"
	mkdir -p "$BATS_TEST_TMPDIR"
}

# Clean up temporary workspace after all tests
teardown_file() {
	rm -rf "$BATS_TEST_TMPDIR"
}

#------------------------------------------------------------------------------
# Mocks
#------------------------------------------------------------------------------

# Setup mock paths
setup_path_mocks() {
	SUDOERS_DIR_MOCK="$BATS_TEST_TMPDIR/sudoers.d"
	COMMAND_LOG="$BATS_TEST_TMPDIR/command.log"
	mkdir -p "$SUDOERS_DIR_MOCK"
	touch "$COMMAND_LOG"
}

# Cleanup mock paths
teardown_path_mocks() {
	rm -rf "$SUDOERS_DIR_MOCK"
	rm -f "$COMMAND_LOG"
}

# Create mock system commands
create_system_mocks() {
	# Simulate user does not exist
	getent() { return 1; }
	id() { echo "1001"; }

	# Cannot create users in tests, so log it
	adduser() {
		echo "adduser $*" >>"$COMMAND_LOG"
		return 0
	}

	# Changing ownership requires root, so log it
	chown() {
		echo "chown $*" >>"$COMMAND_LOG"
		return 0
	}

	chmod() { return 0; }
	mkdir() { return 0; }
	ln() { return 0; }
}

# Mock mw_create_user function
create_mw_create_user_mock() {
	mw_create_user() {
		echo "mw_create_user called with user: '$1'"
		if [[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]; then
			echo "VERBOSE_OUTPUT was set to 1"
		fi
		return 0
	}
}

#------------------------------------------------------------------------------
# Tests: mw_create_user
#------------------------------------------------------------------------------

# bats test_tags=mw_create_user
@test "mw_create_user: fails if no username is provided" {
	run mw_create_user ""
	assert_failure
	assert_output --partial "Error: No username provided."
}

# bats test_tags=mw_create_user
@test "mw_create_user: fails for invalid username starting with a number" {
	run mw_create_user "123user"
	assert_failure
	assert_output --partial "Error: Invalid username '123user'."
	assert_output --partial "Username must start with a lowercase letter"
}

# bats test_tags=mw_create_user
@test "mw_create_user: fails for invalid username with uppercase letters" {
	run mw_create_user "InvalidUser"
	assert_failure
	assert_output --partial "Error: Invalid username 'InvalidUser'."
}

# bats test_tags=mw_create_user
@test "mw_create_user: fails for invalid username with special characters" {
	run mw_create_user "user.name"
	assert_failure
	assert_output --partial "Error: Invalid username 'user.name'."
}

# bats test_tags=mw_create_user
@test "mw_create_user: fails for invalid username formatted like an email" {
	run mw_create_user "user@example.com"
	assert_failure
	assert_output --partial "Error: Invalid username 'user@example.com'."
}

# bats test_tags=mw_create_user
@test "mw_create_user: fails for username longer than 32 characters" {
	local long_username="user123456789012345678901234567890"
	run mw_create_user "$long_username"
	assert_failure
	assert_output --partial "Error: Invalid username '$long_username'."
	assert_output --partial "Username must not be more than 32 characters long."
}

# bats test_tags=mw_create_user
@test "mw_create_user: creates a new user" {
	setup_path_mocks
	create_system_mocks
	local username="newuser"
	local sudoer_file="$SUDOERS_DIR_MOCK/$username"

	VERBOSE_OUTPUT=1 run mw_create_user "$username" "$SUDOERS_DIR_MOCK"

	assert_success
	assert_output --partial "User '$username' not found. Creating..."
	assert_output --partial "USERNAME: $username"
	assert_output --partial "UID: 1001"

	run cat "$COMMAND_LOG"
	# user creation
	assert_output --partial "adduser"
	assert_output --partial "$username"
	# home directory ownership
	assert_output --partial "chown"
	assert_output --partial "$username:$username"
	# sudo config
	assert [ -f "$sudoer_file" ]
	run cat "$sudoer_file"
	assert_output "$username ALL=(ALL) NOPASSWD: ALL"
}

# bats test_tags=mw_create_user
@test "mw_create_user: does not create user if they already exist" {
	setup_path_mocks
	create_system_mocks
	# Simulate existing user
	getent() { return 0; }
	id() { echo "505"; }

	run mw_create_user "existinguser" "$SUDOERS_DIR_MOCK"

	assert_success
	assert_output --partial "USERNAME: existinguser"
	assert_output --partial "UID: 505"
	# no side effects
	assert [ ! -f "$SUDOERS_DIR_MOCK/existinguser" ]
}

#------------------------------------------------------------------------------
# Tests: main_create_user
#------------------------------------------------------------------------------

# bats test_tags=main_create_user
@test "main_create_user: displays help with -h or --help" {
	run main_create_user -h
	assert_success
	assert_output --partial "This script creates the specified user"

	run main_create_user --help
	assert_success
	assert_output --partial "This script creates the specified user"
}

# bats test_tags=main_create_user
@test "main_create_user: fails on unknown option" {
	run main_create_user --bad-option
	assert_failure
	assert_output --partial "Unknown parameter passed: --bad-option"
}

# bats test_tags=main_create_user
@test "main_create_user: calls mw_create_user with correct username from -u or --username" {
	create_mw_create_user_mock

	run main_create_user -u testuser
	assert_success
	assert_output --partial "mw_create_user called with user: 'testuser'"

	run main_create_user --user testuser
	assert_success
	assert_output --partial "mw_create_user called with user: 'testuser'"
}

# bats test_tags=main_create_user
@test "main_create_user: sets VERBOSE_OUTPUT flag with -v or --verbose" {
	create_mw_create_user_mock

	run main_create_user -v -u verboseuser
	assert_success
	assert_output --partial "VERBOSE_OUTPUT was set to 1"

	run main_create_user --verbose -u verboseuser
	assert_success
	assert_output --partial "VERBOSE_OUTPUT was set to 1"
}

# bats test_tags=main_create_user
@test "main_create_user: fails if mw_create_user fails" {
	mw_create_user() {
		echo "mw_create_user failed" >&2
		return 1
	}

	run main_create_user -u testuser
	assert_failure
	assert_output --partial "mw_create_user failed"
}
