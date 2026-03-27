# Copyright 2026 The MathWorks, Inc.


from resources.notebooks.mwhelpers import diagnostics, version


class TestGetMatlabInfo:
    def test_returns_info_when_matlab_installed(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="/opt/matlab/R2025b",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.version",
            return_value="R2025b Update 2",
        )
        result = diagnostics._get_matlab_info()
        assert "MATLAB Installed: /opt/matlab/R2025b" in result
        assert "MATLAB Version: R2025b Update 2" in result

    def test_returns_not_installed_when_root_empty(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.matlab.root", return_value="")
        mocker.patch("resources.notebooks.mwhelpers.matlab.version", return_value="")
        assert diagnostics._get_matlab_info() == "MATLAB is not installed"

    def test_returns_not_installed_on_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            side_effect=Exception("fail"),
        )
        assert diagnostics._get_matlab_info() == "MATLAB is not installed"


class TestGetDatabricksInfo:
    def test_returns_info_for_supported_runtime(self, mock_databricks_context):
        mock_databricks_context.runtimeVersion = "16.4.x-scala2.13"
        result = diagnostics._get_databricks_info(dbx_context=mock_databricks_context)
        assert "Databricks Runtime Version: 16.4.x-scala2.13" in result

    def test_returns_unsupported_for_old_runtime(self, mock_databricks_context):
        mock_databricks_context.runtimeVersion = "client.1.3-scala2.13"
        result = diagnostics._get_databricks_info(dbx_context=mock_databricks_context)
        assert "Unsupported Databricks Runtime Version" in result


class TestGetMatlabProxyInfo:
    def test_returns_version_when_installed(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy.version",
            return_value="0.26.4",
        )
        assert (
            diagnostics._get_matlab_proxy_info(username="testuser")
            == "MATLAB Proxy Version: 0.26.4"
        )

    def test_returns_not_found_when_version_is_none(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy.version",
            return_value=None,
        )
        assert (
            diagnostics._get_matlab_proxy_info(username="testuser")
            == "MATLAB Proxy not found"
        )

    def test_returns_not_found_on_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab_proxy.version",
            side_effect=Exception("fail"),
        )
        assert (
            diagnostics._get_matlab_proxy_info(username="testuser")
            == "MATLAB Proxy not found"
        )


class TestCheckInternetConnection:
    def test_returns_true_on_success(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics.requests.head",
            return_value=mock_response,
        )
        assert diagnostics.check_internet_connection("https://mathworks.com") is True

    def test_returns_false_on_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics.requests.head",
            side_effect=Exception("timeout"),
        )
        assert diagnostics.check_internet_connection("https://mathworks.com") is False

    def test_returns_false_on_bad_status_code(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 500
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics.requests.head",
            return_value=mock_response,
        )
        assert diagnostics.check_internet_connection("https://mathworks.com") is False


class TestGetDspEnvironmentVariables:
    def test_returns_dsp_env_vars(self, mocker, mock_databricks_context):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={
                "MW_ORG_ID": "12345",
                "MW_HOST": "https://my-workspace",
                "MW_API_TOKEN_B64": "c2VjcmV0",
            },
        )
        result = diagnostics._get_dsp_environment_variables(
            dbx_context=mock_databricks_context
        )
        values = {
            line.split("=")[0].strip(): line.split("=")[1].strip() for line in result
        }
        assert values["MW_ORG_ID"] == "12345"
        assert values["MW_HOST"] == "https://my-workspace"

    def test_redacts_api_token(self, mocker, mock_databricks_context):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            return_value={"MW_API_TOKEN_B64": "c2VjcmV0"},
        )
        result = diagnostics._get_dsp_environment_variables(
            dbx_context=mock_databricks_context
        )
        values = {
            line.split("=")[0].strip(): line.split("=")[1].strip() for line in result
        }
        assert values["MW_API_TOKEN_B64"] == "REDACTED"

    def test_returns_error_message_on_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.required_env_vars",
            side_effect=Exception("failed"),
        )
        result = diagnostics._get_dsp_environment_variables(dbx_context=mocker.Mock())
        assert result == ["DSP environment variables could not be resolved"]


class TestGetEnvironmentVariables:
    def test_returns_formatted_env_vars(self, mocker):
        mocker.patch.dict("os.environ", {"VAR1": "value1", "VAR2": "value2"})
        result = diagnostics._get_environment_variables(["VAR1", "VAR2"])
        assert len(result) == 2
        assert "VAR1" in result[0]
        assert "value1" in result[0]

    def test_returns_empty_value_for_missing_env_var(self, mocker):
        mocker.patch.dict("os.environ", {}, clear=True)
        result = diagnostics._get_environment_variables(["NONEXISTENT"])
        assert "NONEXISTENT" in result[0]


class TestGetMwiEnvironmentVariableKeys:
    def test_returns_only_mwi_keys(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {"MWI_APP_PORT": "8080", "MWI_BASE_URL": "/matlab", "OTHER_VAR": "x"},
            clear=True,
        )
        result = diagnostics._get_mwi_environment_variable_keys()
        assert "MWI_APP_PORT" in result
        assert "MWI_BASE_URL" in result
        assert "OTHER_VAR" not in result

    def test_excludes_non_mwi_keys(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {"JAVA_HOME": "/usr/lib/jvm", "MW_CONTEXT_TAGS": "tag"},
            clear=True,
        )
        result = diagnostics._get_mwi_environment_variable_keys()
        assert result == []

    def test_returns_sorted_keys(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {
                "MWI_USE_EXISTING_LICENSE": "1",
                "MWI_APP_HOST": "0.0.0.0",
                "MWI_BASE_URL": "/m",
            },
            clear=True,
        )
        result = diagnostics._get_mwi_environment_variable_keys()
        assert result == sorted(result)

    def test_returns_empty_list_when_no_mwi_keys(self, mocker):
        mocker.patch.dict("os.environ", {}, clear=True)
        result = diagnostics._get_mwi_environment_variable_keys()
        assert result == []

    def test_dynamic_keys_included_in_stream_env_keys(
        self, mocker, mock_databricks_context
    ):
        """Verify stream() passes dynamically discovered MWI* keys to _get_environment_variables."""
        mocker.patch.dict(
            "os.environ",
            {"MWI_CUSTOM_NEW_VAR": "custom_value"},
            clear=False,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_matlab_info",
            return_value="",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_mpm_info", return_value=""
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_databricks_info",
            return_value="",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_matlab_proxy_info",
            return_value="",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics.check_internet_connection",
            return_value=True,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_dsp_environment_variables",
            return_value=[],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_installed_python_packages",
            return_value=[],
        )
        spy = mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_environment_variables",
            return_value=[],
        )
        mocker.patch("resources.notebooks.mwhelpers.user.exists", return_value=True)

        list(
            diagnostics.stream(username="testuser", dbx_context=mock_databricks_context)
        )

        called_keys = spy.call_args[0][0]
        assert "MWI_CUSTOM_NEW_VAR" in called_keys


class TestGetDiagnostics:
    def test_assembles_all_sections(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_matlab_info",
            return_value="MATLAB Installed: /opt/matlab/R2025b",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_mpm_info",
            return_value="mpm 1.0",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_databricks_info",
            return_value="Databricks Runtime Version: 16.4",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_matlab_proxy_info",
            return_value="MATLAB Proxy Version: 0.26.4",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics.check_internet_connection",
            return_value=True,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_dsp_environment_variables",
            return_value=["MW_ORG_ID = 12345"],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_environment_variables",
            return_value=["VAR1 = val1"],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_installed_python_packages",
            return_value=["numpy == 1.24.0"],
        )

        result = diagnostics.get(username="testuser")

        assert f"Notebook version: {version()}" in result
        assert "MATLAB Installed" in result
        assert "mpm 1.0" in result
        assert "Databricks Runtime Version" in result
        assert "MATLAB Proxy Version" in result
        assert "Internet Connection OK" in result
        assert "MATLAB Interface for Databricks Environment Variables:" in result
        assert "Cluster Environment Variables:" in result
        assert "Python Packages Installed:" in result
        assert "************************" in result

    def test_shows_internet_connection_failed(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_matlab_info",
            return_value="MATLAB Installed",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_mpm_info",
            return_value="mpm info",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_databricks_info",
            return_value="DBR info",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_matlab_proxy_info",
            return_value="Proxy info",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics.check_internet_connection",
            return_value=False,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_dsp_environment_variables",
            return_value=[],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_environment_variables",
            return_value=[],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.diagnostics._get_installed_python_packages",
            return_value=[],
        )

        result = diagnostics.get(username="testuser")

        assert f"Notebook version: {version()}" in result
        assert "Internet Connection Failed" in result
