#!/usr/bin/env bats
# shellcheck disable=SC2317,SC2329
#------------------------------------------------------------------------------
# Copyright 2026 The MathWorks, Inc.
#------------------------------------------------------------------------------

load "${SOURCE_SCRIPTS_DIR}/ListInstalledProducts.sh"

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
setup_matlab_path_mock() {
	MATLAB_ROOT_MOCK="$BATS_TEST_TMPDIR/matlab"
	mkdir -p "$MATLAB_ROOT_MOCK"
}

# Cleanup mock paths
teardown_matlab_path_mock() {
	rm -rf "$MATLAB_ROOT_MOCK"
}

# Create mock version info file
create_version_info_mock() {
	local version="${1:-25.2.0.2986527}"
	local release="${2:-R2025b}"
	local description="${3:-Update 2}"

	cat <<EOF >"$MATLAB_ROOT_MOCK/VersionInfo.xml"
<?xml version="1.0" encoding="UTF-8"?>
<MathWorks_version_info>
  <version>$version</version>
  <release>$release</release>
  <description>$description</description>
</MathWorks_version_info>
EOF
}

# Create mock product entry
create_product_mock() {
	local relative_path="$1"
	local product_name="$2"
	local version="$3"
	local full_path="$MATLAB_ROOT_MOCK/$relative_path"

	mkdir -p "$full_path"
	echo "% $product_name" >"$full_path/Contents.m"
	if [[ -n "$version" ]]; then
		echo "% Version $version" >>"$full_path/Contents.m"
	fi
}

# Mock mw_list_installed_products function
create_mw_list_installed_products_mock() {
	mw_list_installed_products() {
		echo "mw_list_installed_products called with: $*"
		if [[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]; then
			echo "VERBOSE_OUTPUT was set to 1"
		fi
		return 0
	}
}

#------------------------------------------------------------------------------
# Tests: mw_get_matlab_version_info
#------------------------------------------------------------------------------

# bats test_tags=mw_get_matlab_version_info
@test "mw_get_matlab_version_info: successfully parses VersionInfo.xml" {
	setup_matlab_path_mock
	create_version_info_mock "25.2.0.2986527" "R2025b" "Update 2"

	run mw_get_matlab_version_info "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output "R2025b Update 2 (25.2.0.2986527)"

	teardown_matlab_path_mock
}

# bats test_tags=mw_get_matlab_version_info
@test "mw_get_matlab_version_info: returns 'Unknown' if VersionInfo.xml is missing" {
	setup_matlab_path_mock

	VERBOSE_OUTPUT=1 run mw_get_matlab_version_info "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output --partial "Warning: VersionInfo.xml not found"
	assert_output --partial "Unknown"

	teardown_matlab_path_mock
}

#------------------------------------------------------------------------------
# Tests: mw_get_installed_products
#------------------------------------------------------------------------------

# bats test_tags=mw_get_installed_products
@test "mw_get_installed_products: finds valid products" {
	setup_matlab_path_mock
	create_product_mock "toolbox/simulink" "Simulink" "10.0"
	create_product_mock "toolbox/signal" "Signal Processing Toolbox" "9.0"

	run mw_get_installed_products "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output --partial "Simulink"
	assert_output --partial "Signal Processing Toolbox"

	teardown_matlab_path_mock
}

# bats test_tags=mw_get_installed_products
@test "mw_get_installed_products: includes MATLAB if present in standard location" {
	setup_matlab_path_mock
	create_product_mock "toolbox/matlab/general" "MATLAB" ""

	run mw_get_installed_products "$MATLAB_ROOT_MOCK"
	assert_success
	# MATLAB should be listed first
	assert_line --index 0 "MATLAB"

	teardown_matlab_path_mock
}

# bats test_tags=mw_get_installed_products
@test "mw_get_installed_products: excludes mcr and local directories" {
	setup_matlab_path_mock
	# These paths are explicitly excluded in find command
	create_product_mock "toolbox/local" "Local Toolbox" "1.0"
	create_product_mock "mcr/v913" "MCR Product" "1.0"
	# toolbox/matlab/* is excluded from find,
	# but MATLAB is added manually if general/Contents.m exists.
	create_product_mock "toolbox/matlab/other" "Other MATLAB Component" "1.0"

	run mw_get_installed_products "$MATLAB_ROOT_MOCK"
	assert_success
	refute_output --partial "Local Toolbox"
	refute_output --partial "MCR Product"
	refute_output --partial "Other MATLAB Component"

	teardown_matlab_path_mock
}

# bats test_tags=mw_get_installed_products
@test "mw_get_installed_products: excludes packages (+) and classes (@)" {
	setup_matlab_path_mock
	create_product_mock "toolbox/pkg/+internal" "Internal Package" "1.0"
	create_product_mock "toolbox/pkg/@myclass" "Class Folder" "1.0"

	run mw_get_installed_products "$MATLAB_ROOT_MOCK"
	assert_success
	refute_output --partial "Internal Package"
	refute_output --partial "Class Folder"

	teardown_matlab_path_mock
}

#------------------------------------------------------------------------------
# Tests: mw_list_installed_products
#------------------------------------------------------------------------------

# bats test_tags=mw_list_installed_products
@test "mw_list_installed_products: generates correct output" {
	setup_matlab_path_mock
	mw_get_matlab_root() { echo "$MATLAB_ROOT_MOCK"; }
	mw_get_matlab_version_info() { echo "R2025b Mock Version"; }
	mw_get_installed_products() { echo -e "MATLAB\nSimulink"; }

	run mw_list_installed_products "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output --partial "MATLAB Root: $MATLAB_ROOT_MOCK"
	assert_output --partial "MATLAB Version: R2025b Mock Version"
	assert_output --partial "MATLAB"
	assert_output --partial "Simulink"
	# ensure summary is not present by default
	refute_output --partial "Number of Installed Products"

	teardown_matlab_path_mock
}

# bats test_tags=mw_list_installed_products
@test "mw_list_installed_products: includes summary in verbose mode" {
	setup_matlab_path_mock
	mw_get_matlab_root() { echo "$MATLAB_ROOT_MOCK"; }
	mw_get_matlab_version_info() { echo "R2025b Mock Version"; }
	mw_get_installed_products() { echo -e "MATLAB\nSimulink"; }

	VERBOSE_OUTPUT=1 run mw_list_installed_products "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output --partial "Summary:"
	assert_output --partial "Number of Installed Products: 2"
	assert_output --regexp "Search Time: [0-9]+ seconds"

	teardown_matlab_path_mock
}

#------------------------------------------------------------------------------
# Tests: main_list_installed_products
#------------------------------------------------------------------------------

# bats test_tags=main_list_installed_products
@test "main_list_installed_products: displays help with -h or --help" {
	run main_list_installed_products -h
	assert_success
	assert_output --partial "This script lists all toolboxes installed"

	run main_list_installed_products --help
	assert_success
	assert_output --partial "This script lists all toolboxes installed"
}

# bats test_tags=main_list_installed_products
@test "main_list_installed_products: fails on unknown option" {
	run main_list_installed_products --bad-option
	assert_failure
	assert_output --partial "Unknown parameter passed: --bad-option"
}

# bats test_tags=main_list_installed_products
@test "main_list_installed_products: calls function with correct arguments" {
	setup_matlab_path_mock
	create_mw_list_installed_products_mock

	run main_list_installed_products -r "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output --partial "mw_list_installed_products called with: $MATLAB_ROOT_MOCK"

	run main_list_installed_products --root "$MATLAB_ROOT_MOCK"
	assert_success
	assert_output --partial "mw_list_installed_products called with: $MATLAB_ROOT_MOCK"

	teardown_matlab_path_mock
}

# bats test_tags=main_list_installed_products
@test "main_list_installed_products: sets VERBOSE_OUTPUT flag with -v or --verbose" {
	create_mw_list_installed_products_mock

	run main_list_installed_products -v
	assert_success
	assert_output --partial "VERBOSE_OUTPUT was set to 1"

	run main_list_installed_products --verbose
	assert_success
	assert_output --partial "VERBOSE_OUTPUT was set to 1"
}

# bats test_tags=main_list_installed_products
@test "main_list_installed_products: fails if mw_list_installed_products fails" {
	# Override mock to simulate failure
	mw_list_installed_products() {
		echo "mw_list_installed_products failed" >&2
		return 1
	}

	run main_list_installed_products
	assert_failure
	assert_output --partial "mw_list_installed_products failed"
}
