# Copyright 2026 The MathWorks, Inc.

import logging

import pytest
from conftest import (
    TEST_BROWSER_HOSTNAME,
    TEST_CLUSTER_ID,
    TEST_CLUSTER_NAME,
    TEST_WORKSPACE_ID,
)

from resources.notebooks.mwhelpers import dbx


class TestGetContext:
    def test_returns_context_object(self, mock_databricks_context):
        assert dbx.get_context() == mock_databricks_context


class TestGetClusterId:
    def test_returns_cluster_id_from_context(self, mock_databricks_context):
        assert dbx.get_cluster_id() == TEST_CLUSTER_ID


class TestGetClusterName:
    def test_returns_job_cluster_in_job_mode(self, mock_databricks_context):
        mock_databricks_context.isInJob = True
        assert dbx.get_cluster_name() == "Job Cluster"

    def test_returns_cluster_name_in_interactive_mode(
        self, mock_databricks_context, mocker
    ):
        mock_cluster_info = mocker.MagicMock()
        mock_cluster_info.cluster_name = TEST_CLUSTER_NAME
        mock_client_instance = mocker.MagicMock()
        mock_client_instance.clusters.get.return_value = mock_cluster_info
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient",
            return_value=mock_client_instance,
        )

        assert dbx.get_cluster_name() == TEST_CLUSTER_NAME
        mock_client_instance.clusters.get.assert_called_once_with(
            mock_databricks_context.clusterId
        )


class TestGetDataSecurityMode:
    def test_returns_mode_value_when_sdk_returns_enum(
        self, mock_databricks_context, mocker
    ):
        mock_cluster_info = mocker.MagicMock()
        mock_cluster_info.data_security_mode.value = "SINGLE_USER"
        mock_client_instance = mocker.MagicMock()
        mock_client_instance.clusters.get.return_value = mock_cluster_info
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient",
            return_value=mock_client_instance,
        )

        assert dbx.get_cluster_data_security_mode() == "SINGLE_USER"
        mock_client_instance.clusters.get.assert_called_once_with(
            mock_databricks_context.clusterId
        )

    def test_raises_when_data_security_mode_is_none(
        self, mock_databricks_context, mocker
    ):
        mock_cluster_info = mocker.MagicMock()
        mock_cluster_info.data_security_mode = None
        mock_client_instance = mocker.MagicMock()
        mock_client_instance.clusters.get.return_value = mock_cluster_info
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient",
            return_value=mock_client_instance,
        )

        with pytest.raises(AttributeError):
            dbx.get_cluster_data_security_mode()

    def test_raises_when_workspace_client_raises(self, mock_databricks_context, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient",
            side_effect=Exception("auth failed"),
        )

        with pytest.raises(Exception, match="auth failed"):
            dbx.get_cluster_data_security_mode()

    def test_raises_when_clusters_get_raises(self, mock_databricks_context, mocker):
        mock_client_instance = mocker.MagicMock()
        mock_client_instance.clusters.get.side_effect = Exception("cluster not found")
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient",
            return_value=mock_client_instance,
        )

        with pytest.raises(Exception, match="cluster not found"):
            dbx.get_cluster_data_security_mode()

    def test_raises_when_context_is_degraded(self, mocker):
        """Simulate running from a thread where ``get_context()`` yields a
        context whose attributes are ``None`` (e.g. ipywidgets callback
        thread). The SDK call then raises."""
        degraded_context = mocker.MagicMock()
        degraded_context.browserHostName = None
        degraded_context.apiToken = None
        degraded_context.clusterId = None
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.get_context",
            return_value=degraded_context,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient",
            side_effect=Exception("invalid host"),
        )

        with pytest.raises(Exception, match="invalid host"):
            dbx.get_cluster_data_security_mode()


class TestCurrentUserName:
    def test_delegates_to_user_module(self, mock_databricks_context, mocker):
        mock_databricks_context.user = "testuser@company.com"
        to_valid = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.user.to_valid_linux_username",
            return_value="testuser",
        )
        assert dbx.current_user_name() == "testuser"
        to_valid.assert_called_once_with("testuser@company.com")


class TestRuntimeVersion:
    @pytest.mark.parametrize(
        "runtime_version, expected_version",
        [
            ("16.4.x-scala2.13", [16, 4, 0]),
            ("client.1.13-scala2.12", [0, 1, 13]),
        ],
        ids=["standard_runtime", "serverless_runtime"],
    )
    def test_returns_version_list(
        self, mock_databricks_context, runtime_version, expected_version
    ):
        mock_databricks_context.runtimeVersion = runtime_version
        assert dbx.runtime_version() == expected_version


class TestGetUrlToMatlab:
    def test_raises_runtime_error_when_context_in_job_mode(
        self, mock_databricks_context
    ):
        mock_databricks_context.isInJob = True
        with pytest.raises(RuntimeError):
            dbx.get_url_to_matlab(
                session_id=3000, databricks_context=mock_databricks_context
            )

    def test_returns_url_when_context_in_interactive_mode(
        self, mock_databricks_context
    ):
        expected_url = (
            f"https://{TEST_BROWSER_HOSTNAME}/driver-proxy/"
            f"o/{TEST_WORKSPACE_ID}/{TEST_CLUSTER_ID}/3000/matlab/index.html"
        )
        assert (
            dbx.get_url_to_matlab(
                session_id=3000, databricks_context=mock_databricks_context
            )
            == expected_url
        )

    def test_raises_value_error_when_session_id_is_none(self, mock_databricks_context):
        with pytest.raises(ValueError):
            dbx.get_url_to_matlab(
                session_id=None, databricks_context=mock_databricks_context
            )


class TestReservedPorts:
    def test_returns_list_of_reserved_ports(self):
        reserved = dbx._reserved_ports()
        assert isinstance(reserved, list)
        assert len(reserved) > 0
        assert 6060 in reserved


class TestGetKeepAliveLogger:
    @pytest.fixture(autouse=True)
    def _reset_logger(self):
        """Reset the keep-alive logger between tests to avoid singleton state leaking."""
        logger = logging.getLogger("matlab-keep-alive")
        logger.handlers.clear()
        logger.disabled = False
        yield
        logger.handlers.clear()
        logger.disabled = False

    def test_logging_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING", raising=False)
        logger = dbx._get_keep_alive_logger()
        assert logger.disabled is True
        assert len(logger.handlers) == 0

    def test_logging_enabled_when_env_var_true(self, monkeypatch, mocker):
        monkeypatch.setenv("MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING", "true")
        mocker.patch("resources.notebooks.mwhelpers.dbx.Path.mkdir")
        mocker.patch("logging.FileHandler", return_value=logging.NullHandler())
        logger = dbx._get_keep_alive_logger()
        assert logger.disabled is False
        assert len(logger.handlers) == 1

    def test_logging_disabled_when_env_var_false(self, monkeypatch):
        monkeypatch.setenv("MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING", "false")
        logger = dbx._get_keep_alive_logger()
        assert logger.disabled is True
        assert len(logger.handlers) == 0


class TestStartClusterKeepAlive:
    def test_returns_none_when_username_is_empty(self):
        assert dbx.start_cluster_keep_alive(username="") is None
        assert dbx.start_cluster_keep_alive(username=None) is None

    def test_starts_daemon_thread(self, mocker, mock_databricks_context):
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy.list_servers_with_idle_timeout",
            return_value=[],
        )
        thread = dbx.start_cluster_keep_alive(
            username="testuser", check_interval_minutes=1
        )
        assert thread is not None
        assert thread.is_alive()
        assert thread.daemon is True
        assert thread.name == "matlab-keep-alive"

    def test_returns_existing_thread_if_already_running(
        self, mocker, mock_databricks_context
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy.list_servers_with_idle_timeout",
            return_value=[],
        )
        thread1 = dbx.start_cluster_keep_alive(
            username="testuser", check_interval_minutes=1
        )
        thread2 = dbx.start_cluster_keep_alive(
            username="testuser", check_interval_minutes=1
        )
        assert thread1 is thread2


class TestRunKeepAliveCommand:
    def test_raises_value_error_if_cluster_id_is_none(self):
        with pytest.raises(ValueError):
            dbx.run_keep_alive_command(cluster_id=None)

    def test_successful_execution_logs_info(self, mocker):
        """Test that successful execution logs info message."""
        mock_logger = mocker.Mock()
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
            return_value=mock_logger,
        )

        mock_execution_context = mocker.MagicMock()
        mock_execution_context.run_command.return_value = "SUCCESS"
        mock_execution_context_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.DatabricksExecutionContext"
        )
        mock_execution_context_class.return_value.__enter__.return_value = (
            mock_execution_context
        )

        cluster_id = "test-cluster-123"

        dbx.run_keep_alive_command(cluster_id=cluster_id)

        mock_execution_context_class.assert_called_once_with(cluster_id=cluster_id)
        mock_execution_context.run_command.assert_called_once()
        mock_logger.info.assert_called_once_with(
            "Cluster kept alive: command status: SUCCESS"
        )
        mock_logger.error.assert_not_called()

    def test_run_command_exception_logs_error(self, mocker):
        """Test that exceptions from run_command are logged as errors."""
        mock_logger = mocker.Mock()
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
            return_value=mock_logger,
        )

        mock_context = mocker.MagicMock()
        test_exception = RuntimeError("Command execution failed")
        mock_context.run_command.side_effect = test_exception
        mock_context_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.DatabricksExecutionContext"
        )
        mock_context_class.return_value.__enter__.return_value = mock_context

        cluster_id = "test-cluster-789"

        dbx.run_keep_alive_command(cluster_id=cluster_id)

        mock_logger.error.assert_called_once_with(
            f"Error running execution command: {test_exception}"
        )
