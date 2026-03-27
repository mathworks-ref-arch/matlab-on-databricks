# Copyright 2026 The MathWorks, Inc.


import subprocess

from resources.notebooks.mwhelpers import subprocess_shim


class TestRun:
    def test_runs_command_with_user_parameter(self, mocker):
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.subprocess.run",
            return_value=mocker.Mock(returncode=0, stdout="output"),
        )

        result = subprocess_shim.run(uid=1001, command=["echo", "hello"], env={})

        assert result.returncode == 0
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["capture_output"] is True
        assert call_kwargs["text"] is True
        # Verify the 'user' parameter is used (not deprecated preexec_fn)
        assert call_kwargs["user"] == 1001
        assert "preexec_fn" not in call_kwargs


class TestSpawn:
    def test_spawns_process_with_user_parameter(self, mocker):
        mock_popen = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.subprocess.Popen",
            return_value=mocker.MagicMock(),
        )

        subprocess_shim.spawn(uid=1001, command=["matlab-proxy-app"], env={})

        mock_popen.assert_called_once()
        call_kwargs = mock_popen.call_args[1]
        # Verify the 'user' parameter is used (not deprecated preexec_fn)
        assert call_kwargs["user"] == 1001
        assert "preexec_fn" not in call_kwargs
        assert call_kwargs["stdout"] == subprocess.DEVNULL
        assert call_kwargs["stderr"] == subprocess.DEVNULL


class TestRunRunuser:
    def test_runs_command_as_specified_user(self, mocker):
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.subprocess.run",
            return_value=mocker.Mock(returncode=0, stdout="output"),
        )

        result = subprocess_shim.run_runuser(
            username="testuser",
            command="echo hello",
            env={"PATH": "/usr/bin"},
        )

        assert result.returncode == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "runuser" in call_args
        assert "testuser" in call_args

    def test_includes_whitelist_env_vars_when_provided(self, mocker):
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.subprocess.run",
            return_value=mocker.Mock(returncode=0, stdout=""),
        )

        subprocess_shim.run_runuser(
            username="testuser",
            command="matlab -batch 'disp(1)'",
            env={},
            whitelist_env_vars="MLM_LICENSE_FILE,PYSPARK_PYTHON",
        )

        call_args = mock_run.call_args[0][0]
        whitelist_found = any("whitelist-environment" in str(arg) for arg in call_args)
        assert whitelist_found

    def test_omits_whitelist_when_empty(self, mocker):
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.subprocess.run",
            return_value=mocker.Mock(returncode=0, stdout=""),
        )

        subprocess_shim.run_runuser(
            username="testuser",
            command="echo hello",
            env={},
            whitelist_env_vars="",
        )

        call_args = mock_run.call_args[0][0]
        whitelist_found = any("whitelist-environment" in str(arg) for arg in call_args)
        assert not whitelist_found
