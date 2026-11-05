# Copyright 2026 The MathWorks, Inc.

import logging

import pytest
from conftest import (
    TEST_API_TOKEN,
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
        logger = dbx._get_keep_alive_logger(TEST_CLUSTER_ID)
        assert logger.disabled is True
        assert len(logger.handlers) == 0

    def test_logging_enabled_when_env_var_true(self, monkeypatch, mocker):
        monkeypatch.setenv("MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING", "true")
        mocker.patch("resources.notebooks.mwhelpers.dbx.Path.mkdir")
        mock_file_handler = mocker.patch(
            "logging.FileHandler", return_value=logging.NullHandler()
        )
        logger = dbx._get_keep_alive_logger(TEST_CLUSTER_ID)
        assert logger.disabled is False
        assert len(logger.handlers) == 1
        log_file = mock_file_handler.call_args.args[0]
        assert log_file.parent.name == "keep_alive_logs"
        assert log_file.name == f"keep_alive_{TEST_CLUSTER_ID}.log"

    def test_logging_disabled_when_env_var_false(self, monkeypatch):
        monkeypatch.setenv("MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING", "false")
        logger = dbx._get_keep_alive_logger(TEST_CLUSTER_ID)
        assert logger.disabled is True
        assert len(logger.handlers) == 0


class TestActiveSessions:
    def test_lists_user_and_port_of_every_session(self):
        servers_by_user = {
            "alice": ["http://0.0.0.0:3000/matlab", "http://0.0.0.0:3001/matlab"],
            "bob": [],
            "carol": ["http://0.0.0.0:3002/matlab"],
        }

        assert (
            dbx._active_sessions(servers_by_user)
            == "alice:3000, alice:3001, carol:3002"
        )

    def test_returns_empty_string_without_sessions(self):
        assert dbx._active_sessions({"alice": [], "bob": []}) == ""


@pytest.fixture
def mock_servers_by_user(mocker):
    """Mock the servers with idle timeout of every MATLAB user."""

    def _mock(servers_by_user: dict):
        return mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy.list_servers_with_idle_timeout_by_user",
            return_value=servers_by_user,
        )

    return _mock


class TestKeepAliveTick:
    def test_sends_keep_alive_when_any_user_has_a_session(
        self, mocker, mock_servers_by_user
    ):
        mock_servers_by_user({"alice": [], "bob": ["http://0.0.0.0:3000/matlab"]})
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.run_keep_alive_command"
        )
        mock_client = mocker.Mock()
        mock_logger = mocker.Mock()

        dbx._keep_alive_tick(TEST_CLUSTER_ID, mock_client, mock_logger)

        mock_run.assert_called_once_with(
            TEST_CLUSTER_ID,
            workspace_client=mock_client,
            active_sessions="bob:3000",
        )
        mock_logger.info.assert_called_once_with(
            "Active MATLAB session(s) (alice: []; bob: ['http://0.0.0.0:3000/matlab']), "
            "sending keep-alive"
        )

    def test_skips_keep_alive_when_no_user_has_a_session(
        self, mocker, mock_servers_by_user
    ):
        mock_servers_by_user({"alice": [], "bob": []})
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.run_keep_alive_command"
        )
        mock_logger = mocker.Mock()

        dbx._keep_alive_tick(TEST_CLUSTER_ID, mocker.Mock(), mock_logger)

        mock_run.assert_not_called()
        mock_logger.info.assert_called_once_with(
            "No active MATLAB sessions with idle timeout (alice: []; bob: []), "
            "skipping keep-alive"
        )

    def test_skips_keep_alive_when_there_are_no_matlab_users(
        self, mocker, mock_servers_by_user
    ):
        mock_servers_by_user({})
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.run_keep_alive_command"
        )
        mock_logger = mocker.Mock()

        dbx._keep_alive_tick(TEST_CLUSTER_ID, mocker.Mock(), mock_logger)

        mock_run.assert_not_called()
        mock_logger.info.assert_called_once_with(
            "No active MATLAB sessions with idle timeout (no MATLAB users), "
            "skipping keep-alive"
        )


class TestLogKeepAliveStart:
    def test_logs_cluster_name_id_and_interval(self, mocker):
        mock_client = mocker.Mock()
        mock_client.clusters.get.return_value.cluster_name = "my-cluster"
        mock_logger = mocker.Mock()

        dbx._log_keep_alive_start(TEST_CLUSTER_ID, mock_client, mock_logger, 3)

        mock_client.clusters.get.assert_called_once_with(TEST_CLUSTER_ID)
        mock_logger.info.assert_called_once_with(
            f"Keep-alive started (cluster my-cluster, ID {TEST_CLUSTER_ID}, "
            "check interval 3 min)"
        )

    def test_logs_unknown_name_when_lookup_fails(self, mocker):
        mock_client = mocker.Mock()
        mock_client.clusters.get.side_effect = RuntimeError("API unavailable")
        mock_logger = mocker.Mock()

        dbx._log_keep_alive_start(TEST_CLUSTER_ID, mock_client, mock_logger, 3)

        mock_logger.info.assert_called_once_with(
            f"Keep-alive started (cluster unknown, ID {TEST_CLUSTER_ID}, "
            "check interval 3 min)"
        )


class TestStartClusterKeepAlive:
    def test_starts_daemon_thread(self, mocker, mock_databricks_context):
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
        )
        mocker.patch("resources.notebooks.mwhelpers.dbx._log_keep_alive_start")
        thread = dbx.start_cluster_keep_alive(check_interval_minutes=1)
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
        mocker.patch("resources.notebooks.mwhelpers.dbx._log_keep_alive_start")
        thread1 = dbx.start_cluster_keep_alive(check_interval_minutes=1)
        thread2 = dbx.start_cluster_keep_alive(check_interval_minutes=1)
        assert thread1 is thread2

    def test_loop_uses_explicitly_authenticated_client(
        self, mocker, mock_databricks_context
    ):
        """The loop outlives the REPL context, so it must not rely on default auth."""

        class StopLoop(BaseException):
            pass

        mock_get_logger = mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger"
        )
        mock_log_start = mocker.patch(
            "resources.notebooks.mwhelpers.dbx._log_keep_alive_start"
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.threading.enumerate", return_value=[]
        )
        mock_thread_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.threading.Thread"
        )
        mock_client_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient"
        )
        mock_tick = mocker.patch("resources.notebooks.mwhelpers.dbx._keep_alive_tick")
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.time.sleep", side_effect=StopLoop
        )

        dbx.start_cluster_keep_alive(check_interval_minutes=1)

        mock_client_class.assert_called_once_with(
            host=TEST_BROWSER_HOSTNAME, token=TEST_API_TOKEN
        )
        # Run one iteration of the loop on this thread.
        keep_alive_loop = mock_thread_class.call_args.kwargs["target"]
        with pytest.raises(StopLoop):
            keep_alive_loop()
        mock_get_logger.assert_called_once_with(TEST_CLUSTER_ID)
        mock_log_start.assert_called_once_with(
            TEST_CLUSTER_ID,
            mock_client_class.return_value,
            mock_get_logger.return_value,
            1,
        )
        mock_tick.assert_called_once_with(
            TEST_CLUSTER_ID, mock_client_class.return_value, mocker.ANY
        )


class TestRunKeepAliveCommand:
    def test_raises_value_error_if_cluster_id_is_none(self):
        with pytest.raises(ValueError):
            dbx.run_keep_alive_command(cluster_id=None)

    def test_successful_execution_logs_info(self, mocker):
        """Test that successful execution logs info message."""
        mock_logger = mocker.Mock()
        mock_get_logger = mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
            return_value=mock_logger,
        )

        mock_execution_context = mocker.MagicMock()
        mock_execution_context.run_print_command.return_value = "SUCCESS"
        mock_execution_context_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.DatabricksExecutionContext"
        )
        mock_execution_context_class.return_value.__enter__.return_value = (
            mock_execution_context
        )

        cluster_id = "test-cluster-123"

        dbx.run_keep_alive_command(cluster_id=cluster_id, active_sessions="alice:3000")

        mock_execution_context_class.assert_called_once_with(
            cluster_id=cluster_id, workspace_client=None
        )
        mock_execution_context.run_print_command.assert_called_once_with(
            message="MATLAB sessions: alice:3000"
        )
        mock_get_logger.assert_called_once_with(cluster_id)
        mock_logger.info.assert_called_once_with(
            "Command status: SUCCESS (sessions: alice:3000)"
        )
        mock_logger.error.assert_not_called()

    def test_passes_workspace_client_to_execution_context(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.dbx._get_keep_alive_logger")
        mock_execution_context_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.DatabricksExecutionContext"
        )
        mock_client = mocker.Mock()

        dbx.run_keep_alive_command(
            cluster_id=TEST_CLUSTER_ID, workspace_client=mock_client
        )

        mock_execution_context_class.assert_called_once_with(
            cluster_id=TEST_CLUSTER_ID, workspace_client=mock_client
        )

    def test_execution_context_uses_supplied_workspace_client(self, mocker):
        mock_client_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.WorkspaceClient"
        )
        mock_client = mocker.Mock()

        context = dbx.DatabricksExecutionContext(
            cluster_id=TEST_CLUSTER_ID, workspace_client=mock_client
        )

        assert context.workspace_client is mock_client
        mock_client_class.assert_not_called()

    def test_run_print_command_exception_logs_error(self, mocker):
        """Test that exceptions from run_print_command are logged as errors."""
        mock_logger = mocker.Mock()
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx._get_keep_alive_logger",
            return_value=mock_logger,
        )

        mock_context = mocker.MagicMock()
        test_exception = RuntimeError("Command execution failed")
        mock_context.run_print_command.side_effect = test_exception
        mock_context_class = mocker.patch(
            "resources.notebooks.mwhelpers.dbx.DatabricksExecutionContext"
        )
        mock_context_class.return_value.__enter__.return_value = mock_context

        cluster_id = "test-cluster-789"

        dbx.run_keep_alive_command(cluster_id=cluster_id)

        mock_logger.error.assert_called_once_with(
            f"Error running execution command: {test_exception}"
        )
