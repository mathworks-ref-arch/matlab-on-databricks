# Copyright 2026 The MathWorks, Inc.

import helper
import pytest

DATABRICKS_PYTHON_BIN = "/databricks/python3/bin"
DEFAULT_MWI_APP_PORT = 8888


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "entrypoint": f"{DATABRICKS_PYTHON_BIN}/matlab-proxy-app",
            "ports": {f"{DEFAULT_MWI_APP_PORT}/tcp": None},
            "wait_for": "matlab-proxy-app",
        }
    ],
    indirect=True,
)
class TestMATLABProxyIntegration:
    @pytest.mark.parametrize(
        "variable,expected_value",
        [
            ("MWI_USE_COOKIE_CACHE", "True"),
            ("MWI_APP_PORT", f"{DEFAULT_MWI_APP_PORT}"),
            ("MWI_BASE_URL", "/matlab"),
            ("MWI_ENABLE_TOKEN_AUTH", "False"),
        ],
    )
    def test_env_vars(self, docker_host, variable, expected_value):
        """
        Verify that specific environment variables are set correctly in the container.
        """
        actual_value = docker_host.environment().get(variable, "")
        assert actual_value == expected_value, (
            f"Expected {variable}={expected_value}, but got {actual_value}"
        )

    def test_listening_port(self, docker_host):
        """
        Verify that the MATLAB Proxy is listening on the expected TCP port.
        """
        try:
            helper.wait_for(
                lambda: docker_host.socket(
                    f"tcp://0.0.0.0:{DEFAULT_MWI_APP_PORT}"
                ).is_listening,
                timeout=30,
                description=f"port {DEFAULT_MWI_APP_PORT} listening",
            )
        except TimeoutError:
            pytest.fail(f"No service is listening on port {DEFAULT_MWI_APP_PORT}")
