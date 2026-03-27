# Copyright 2026 The MathWorks, Inc.

import sys
from unittest.mock import MagicMock

import pytest

# Mock missing databricks modules to prevent ImportErrors.
# This must happen at module level before any test file imports mwhelpers.
sys.modules["databricks"] = MagicMock()
sys.modules["databricks.sdk"] = MagicMock()
sys.modules["databricks.sdk.service"] = MagicMock()
sys.modules["dbruntime"] = MagicMock()
sys.modules["dbruntime.databricks_repl_context"] = MagicMock()
mock_requests = MagicMock()
# Set up real exception classes so `except requests.Timeout:` works in source code.
mock_requests.Timeout = type("Timeout", (Exception,), {})
mock_requests.exceptions.RequestException = type("RequestException", (Exception,), {})
mock_requests.exceptions.Timeout = mock_requests.Timeout
sys.modules["requests"] = mock_requests

TEST_API_TOKEN = "test-token"
TEST_CLUSTER_ID = "test-cluster-id"
TEST_CLUSTER_NAME = "test-cluster"
TEST_BROWSER_HOSTNAME = "test.databricks.com"
TEST_WORKSPACE_ID = "test-workspace-id"
TEST_RUNTIME_VERSION = "16.4.x-scala2.13"


@pytest.fixture
def mock_databricks_context(mocker):
    """Mock the Databricks runtime context."""
    mock_context = mocker.MagicMock()
    mock_context.apiToken = TEST_API_TOKEN
    mock_context.browserHostName = TEST_BROWSER_HOSTNAME
    mock_context.clusterId = TEST_CLUSTER_ID
    mock_context.isInJob = False
    mock_context.workspaceId = TEST_WORKSPACE_ID
    mock_context.runtimeVersion = TEST_RUNTIME_VERSION
    mocker.patch(
        "resources.notebooks.mwhelpers.dbx.get_context",
        return_value=mock_context,
    )
    return mock_context


@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess.run to prevent actual system calls."""
    return mocker.patch("subprocess.run")
