# Copyright 2026 The MathWorks, Inc.

import logging
from pathlib import Path

import helper
import pytest

logger = logging.getLogger(__name__)

LOCAL_SOURCE_DIR = Path(__file__).parents[3] / "resources"
CONTAINER_SOURCE_DIR = "/opt/resources"

LOCAL_TEST_DIR = Path(__file__).parent / "python_tests"
CONTAINER_TEST_DIR = "/opt/python_tests"

CONTAINER_VOLUME = {
    str(LOCAL_SOURCE_DIR): {"bind": CONTAINER_SOURCE_DIR, "mode": "ro"},
    str(LOCAL_TEST_DIR): {"bind": CONTAINER_TEST_DIR, "mode": "ro"},
}

CONTAINER_ENV = {"PYTHONPATH": f"/opt:{CONTAINER_TEST_DIR}"}


def _discover(filename):
    """Discover test_* functions from a local test file for parametrize."""
    return helper.discover_test_functions(LOCAL_TEST_DIR / filename)


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "licensed": True,
            "set_release": True,
            "volumes": CONTAINER_VOLUME,
            "environment": CONTAINER_ENV,
            "command": "sleep infinity",
        }
    ],
    indirect=True,
)
class TestMATLAB:
    @pytest.mark.parametrize("test_function", _discover("matlab_in_container_tests.py"))
    def test_matlab_in_container(
        self, docker_host, databricks_python_path, test_function
    ):
        result = helper.run_python_function(
            host=docker_host,
            test_file="matlab_in_container_tests",
            function_name=test_function,
            python_bin_path=databricks_python_path,
        )
        assert result.exit_status == 0, (
            f"{test_function} failed:\n{result.stdout}\n{result.stderr}"
        )


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "volumes": CONTAINER_VOLUME,
            "environment": CONTAINER_ENV,
            "command": "sleep infinity",
        }
    ],
    indirect=True,
)
class TestMATLABProxy:
    @pytest.mark.parametrize(
        "test_function", _discover("matlab_proxy_in_container_tests.py")
    )
    def test_matlab_proxy_in_container(
        self, docker_host, databricks_python_path, test_function
    ):
        result = helper.run_python_function(
            host=docker_host,
            test_file="matlab_proxy_in_container_tests",
            function_name=test_function,
            python_bin_path=databricks_python_path,
        )
        assert result.exit_status == 0, (
            f"{test_function} failed:\n{result.stdout}\n{result.stderr}"
        )


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "volumes": CONTAINER_VOLUME,
            "environment": CONTAINER_ENV,
            "command": "sleep infinity",
        }
    ],
    indirect=True,
)
class TestUser:
    @pytest.mark.parametrize("test_function", _discover("user_in_container_tests.py"))
    def test_user_in_container(
        self, docker_host, databricks_python_path, test_function
    ):
        result = helper.run_python_function(
            host=docker_host,
            test_file="user_in_container_tests",
            function_name=test_function,
            python_bin_path=databricks_python_path,
        )
        assert result.exit_status == 0, (
            f"{test_function} failed:\n{result.stdout}\n{result.stderr}"
        )
