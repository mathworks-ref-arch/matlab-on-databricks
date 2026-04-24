# Copyright 2026 The MathWorks, Inc.

import pytest


@pytest.mark.parametrize("docker_host", [{"command": "sleep infinity"}], indirect=True)
class TestContainer:
    @pytest.mark.parametrize(
        "package",
        [
            "wget",
            "curl",
            "unzip",
            "ca-certificates",
            "xvfb",
            "git",
            "fluxbox",
            "python3",
        ],
    )
    def test_system_packages(self, docker_host, package):
        """
        Verifies that essential system packages are installed.
        """
        assert docker_host.package(package).is_installed

    @pytest.mark.parametrize("package", ["matlab-proxy", "ipywidgets", "matlabengine"])
    def test_python_packages(
        self,
        docker_host,
        package,
        databricks_python_path,
        matlab_release,
        databricks_runtime,
    ):
        """
        Verifies that required Python packages are installed in the Databricks Python environment.
        """
        if package == "matlabengine":
            # DBR 16.4+ uses Python 3.12 which might not be supported by older engines or specific releases
            if (
                matlab_release in ["R2023b", "R2024a"]
                and float(databricks_runtime) >= 16.4
            ):
                pytest.skip(
                    f"Skipping matlabengine check: Not supported on {matlab_release} with Python 3.12 on DBR 16.4+"
                )
        installed_packages = docker_host.pip.get_packages(
            pip_path=f"{databricks_python_path}/pip3"
        )
        assert package in installed_packages, f"{package} is not installed"

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

    def test_ddux(self, docker_host):
        """
        Verifies the DDUX environment variable.
        """
        expected_value = "MATLAB_PROXY:DATABRICKS:V1"
        actual_value = docker_host.environment().get("MW_CONTEXT_TAGS", "")
        assert actual_value == expected_value, (
            f"Expected MW_CONTEXT_TAGS={expected_value}, but got {actual_value}"
        )

    @pytest.mark.parametrize(
        "env_var",
        [
            "PIP_BREAK_SYSTEM_PACKAGES",
            "PIP_INDEX_URL",
        ],
    )
    def test_env_vars_not_set(self, docker_host, env_var):
        """
        Verifies that PIP env vars are unset or empty.
        """
        value = docker_host.environment().get(env_var, "")
        assert value == "", f"Expected {env_var} to be unset or empty, but got {value}"

    def test_databricks_runtime(self, docker_host, databricks_runtime):
        """
        Verifies the Databricks Runtime version environment variable.
        """
        actual_value = docker_host.environment().get("DATABRICKS_RUNTIME_VERSION", "")
        assert actual_value == databricks_runtime, (
            f"Expected DATABRICKS_RUNTIME_VERSION={databricks_runtime}, but got {actual_value}"
        )

    def test_ld_lib_path(self, docker_host, matlab_release):
        """
        Verifies that LD_LIBRARY_PATH is correctly set for MATLAB runtime.
        """
        matlab_install_location = f"/opt/matlab/{matlab_release}"
        expected_value = f"{matlab_install_location}/runtime/glnxa64:{matlab_install_location}/bin/glnxa64:{matlab_install_location}/sys/os/glnxa64:{matlab_install_location}/extern/bin/glnxa64:{matlab_install_location}/sys/opengl/lib/glnxa64"
        actual_value = docker_host.environment().get("LD_LIBRARY_PATH", "")
        assert actual_value == expected_value, (
            f"Expected LD_LIBRARY_PATH={expected_value}, but got {actual_value}"
        )

    def test_working_directory(self, docker_host):
        """
        Verifies that the working directory is set to /root.
        """
        assert docker_host.check_output("pwd") == "/root"

    def test_mpm_is_installed(self, docker_host):
        """
        Verifies that the MATLAB Package Manager (mpm) binary is available on the PATH.
        """
        assert docker_host.file("/usr/local/bin/mpm").exists, (
            "mpm binary not found at /usr/local/bin/mpm"
        )

    def test_matlab_installation_directory(self, docker_host, matlab_release):
        """
        Verifies that MATLAB is installed in the expected directory.
        """
        matlab_install_location = f"/opt/matlab/{matlab_release}"
        assert docker_host.file(matlab_install_location).is_directory, (
            f"MATLAB installation directory not found at {matlab_install_location}"
        )

    def test_matlab_binary_is_symlinked(self, docker_host):
        """
        Verifies that the matlab binary is symlinked to /usr/local/bin/matlab.
        """
        matlab_link = docker_host.file("/usr/local/bin/matlab")
        assert matlab_link.exists, "matlab symlink not found at /usr/local/bin/matlab"
        assert matlab_link.is_symlink, "/usr/local/bin/matlab should be a symlink"
