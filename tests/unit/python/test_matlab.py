# Copyright 2026 The MathWorks, Inc.

import pytest

from resources.notebooks.mwhelpers import matlab


class TestMatlabRoot:
    @pytest.mark.parametrize(
        "which_output, readlink_output, expected_root",
        [
            (
                "/usr/local/bin/matlab",
                "/opt/matlab/R2025b/bin/matlab",
                "/opt/matlab/R2025b",
            ),
            (
                "/custom/matlab/executable/path",
                "/custom/matlab/path",
                "/custom/matlab/path",
            ),
            (
                "/custom/matlab/executable/path",
                "/custom/matlab/executable/path",
                "/custom/matlab/executable/path",
            ),
            ("", "", ""),
        ],
        ids=["standard_path", "custom_path", "same_path", "no_path"],
    )
    def test_resolves_matlab_root_path(
        self, mocker, which_output, readlink_output, expected_root
    ):
        mocker.patch(
            "shutil.which", return_value=which_output if which_output else None
        )
        mocker.patch(
            "pathlib.Path.resolve",
            return_value=readlink_output if readlink_output else None,
        )
        assert matlab.root() == expected_root


class TestMatlabVersion:
    def test_returns_version_string_from_version_info_xml(self, mocker, tmp_path):
        version_xml = tmp_path / "VersionInfo.xml"
        version_xml.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<MathWorks_version_info>\n"
            "  <version>25.2.0.2986527</version>\n"
            "  <release>R2025b</release>\n"
            "  <description>Update 2</description>\n"
            "</MathWorks_version_info>\n"
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value=str(tmp_path),
        )
        assert matlab.version() == "R2025b Update 2 (25.2.0.2986527)"

    def test_returns_version_without_description_when_absent(self, mocker, tmp_path):
        version_xml = tmp_path / "VersionInfo.xml"
        version_xml.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<MathWorks_version_info>\n"
            "  <version>25.2.0.2986527</version>\n"
            "  <release>R2025b</release>\n"
            "</MathWorks_version_info>\n"
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value=str(tmp_path),
        )
        assert matlab.version() == "R2025b (25.2.0.2986527)"

    def test_returns_unknown_when_root_is_empty(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="",
        )
        assert matlab.version() == "Unknown"

    def test_returns_unknown_on_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="/nonexistent/path",
        )
        assert matlab.version() == "Unknown"


class TestInstalledToolboxes:
    def test_returns_list_from_products(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="/opt/matlab/R2025b",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab._list_installed_products",
            return_value=["MATLAB", "Simulink"],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available",
            return_value=False,
        )
        assert matlab.installed_toolboxes(username="testuser") == [
            "MATLAB",
            "Simulink",
        ]

    def test_returns_empty_list_when_root_is_empty(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="",
        )
        assert matlab.installed_toolboxes(username="testuser") == []

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="Username is required"):
            matlab.installed_toolboxes(username="")

    def test_appends_dsp_when_available(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="/opt/matlab/R2025b",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab._list_installed_products",
            return_value=["MATLAB", "Simulink"],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.is_dsp_available",
            return_value=True,
        )
        toolboxes = matlab.installed_toolboxes(username="testuser")
        assert "Databricks Support Package" in toolboxes


class TestListInstalledProducts:
    def test_returns_products_from_contents_files(self, tmp_path):
        # Create toolbox structure with valid Contents.m
        toolbox_dir = tmp_path / "toolbox" / "signal" / "signal"
        toolbox_dir.mkdir(parents=True)
        (toolbox_dir / "Contents.m").write_text(
            "% Signal Processing Toolbox\n% Version 24.2 (R2024b)\n"
        )
        # Create MATLAB general Contents.m (should be excluded from scan but trigger has_matlab)
        matlab_general = tmp_path / "toolbox" / "matlab" / "general"
        matlab_general.mkdir(parents=True)
        (matlab_general / "Contents.m").write_text(
            "% General purpose commands.\n% Version 24.2 (R2024b)\n"
        )
        result = matlab._list_installed_products(str(tmp_path))
        assert result == ["MATLAB", "Signal Processing Toolbox"]

    def test_excludes_paths_with_plus_or_at(self, tmp_path):
        toolbox_dir = tmp_path / "toolbox" / "pkg" / "+internal"
        toolbox_dir.mkdir(parents=True)
        (toolbox_dir / "Contents.m").write_text("% Internal Package\n% Version 1.0\n")
        result = matlab._list_installed_products(str(tmp_path))
        assert result == []

    def test_skips_files_without_version_line(self, tmp_path):
        toolbox_dir = tmp_path / "toolbox" / "custom" / "custom"
        toolbox_dir.mkdir(parents=True)
        (toolbox_dir / "Contents.m").write_text("% Custom Toolbox\n% No version here\n")
        result = matlab._list_installed_products(str(tmp_path))
        assert result == []

    def test_returns_empty_when_no_toolbox_dir(self, tmp_path):
        result = matlab._list_installed_products(str(tmp_path))
        assert result == []

    def test_excludes_toolbox_local(self, tmp_path):
        local_dir = tmp_path / "toolbox" / "local"
        local_dir.mkdir(parents=True)
        (local_dir / "Contents.m").write_text("% Local Settings\n% Version 1.0\n")
        result = matlab._list_installed_products(str(tmp_path))
        assert result == []


class TestMatlabRootException:
    def test_returns_empty_string_on_exception(self, mocker):
        mocker.patch(
            "shutil.which",
            side_effect=Exception("unexpected error"),
        )
        assert matlab.root() == ""


class TestCodeExecutionWithMatlabBatch:
    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="Username cannot be empty"):
            matlab.run_code_with_matlab_batch(username="", code="")

    def test_raises_when_license_not_set(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch.dict("os.environ", {"MLM_LICENSE_FILE": ""})
        with pytest.raises(ValueError, match="MLM_LICENSE_FILE"):
            matlab.run_code_with_matlab_batch(username="testuser", code="ver")

    def test_returns_true_on_success(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch.dict("os.environ", {"MLM_LICENSE_FILE": "port@server"})
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run_runuser",
            return_value=mocker.Mock(returncode=0, stdout="ok"),
        )
        assert matlab.run_code_with_matlab_batch(username="testuser", code="ver") == (
            True,
            "ok",
        )

    def test_returns_false_on_failure(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch.dict("os.environ", {"MLM_LICENSE_FILE": "port@server"})
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run_runuser",
            return_value=mocker.Mock(returncode=1, stdout="", stderr="error"),
        )
        assert matlab.run_code_with_matlab_batch(username="testuser", code="ver") == (
            False,
            "error",
        )

    def test_raises_value_error_when_code_empty(self):
        with pytest.raises(ValueError, match="No code to run provided"):
            matlab.run_code_with_matlab_batch(username="testuser", code="")

    def test_license_server_address_takes_precedence_over_env(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch.dict("os.environ", {"MLM_LICENSE_FILE": "env@server"})
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run_runuser",
            return_value=mocker.Mock(returncode=0, stdout="ok"),
        )
        matlab.run_code_with_matlab_batch(
            username="testuser", code="ver", license_server_address="arg@server"
        )
        call_env = mock_run.call_args[1]["env"]
        assert call_env["MLM_LICENSE_FILE"] == "arg@server"

    def test_uses_custom_env_dict(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        custom_env = {"MLM_LICENSE_FILE": "custom@server", "MY_VAR": "value"}
        mock_run = mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run_runuser",
            return_value=mocker.Mock(returncode=0, stdout="ok"),
        )
        matlab.run_code_with_matlab_batch(
            username="testuser", code="ver", env=custom_env
        )
        call_env = mock_run.call_args[1]["env"]
        assert call_env["MY_VAR"] == "value"

    def test_raises_when_license_not_in_env_or_arg(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1001)
        mocker.patch.dict("os.environ", {}, clear=True)
        with pytest.raises(ValueError, match="MLM_LICENSE_FILE"):
            matlab.run_code_with_matlab_batch(username="testuser", code="ver")
