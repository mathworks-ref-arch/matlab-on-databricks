# Copyright 2026 The MathWorks, Inc.

import logging
import stat

import helper
import pytest

logger = logging.getLogger(__name__)

MSH_INSTALL_ROOT = "/usr/local/MathWorks/ServiceHost/"


@pytest.mark.parametrize(
    "docker_host",
    [{"licensed": True, "command": "matlab", "wait_for": "MATLAB"}],
    indirect=True,
)
class TestMSHIntegration:
    @pytest.fixture(scope="class")
    @classmethod
    def msh_versioned_root_path(cls, docker_host):
        """
        Fixture to dynamically locate the versioned MSH directory.

        Returns:
            str: The full path to the versioned MSH directory.
        """
        logger.info(f"Locating MSH versioned root directory in {MSH_INSTALL_ROOT}...")
        base_dir = docker_host.file(MSH_INSTALL_ROOT)

        if not base_dir.is_directory:
            error_msg = f"MSH base directory not found at {MSH_INSTALL_ROOT}"
            logger.error(error_msg)
            pytest.fail(error_msg)

        version_dirs = [d for d in base_dir.listdir() if d.startswith("v")]

        if len(version_dirs) != 1:
            error_msg = f"Expected exactly one version directory in {MSH_INSTALL_ROOT}, but found {len(version_dirs)}"
            logger.error(error_msg)
            pytest.fail(error_msg)

        full_path = f"{MSH_INSTALL_ROOT}{version_dirs[0]}"
        logger.info(f"Resolved MSH versioned root path: {full_path}")
        return full_path

    @pytest.mark.parametrize(
        "variable, expected_value",
        [
            ("MATHWORKS_SERVICE_HOST_MANAGED_INSTALL_ROOT", MSH_INSTALL_ROOT),
            ("MATHWORKS_SERVICE_HOST_IN_LSF", "1"),
        ],
    )
    def test_msh_env_vars(self, docker_host, variable, expected_value):
        """
        Verify that required MSH environment variables are set correctly.
        """
        actual_value = docker_host.environment().get(variable, "")
        assert actual_value == expected_value, (
            f"Expected {variable}={expected_value}, but got {actual_value}"
        )

    def test_msh_latest_install_info(self, docker_host):
        """
        Verify the existence of the 'LatestInstall.info' file.
        """
        assert docker_host.file(f"{MSH_INSTALL_ROOT}LatestInstall.info").exists

    def test_msh_managed_version(self, docker_host, msh_versioned_root_path):
        """
        Verify that MSH version is managed, which disables auto-update feature.
        """
        managed_lib_path = (
            f"{msh_versioned_root_path}/bin/glnxa64/mathworksservicehost/configuration/"
            "matlabconnector/managed_matlabconnector_configuration/"
            "libmwmshconfigservicehostservicemanaged.so"
        )
        assert docker_host.file(managed_lib_path).exists

    def test_msh_executable(self, docker_host, msh_versioned_root_path):
        """
        Verify that the MathWorksServiceHost binary exists and is executable.
        """
        binary_path = f"{msh_versioned_root_path}/bin/glnxa64/MathWorksServiceHost"
        msh_binary = docker_host.file(binary_path)
        assert msh_binary.is_file, f"MSH binary not found at {binary_path}"
        mode = msh_binary.mode
        assert mode & stat.S_IXUSR, "File is not executable by user"
        assert mode & stat.S_IXGRP, "File is not executable by group"
        assert mode & stat.S_IXOTH, "File is not executable by others"

    def test_msh_process_is_running(self, docker_host, matlab_release):
        """
        Verify that the MathWorksServiceHost process is running.
        """
        if matlab_release == "R2023b":
            pytest.skip("MathWorksServiceHost process not available in R2023b")
        msh_process_substr = "MathWorksServiceHost service"
        try:
            helper.wait_for_process(docker_host, msh_process_substr)
        except ValueError as e:
            pytest.fail(f"'{msh_process_substr}' is not running. Raised exception {e}")
