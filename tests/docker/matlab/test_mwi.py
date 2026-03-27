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


@pytest.mark.parametrize(
    "docker_host",
    [
        {
            "licensed": True,
            "set_release": True,
            "volumes": {
                str(LOCAL_SOURCE_DIR): {"bind": CONTAINER_SOURCE_DIR, "mode": "ro"},
                str(LOCAL_TEST_DIR): {"bind": CONTAINER_TEST_DIR, "mode": "ro"},
            },
            "environment": {
                "PYTHONPATH": "/opt",
            },
            "command": "sleep infinity",
        }
    ],
    indirect=True,
)
class TestMWI:
    def test_mwi_in_container(self, docker_host, databricks_python_path):
        """
        Verifies that mwi functions correctly within the container.
        """
        result = helper.run_python_test(
            host=docker_host,
            test_file_path=f"{CONTAINER_TEST_DIR}/mwi_in_container_tests.py",
            python_bin_path=databricks_python_path,
        )
        assert result.exit_status == 0, "MWI container tests failed"
