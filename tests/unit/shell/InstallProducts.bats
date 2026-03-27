#!/usr/bin/env bats
# shellcheck disable=SC2317,SC2329
#------------------------------------------------------------------------------
# Copyright 2026 The MathWorks, Inc.
#------------------------------------------------------------------------------

load "${SOURCE_SCRIPTS_DIR}/InstallProducts.sh"

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
	MATLAB_ROOT_MOCK="$BATS_TEST_TMPDIR/matlab"
	MATLAB_BIN_MOCK="$MATLAB_ROOT_MOCK/bin"
	mkdir -p "$MATLAB_BIN_MOCK"
}

# Cleanup mock paths
teardown_path_mocks() {
	rm -rf "$MATLAB_ROOT_MOCK"
}

# Create mock system commands
create_system_mocks() {
	chmod() { return 0; }
	# default commands to fail
	wget() { return 1; }
	which() { return 1; }
	readlink() { return 1; }
}

# Mock internal functions
create_internal_mocks() {
	mw_get_matlab_root() {
		echo "$MATLAB_ROOT_MOCK"
		return 0
	}
	mw_install_products() {
		echo "mw_install_products called with $*"
		if [[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]; then
			echo "VERBOSE_OUTPUT was set to 1"
		fi
		return 0
	}
}

#------------------------------------------------------------------------------
# Tests: mw_get_matlab_root
#------------------------------------------------------------------------------

# bats test_tags=mw_get_matlab_root
@test "mw_get_matlab_root: returns explicit path if provided" {
	setup_path_mocks

	run mw_get_matlab_root "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output "$MATLAB_ROOT_MOCK"

	teardown_path_mocks
}

# bats test_tags=mw_get_matlab_root
@test "mw_get_matlab_root: finds MATLAB path from system path" {
	setup_path_mocks
	create_system_mocks
	# Simulate finding matlab on path
	which() {
		if [[ "$1" == "matlab" ]]; then
			echo "$MATLAB_BIN_MOCK/matlab"
			return 0
		fi
		return 1
	}
	# Return path to mock matlab executable
	readlink() {
		echo "$MATLAB_BIN_MOCK/matlab"
	}

	run mw_get_matlab_root ""
	assert_success
	assert_output "$MATLAB_ROOT_MOCK"

	teardown_path_mocks
}

# bats test_tags=mw_get_matlab_root
@test "mw_get_matlab_root: fails if MATLAB is not on PATH" {
	create_system_mocks

	run mw_get_matlab_root ""
	assert_failure
	assert_output --partial "Error: MATLAB not found on PATH"
}

# bats test_tags=mw_get_matlab_root
@test "mw_get_matlab_root: fails if explicit path is not a directory" {
	run mw_get_matlab_root "/non/existent/path"
	assert_failure
	assert_output --partial "Error: Directory does not exist"
}

#------------------------------------------------------------------------------
# Tests: mw_install_products
#------------------------------------------------------------------------------

# bats test_tags=mw_install_products
@test "mw_install_products: fails if no products are specified" {
	setup_path_mocks

	run mw_install_products "$MATLAB_ROOT_MOCK" "" "R2025b"
	assert_failure
	assert_output --partial "No products specified"

	teardown_path_mocks
}

# bats test_tags=mw_install_products
@test "mw_install_products: fails if no release is specified" {
	setup_path_mocks

	run mw_install_products "$MATLAB_ROOT_MOCK" "Simulink" ""
	assert_failure
	assert_output --partial "No MATLAB release specified"

	teardown_path_mocks
}

# bats test_tags=mw_install_products
@test "mw_install_products: fails if wget fails" {
	setup_path_mocks
	create_system_mocks

	run mw_install_products "$MATLAB_ROOT_MOCK" "Simulink" "R2025b"
	assert_failure
	assert_output --partial "Error: Failed to download MPM."

	teardown_path_mocks
}

# bats test_tags=mw_install_products
@test "mw_install_products: fails if mpm install fails" {
	setup_path_mocks
	create_system_mocks
	# mock wget to download mpm successfully,
	# but mpm script fails when run
	wget() {
		cat <<EOF >mpm
#!/bin/bash
echo "Simulating mpm failure" >&2
exit 1
EOF
		command chmod +x mpm
		return 0
	}

	run mw_install_products "$MATLAB_ROOT_MOCK" "Simulink" "R2025b"
	assert_failure
	assert_output --partial "Error: mpm installation failed."
	assert_output --partial "Simulating mpm failure"
	# cleanup mpm file
	assert [ ! -f "mpm" ]

	teardown_path_mocks
}

# bats test_tags=mw_install_products
@test "mw_install_products: successfully installs products" {
	setup_path_mocks
	create_system_mocks
	local MPM_LOG="$BATS_TEST_TMPDIR/mpm_args.log"
	# mock wget to download mpm successfully,
	# and mpm script succeeds when run
	wget() {
		cat <<EOF >mpm
#!/bin/bash
echo "\$*" >> "$MPM_LOG"
EOF
		command chmod +x mpm
		return 0
	}

	VERBOSE_OUTPUT=1 run mw_install_products "$MATLAB_ROOT_MOCK" "Simulink" "R2025b"
	assert_success
	assert_output --partial "Installing products: Simulink"
	assert_output --partial "Installation complete."
	assert [ -f "$MPM_LOG" ]
	run cat "$MPM_LOG"
	assert_output --partial "install --destination $MATLAB_ROOT_MOCK --products Simulink --release R2025b"

	teardown_path_mocks
}

#------------------------------------------------------------------------------
# Tests: main_install_products
#------------------------------------------------------------------------------

# bats test_tags=main_install_products
@test "main_install_products: displays help with -h or --help" {
	run main_install_products -h
	assert_success
	assert_output --partial "This script installs toolboxes into the specified MATLAB root directory."

	run main_install_products --help
	assert_success
	assert_output --partial "This script installs toolboxes into the specified MATLAB root directory."
}

# bats test_tags=main_install_products
@test "main_install_products: fails on unknown option" {
	run main_install_products --bad-option
	assert_failure
	assert_output --partial "Unknown parameter passed: --bad-option"
}

# bats test_tags=main_install_products
@test "main_install_products: calls functions with correct arguments" {
	setup_path_mocks
	create_internal_mocks

	run main_install_products -d "$MATLAB_ROOT_MOCK" -p "Simulink" -r R2025b
	assert_success
	assert_output --partial "mw_install_products called with $MATLAB_ROOT_MOCK Simulink R2025b"

	run main_install_products --destination "$MATLAB_ROOT_MOCK" --products "Simulink" --release R2025b
	assert_success
	assert_output --partial "mw_install_products called with $MATLAB_ROOT_MOCK Simulink R2025b"

	teardown_path_mocks
}

# bats test_tags=main_install_products
@test "main_install_products: sets VERBOSE_OUTPUT flag with -v or --verbose" {
	setup_path_mocks
	create_internal_mocks

	run main_install_products -v -p "Simulink"
	assert_success
	assert_output --partial "VERBOSE_OUTPUT was set to 1"

	run main_install_products --verbose -p "Simulink"
	assert_success
	assert_output --partial "VERBOSE_OUTPUT was set to 1"

	teardown_path_mocks
}

# bats test_tags=main_install_products
@test "main_install_products: fails if mw_get_matlab_root fails" {
	setup_path_mocks
	mw_get_matlab_root() {
		echo "mw_get_matlab_root failed" >&2
		return 1
	}

	run main_install_products -d "$MATLAB_ROOT_MOCK"
	assert_failure

	teardown_path_mocks
}

# bats test_tags=main_install_products
@test "main_install_products: fails if mw_install_products fails" {
	setup_path_mocks
	create_internal_mocks
	mw_install_products() {
		echo "mw_install_products failed" >&2
		return 1
	}

	run main_install_products -p "Simulink"
	assert_failure
	assert_output --partial "mw_install_products failed"

	teardown_path_mocks
}
