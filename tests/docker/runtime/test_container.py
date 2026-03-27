# Copyright 2026 The MathWorks, Inc.

import pytest

MCR_INSTALL_LOCATION = "/MATLAB_Runtime"
LD_LIBRARY_PATH = f"{MCR_INSTALL_LOCATION}/runtime/glnxa64:{MCR_INSTALL_LOCATION}/bin/glnxa64:{MCR_INSTALL_LOCATION}/sys/os/glnxa64:{MCR_INSTALL_LOCATION}/extern/bin/glnxa64:{MCR_INSTALL_LOCATION}/sys/opengl/lib/glnxa64"


@pytest.mark.parametrize("docker_host", [{"command": "sleep infinity"}], indirect=True)
class TestContainer:
    @pytest.mark.parametrize(
        "package",
        [
            "wget",
            "curl",
            "unzip",
            "ca-certificates",
        ],
    )
    def test_system_packages(self, docker_host, package):
        """
        Verifies that essential system packages are installed.
        """
        assert docker_host.package(package).is_installed

    @pytest.mark.parametrize(
        "user",
        [
            "root",
            "ubuntu",
        ],
    )
    def test_users(self, docker_host, user):
        """
        Verifies that expected users exist in the container.
        """
        assert docker_host.user(user).exists

    @pytest.mark.parametrize(
        "variable, expected_value",
        [("MCRROOT", MCR_INSTALL_LOCATION), ("LD_LIBRARY_PATH", LD_LIBRARY_PATH)],
    )
    def test_mcr_env_vars(self, docker_host, variable, expected_value):
        """
        Verify that MCR specific environment variables are set correctly in the container.
        """
        actual_value = docker_host.environment().get(variable, "")
        assert actual_value == expected_value, (
            f"Expected {variable}={expected_value}, but got {actual_value}"
        )

    def test_mcr_version(self, docker_host, matlab_release):
        """
        Verifies the MCR version environment variable.
        """
        actual_value = docker_host.environment().get("MCR_VERSION", "")
        assert actual_value == matlab_release, (
            f"Expected MCR_VERSION={matlab_release}, but got {actual_value}"
        )

    def test_databricks_runtime(self, docker_host, databricks_runtime):
        """
        Verifies the Databricks Runtime version environment variable.
        """
        actual_value = docker_host.environment().get("DATABRICKS_RUNTIME_VERSION", "")
        assert actual_value == databricks_runtime, (
            f"Expected DATABRICKS_RUNTIME_VERSION={databricks_runtime}, but got {actual_value}"
        )

    def test_working_directory(self, docker_host):
        """
        Verifies that the working directory is set to /root.
        """
        assert docker_host.check_output("pwd") == "/root"
