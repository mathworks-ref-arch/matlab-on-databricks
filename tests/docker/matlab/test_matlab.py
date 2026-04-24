# Copyright 2026 The MathWorks, Inc.

import re
from pathlib import Path

import helper
import pytest

LOCAL_TEST_DIR = Path(__file__).parent / "matlab_tests"
CONTAINER_TEST_DIR = "/opt/matlab_tests"
CONTAINER_LICENSE_PATH = "/licenses/license.dat"


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "licensed": True,
            "volumes": {
                str(LOCAL_TEST_DIR): {"bind": CONTAINER_TEST_DIR, "mode": "ro"},
            },
            "command": "sleep infinity",
        }
    ],
    indirect=True,
)
class TestLicensedMATLAB:
    def test_matlab_license(self, docker_host):
        """
        Verify that the license file environment variable is correctly set.
        """
        actual_value = docker_host.environment().get("MLM_LICENSE_FILE", "")
        assert actual_value == CONTAINER_LICENSE_PATH, (
            f"Expected MLM_LICENSE_FILE={CONTAINER_LICENSE_PATH}, but got {actual_value}"
        )

    def test_matlab_release(self, docker_host, matlab_release):
        """
        Verify that the installed MATLAB release matches the expected release.
        """
        result = helper.run_matlab_code(docker_host, "matlabRelease.Release")
        assert matlab_release in result.stdout, (
            f"Expected MATLAB release {matlab_release} in {result.stdout}"
        )

    def test_matlab_update(self, docker_host, matlab_update):
        """
        Verify that the installed MATLAB update matches the expected update.
        """
        if not matlab_update:
            pytest.skip(
                "No --matlab-update specified; skipping update level verification"
            )
        result = helper.run_matlab_code(docker_host, "matlabRelease.Update")
        expected = re.search(r"\d+", matlab_update).group()
        actual = re.search(r"\d+", result.stdout).group()

        assert expected == actual, (
            f"Expected MATLAB update {expected} in {result.stdout}"
        )

    def test_available_products(self, docker_host):
        """
        Verify that the required MATLAB products are installed.
        """
        result = helper.run_matlab_test(
            docker_host, f"{CONTAINER_TEST_DIR}/InstalledProductsTest.m"
        )
        assert result.exit_status == 0, "Incorrect products installed"

    def test_startup_settings(self, docker_host):
        """
        Verify that startup settings are correctly applied.
        """
        result = helper.run_matlab_test(
            docker_host, f"{CONTAINER_TEST_DIR}/StartupSettingsTest.m"
        )
        assert result.exit_status == 0, "Startup settings verification failed"


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "licensed": False,
            "command": "sleep infinity",
        }
    ],
    indirect=True,
)
class TestUnlicensedMATLAB:
    def test_matlab_fails_without_license(self, docker_host):
        result = helper.run_matlab_code(docker_host, "rand", check=False)
        assert result.exit_status != 0, "MATLAB should fail without a valid license"
