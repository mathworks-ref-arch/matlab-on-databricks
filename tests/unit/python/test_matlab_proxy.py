# Copyright 2026 The MathWorks, Inc.

import pytest

from resources.notebooks.mwhelpers import matlab_proxy


class TestVersion:
    def test_returns_version_string_on_success(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "v0.30.0"
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_result,
        )
        assert matlab_proxy.version(username="testuser") == "v0.30.0"

    def test_returns_none_on_nonzero_exit_code(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mock_result = mocker.Mock()
        mock_result.returncode = 1
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_result,
        )
        assert matlab_proxy.version(username="testuser") is None

    def test_returns_none_on_empty_stdout(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "   "
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_result,
        )
        assert matlab_proxy.version(username="testuser") is None


class TestListServers:
    def test_returns_empty_list_when_username_is_none(self):
        assert matlab_proxy.list_servers_ports(username=None) == []  # type: ignore
        assert matlab_proxy.list_servers_ports(username="") == []

    def test_returns_empty_list_when_user_home_not_found(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            side_effect=RuntimeError("Unable to find home folder"),
        )
        assert matlab_proxy.list_servers_ports(username="baduser") == []

    def test_returns_empty_list_when_script_returns_no_output(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value="",
        )
        assert matlab_proxy.list_servers_ports(username="testuser") == []

    def test_returns_port_list(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mock_return_value = mocker.Mock()
        mock_return_value.returncode = 0
        mock_return_value.stdout = (
            "http://localhost:3000/matlab\nhttp://localhost:3100/matlab"
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_return_value,
        )
        assert matlab_proxy.list_servers_ports(username="testuser") == [
            "3000",
            "3100",
        ]

    def test_private_helper_returns_server_dict(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mock_return_value = mocker.Mock()
        mock_return_value.returncode = 0
        mock_return_value.stdout = "http://localhost:3000/matlab"
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_return_value,
        )
        assert matlab_proxy._list_servers(username="testuser") == {
            "3000": "http://localhost:3000/matlab"
        }


class TestListServersWithIdleTimeout:
    def test_returns_servers_with_idle_timeout(self, mocker):
        servers = {
            "3000": "http://localhost:3000/matlab",
            "3100": "http://localhost:3100/matlab",
        }
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value=servers,
        )
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"idleTimeoutDuration": 3600}
        mocker.patch(
            "resources.notebooks.mwhelpers.web.send_http_request",
            return_value=mock_response,
        )
        result = matlab_proxy.list_servers_with_idle_timeout(username="testuser")
        assert result == [
            "http://localhost:3000/matlab",
            "http://localhost:3100/matlab",
        ]

    def test_returns_empty_list_when_no_servers(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value={},
        )
        assert matlab_proxy.list_servers_with_idle_timeout(username="testuser") == []

    def test_excludes_servers_without_idle_timeout(self, mocker):
        servers = {"3000": "http://localhost:3000/matlab"}
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value=servers,
        )
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"someOtherConfig": "value"}
        mocker.patch(
            "resources.notebooks.mwhelpers.web.send_http_request",
            return_value=mock_response,
        )
        assert matlab_proxy.list_servers_with_idle_timeout(username="testuser") == []

    def test_excludes_servers_with_failed_request(self, mocker):
        servers = {"3000": "http://localhost:3000/matlab"}
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value=servers,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.web.send_http_request",
            return_value=None,
        )
        assert matlab_proxy.list_servers_with_idle_timeout(username="testuser") == []


class TestPrepareStartupScript:
    def test_returns_cd_userpath_when_no_dsp_and_no_user_script(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=False
        )
        result = matlab_proxy._prepare_mwi_matlab_startup_script(
            username="testuser", mwi_matlab_startup_script=""
        )
        assert result == "cd(userpath); "

    def test_appends_user_script_when_no_dsp(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=False
        )
        result = matlab_proxy._prepare_mwi_matlab_startup_script(
            username="testuser", mwi_matlab_startup_script="disp('hello')"
        )
        assert result == "cd(userpath); disp('hello')"

    def test_includes_dsp_script_when_available(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=True
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_startup_script",
            return_value="cd /opt/dsp; onDatabricksSetup()",
        )
        result = matlab_proxy._prepare_mwi_matlab_startup_script(
            username="testuser", mwi_matlab_startup_script=""
        )
        assert result == "cd(userpath); cd /opt/dsp; onDatabricksSetup(); "

    def test_includes_dsp_and_user_script(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=True
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_startup_script",
            return_value="cd /opt/dsp; onDatabricksSetup()",
        )
        result = matlab_proxy._prepare_mwi_matlab_startup_script(
            username="testuser", mwi_matlab_startup_script="disp('hello')"
        )
        assert result == "cd(userpath); cd /opt/dsp; onDatabricksSetup(); disp('hello')"


class TestStartSession:
    def test_returns_empty_string_when_username_is_none(self):
        assert matlab_proxy.start(username=None) == ""  # type: ignore
        assert matlab_proxy.start(username="") == ""

    def test_returns_port_and_starts_process_when_setup_succeeds(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={},
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")

        assert matlab_proxy.start(username="testuser") == "3000"

        _, kwargs = mock_spawn.call_args
        assert kwargs["uid"] == 1001
        assert kwargs["command"] == ["matlab-proxy-app"]
        env_vars = kwargs["env"]
        assert env_vars["HOME"] == "/home/testuser"
        assert env_vars["USER"] == "testuser"
        assert env_vars["MWI_APP_PORT"] == "3000"
        assert env_vars["MWI_BASE_URL"] == "/matlab"
        assert env_vars["MWI_ENABLE_TOKEN_AUTH"] == "False"

    def test_creates_user_when_home_folder_does_not_exist(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user._get_passwd_entry_for_user",
            side_effect=["", "/home/testuser"],
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={},
        )
        mock_create_user = mocker.patch(
            "resources.notebooks.mwhelpers.user.create", return_value=1001
        )

        assert matlab_proxy.start(username="testuser") == "3000"
        mock_create_user.assert_called_once_with("testuser")

    def test_raises_when_home_folder_creation_fails(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            side_effect=RuntimeError("Unable to find home folder for user testuser"),
        )
        with pytest.raises(RuntimeError, match="Unable to find home folder"):
            matlab_proxy.start(username="testuser")

    def test_raises_when_uid_lookup_fails(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.user.uid",
            side_effect=RuntimeError("Unable to find UID for user testuser"),
        )
        with pytest.raises(RuntimeError, match="Unable to find UID"):
            matlab_proxy.start(username="testuser")

    def test_returns_empty_string_when_no_ports_available(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=None
        )
        assert matlab_proxy.start(username="testuser") == ""

    def test_sets_dsp_startup_script_when_dsp_available(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=True
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_startup_script",
            return_value="cd /opt/dsp; onDatabricksSetup()",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={},
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")
        mock_context = mocker.Mock()

        assert (
            matlab_proxy.start(username="testuser", dbx_context=mock_context) == "3000"
        )

        _, kwargs = mock_spawn.call_args
        env_vars = kwargs["env"]
        assert (
            env_vars["MWI_MATLAB_STARTUP_SCRIPT"]
            == "cd(userpath); cd /opt/dsp; onDatabricksSetup(); "
        )

    def test_includes_dsp_env_vars_when_dsp_available(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=True
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_startup_script",
            return_value="cd /opt/dsp; onDatabricksSetup()",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={
                "MW_ORG_ID": "12345",
                "MW_HOST": "https://my-workspace.cloud.databricks.com",
                "MW_API_URL": "https://my-workspace.cloud.databricks.com/api",
                "MW_API_TOKEN_B64": "c2VjcmV0",
            },
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")
        mock_context = mocker.Mock()

        matlab_proxy.start(username="testuser", dbx_context=mock_context)

        _, kwargs = mock_spawn.call_args
        env_vars = kwargs["env"]
        assert env_vars["MW_ORG_ID"] == "12345"
        assert env_vars["MW_HOST"] == "https://my-workspace.cloud.databricks.com"
        assert env_vars["MW_API_URL"] == "https://my-workspace.cloud.databricks.com/api"
        assert env_vars["MW_API_TOKEN_B64"] == "c2VjcmV0"

    def test_dsp_env_vars_set_when_dsp_unavailable(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=False
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={
                "MW_ORG_ID": "12345",
                "MW_HOST": "https://my-workspace.cloud.databricks.com",
                "MW_API_URL": "https://my-workspace.cloud.databricks.com/api",
                "MW_API_TOKEN_B64": "c2VjcmV0",
            },
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")
        mock_context = mocker.Mock()

        matlab_proxy.start(username="testuser", dbx_context=mock_context)

        _, kwargs = mock_spawn.call_args
        env_vars = kwargs["env"]
        assert env_vars["MW_ORG_ID"] == "12345"
        assert env_vars["MW_HOST"] == "https://my-workspace.cloud.databricks.com"
        assert env_vars["MW_API_URL"] == "https://my-workspace.cloud.databricks.com/api"
        assert env_vars["MW_API_TOKEN_B64"] == "c2VjcmV0"

    def test_custom_env_overrides_dsp_env_vars(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=True
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_startup_script",
            return_value="cd /opt/dsp; onDatabricksSetup()",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={"MW_HOST": "https://default-host"},
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")
        mock_context = mocker.Mock()

        matlab_proxy.start(
            username="testuser",
            env={"MW_HOST": "https://override-host"},
            dbx_context=mock_context,
        )

        _, kwargs = mock_spawn.call_args
        env_vars = kwargs["env"]
        assert env_vars["MW_HOST"] == "https://override-host"

    def test_passes_custom_env_to_session(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={},
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")

        assert (
            matlab_proxy.start(username="testuser", env={"MY_VAR": "value"}) == "3000"
        )

        _, kwargs = mock_spawn.call_args
        env_vars = kwargs["env"]
        assert env_vars["MY_VAR"] == "value"

    def test_preserves_preexisting_mwi_startup_script(self, mocker, monkeypatch):
        monkeypatch.setenv("MWI_MATLAB_STARTUP_SCRIPT", "disp('preexisting')")
        mocker.patch(
            "resources.notebooks.mwhelpers.user.home_folder",
            return_value="/home/testuser",
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch(
            "resources.notebooks.mwhelpers.dbx.find_next_open_port", return_value=3000
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available", return_value=False
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={},
        )
        mock_spawn = mocker.patch("resources.notebooks.mwhelpers.subprocess_shim.spawn")

        assert matlab_proxy.start(username="testuser") == "3000"

        _, kwargs = mock_spawn.call_args
        env_vars = kwargs["env"]
        assert (
            env_vars["MWI_MATLAB_STARTUP_SCRIPT"] == "cd(userpath); disp('preexisting')"
        )


class TestStopSession:
    def test_returns_false_when_context_in_job_mode(self, mock_databricks_context):
        mock_databricks_context.isInJob = "True"
        assert (
            matlab_proxy.stop(
                username="testuser", port=3000, context=mock_databricks_context
            )
            is False
        )

    def test_returns_false_when_port_is_none(self):
        assert matlab_proxy.stop(username="testuser", port=None) is False  # type:ignore

    def test_returns_false_when_username_is_none(self):
        assert matlab_proxy.stop(username=None, port=3000) is False  # type:ignore

    def test_returns_false_when_no_servers_found(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value=[],
        )
        assert matlab_proxy.stop(username="testuser", port=3000) is False

    def test_returns_false_when_port_not_in_running_servers(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value={"3001": "http://localhost:3001/matlab"},
        )
        assert matlab_proxy.stop(username="testuser", port=3000) is False

    def test_sends_delete_request_when_session_found(self, mocker):
        port = 3000
        base_url = f"http://localhost:{port}/matlab"
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy._list_servers",
            return_value={str(port): base_url},
        )
        mock_send = mocker.patch("resources.notebooks.mwhelpers.web.send_http_request")

        matlab_proxy.stop(username="testuser", port=port)

        mock_send.assert_called_once_with(
            f"{base_url}/shutdown_integration", method="DELETE"
        )
