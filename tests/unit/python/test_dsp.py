# Copyright 2026 The MathWorks, Inc.

import base64
import sys
import types
from pathlib import Path

import pytest

from resources.notebooks.mwhelpers import dsp


class TestGetMwiUnzipLocation:
    def test_returns_expected_path(self):
        result = dsp.get_mwi_unzip_location("testuser")
        assert result == Path("/local_disk0/testuser/matlab-interface-for-databricks")

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.get_mwi_unzip_location("")

    def test_raises_value_error_when_username_none(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.get_mwi_unzip_location(None)


class TestIsDspAvailable:
    def test_returns_true_when_dsp_exists(self, mocker):
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.is_file", return_value=True)
        assert dsp.is_dsp_available("testuser") is True

    def test_returns_false_when_path_does_not_exist(self, mocker):
        mocker.patch("pathlib.Path.exists", return_value=False)
        assert dsp.is_dsp_available("testuser") is False

    def test_returns_false_when_version_file_missing(self, mocker):
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.is_file", return_value=False)
        assert dsp.is_dsp_available("testuser") is False

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.is_dsp_available("")


class TestReadInstalledVersion:
    def test_returns_version_when_installed(self, tmp_path, mocker):
        version_file = tmp_path / "matlab-databricks" / "VERSION"
        version_file.parent.mkdir(parents=True)
        version_file.write_text("2.1.0")
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_mwi_unzip_location",
            return_value=tmp_path,
        )
        assert dsp.read_installed_version("testuser") == "2.1.0"

    def test_strips_whitespace(self, tmp_path, mocker):
        version_file = tmp_path / "matlab-databricks" / "VERSION"
        version_file.parent.mkdir(parents=True)
        version_file.write_text("  3.0.0\n")
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_mwi_unzip_location",
            return_value=tmp_path,
        )
        assert dsp.read_installed_version("testuser") == "3.0.0"

    def test_returns_empty_when_not_installed(self, tmp_path, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_mwi_unzip_location",
            return_value=tmp_path,
        )
        assert dsp.read_installed_version("testuser") == ""

    def test_returns_empty_for_empty_username(self):
        assert dsp.read_installed_version("") == ""

    def test_returns_empty_for_none_username(self):
        assert dsp.read_installed_version(None) == ""


class TestGetDspStartupScript:
    def test_returns_matlab_startup_script(self):
        result = dsp.get_dsp_startup_script("testuser")
        assert "onDatabricksSetup" in result
        assert "testuser" in result
        assert "startupFolder" in result

    def test_includes_options_from_env_var(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {dsp.get_dsp_startup_options_env_var(): "'Option1', 'Option2'"},
        )
        result = dsp.get_dsp_startup_script("testuser")
        assert "'Option1', 'Option2'" in result

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.get_dsp_startup_script("")


class TestGetDspStartupOptionsEnvVar:
    def test_returns_expected_env_var_name(self):
        assert dsp.get_dsp_startup_options_env_var() == "DSP_STARTUP_OPTIONS"


class TestUnzip:
    def test_returns_true_on_success(self, mocker):
        mock_zipfile = mocker.patch("resources.notebooks.mwhelpers.dsp.zipfile.ZipFile")
        mock_zipfile.return_value.__enter__ = mocker.Mock(
            return_value=mocker.MagicMock()
        )
        mock_zipfile.return_value.__exit__ = mocker.Mock(return_value=False)
        mock_uid = mocker.patch(
            "resources.notebooks.mwhelpers.user.uid", return_value=1001
        )
        mock_run = mocker.patch("resources.notebooks.mwhelpers.dsp.subprocess.run")
        assert dsp.unzip("testuser", "/tmp/package.zip") is True
        mock_uid.assert_called_once_with("testuser", create_if_not_exists=True)
        mock_run.assert_called_once_with(
            ["chown", "-R", "testuser", str(dsp.get_mwi_unzip_location("testuser"))],
            check=True,
        )

    def test_returns_false_on_error(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.zipfile.ZipFile",
            side_effect=Exception("bad zip"),
        )
        assert dsp.unzip("testuser", "/tmp/bad.zip") is False


class TestParseSemver:
    def test_parses_three_part_version(self):
        assert dsp._parse_semver("1.2.3") == (1, 2, 3)

    def test_parses_two_part_version(self):
        assert dsp._parse_semver("1.2") == (1, 2)

    def test_parses_single_number(self):
        assert dsp._parse_semver("5") == (5,)

    def test_returns_none_for_non_numeric(self):
        assert dsp._parse_semver("abc") is None

    def test_returns_none_for_mixed(self):
        assert dsp._parse_semver("1.2.beta") is None

    def test_returns_none_for_empty_string(self):
        assert dsp._parse_semver("") is None

    def test_returns_none_for_none(self):
        assert dsp._parse_semver(None) is None


class TestResolveLatestDspFromInterfaceDirectory:
    def test_returns_empty_when_env_var_not_set(self, mocker):
        mocker.patch.dict("os.environ", {}, clear=True)
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert path == ""
        assert error == ""

    def test_returns_error_when_versions_dir_missing(self, mocker, tmp_path):
        interface_dir = tmp_path / "MathWorks"
        interface_dir.mkdir()
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(interface_dir)},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert path == ""
        assert "does not exist" in error

    def test_returns_error_when_no_version_dirs(self, mocker, tmp_path):
        versions_dir = tmp_path / "MathWorks" / "Versions"
        versions_dir.mkdir(parents=True)
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(tmp_path / "MathWorks")},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert path == ""
        assert "No valid version directories" in error

    def test_returns_latest_version_zip(self, mocker, tmp_path):
        interface_dir = tmp_path / "MathWorks"
        for ver in ["1.0.0", "2.1.0", "2.0.5"]:
            ver_dir = interface_dir / "Versions" / ver
            ver_dir.mkdir(parents=True)
            (ver_dir / f"matlab-databricks-v{ver}.zip").touch()
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(interface_dir)},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert error == ""
        assert "2.1.0" in path
        assert path.endswith(".zip")

    def test_returns_error_when_multiple_zips_in_latest(self, mocker, tmp_path):
        interface_dir = tmp_path / "MathWorks"
        ver_dir = interface_dir / "Versions" / "1.0.0"
        ver_dir.mkdir(parents=True)
        (ver_dir / "package-a.zip").touch()
        (ver_dir / "package-b.zip").touch()
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(interface_dir)},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert path == ""
        assert "Multiple zip files" in error

    def test_skips_non_semver_directories(self, mocker, tmp_path):
        interface_dir = tmp_path / "MathWorks"
        # Non-semver directory should be ignored
        (interface_dir / "Versions" / "readme").mkdir(parents=True)
        ver_dir = interface_dir / "Versions" / "3.0.0"
        ver_dir.mkdir(parents=True)
        (ver_dir / "matlab-databricks-v3.0.0.zip").touch()
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(interface_dir)},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert error == ""
        assert "3.0.0" in path

    def test_returns_error_when_no_zips_in_any_version(self, mocker, tmp_path):
        interface_dir = tmp_path / "MathWorks"
        (interface_dir / "Versions" / "1.0.0").mkdir(parents=True)
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(interface_dir)},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert path == ""
        assert "No zip files found" in error

    def test_falls_back_to_older_version_when_latest_has_no_zip(self, mocker, tmp_path):
        interface_dir = tmp_path / "MathWorks"
        # Latest version has no zip
        (interface_dir / "Versions" / "2.0.0").mkdir(parents=True)
        # Older version has a valid zip
        older_dir = interface_dir / "Versions" / "1.0.0"
        older_dir.mkdir(parents=True)
        (older_dir / "matlab-databricks-v1.0.0.zip").touch()
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(interface_dir)},
        )
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert error == ""
        assert "1.0.0" in path

    def test_returns_error_on_unexpected_exception(self, mocker, tmp_path):
        mocker.patch.dict(
            "os.environ",
            {"MW_INTERFACE_DIRECTORY_DEFAULT": str(tmp_path)},
        )
        mocker.patch("pathlib.Path.is_dir", side_effect=OSError("permission denied"))
        path, error = dsp.resolve_latest_dsp_from_interface_directory()
        assert path == ""
        assert "Error while resolving latest DSP" in error


class TestShouldAutoInstall:
    @staticmethod
    def _make_zip(tmp_path, version: str) -> str:
        import zipfile

        zip_path = tmp_path / "matlab-databricks.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("matlab-databricks/VERSION", version)
        return str(zip_path)

    @pytest.mark.parametrize(
        "zip_version, installed, expected",
        [
            pytest.param("1.2.3", "1.2.3", False, id="version_matches_installed"),
            pytest.param("2.0.0", "1.2.3", True, id="version_differs"),
            pytest.param("1.0.0", "", True, id="nothing_installed"),
            pytest.param("1.2.3\n", "1.2.3", False, id="strips_whitespace"),
            pytest.param("1.0.0", "2.0.0", True, id="rollback_to_older_version"),
        ],
    )
    def test_uses_resolved_zip_version(
        self, tmp_path, zip_version, installed, expected
    ):
        zip_path = self._make_zip(tmp_path, zip_version)
        assert dsp._should_auto_install(zip_path, installed) is expected

    def test_returns_false_when_no_resolved_path(self):
        assert dsp._should_auto_install("", "1.0.0") is False

    def test_returns_false_when_zip_unreadable(self, tmp_path):
        bad_zip = tmp_path / "missing.zip"
        assert dsp._should_auto_install(str(bad_zip), "1.2.3") is False


class TestInstallIfNeeded:
    def test_installs_when_newer(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp._should_auto_install",
            return_value=True,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.read_installed_version",
            side_effect=["1.0.0", "2.0.0"],
        )
        mock_unzip = mocker.patch(
            "resources.notebooks.mwhelpers.dsp.unzip", return_value=True
        )
        assert dsp.install_if_needed("testuser", "/tmp/package.zip") == (True, "2.0.0")
        mock_unzip.assert_called_once_with(
            username="testuser", zip_file_path="/tmp/package.zip"
        )

    def test_skips_when_not_needed(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp._should_auto_install",
            return_value=False,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.read_installed_version",
            return_value="1.2.3",
        )
        mock_unzip = mocker.patch("resources.notebooks.mwhelpers.dsp.unzip")
        assert dsp.install_if_needed("testuser", "/tmp/package.zip") == (False, "1.2.3")
        mock_unzip.assert_not_called()

    def test_raises_when_unzip_fails(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp._should_auto_install",
            return_value=True,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.read_installed_version",
            return_value="1.0.0",
        )
        mocker.patch("resources.notebooks.mwhelpers.dsp.unzip", return_value=False)
        with pytest.raises(RuntimeError, match="Failed to extract"):
            dsp.install_if_needed("testuser", "/tmp/package.zip")

    def test_raises_when_no_version_after_extract(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp._should_auto_install",
            return_value=True,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.read_installed_version",
            side_effect=["1.0.0", ""],
        )
        mocker.patch("resources.notebooks.mwhelpers.dsp.unzip", return_value=True)
        with pytest.raises(RuntimeError, match="no version was found"):
            dsp.install_if_needed("testuser", "/tmp/package.zip")


class TestGetDspPythonPackageLocation:
    def test_returns_expected_path(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_mwi_unzip_location",
            return_value=Path("/local_disk0/testuser/matlab-interface-for-databricks"),
        )
        result = dsp.get_dsp_python_package_location("testuser")
        assert result == Path(
            "/local_disk0/testuser/matlab-interface-for-databricks"
            "/matlab-databricks/Software/Python"
        )

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.get_dsp_python_package_location("")

    def test_raises_value_error_when_username_none(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.get_dsp_python_package_location(None)


@pytest.fixture
def restore_sys_path():
    """Restore ``sys.path`` after tests that add the DSP python package location."""
    original = list(sys.path)
    yield
    sys.path[:] = original


class TestAddDspPythonPackageToSysPath:
    def test_inserts_package_location_at_front(self, mocker, restore_sys_path):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        dsp._add_dsp_python_package_to_sys_path("testuser")
        assert sys.path[0] == "/pkg/Python"

    def test_does_not_insert_duplicate_when_called_twice(
        self, mocker, restore_sys_path
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        dsp._add_dsp_python_package_to_sys_path("testuser")
        length_after_first_call = len(sys.path)
        dsp._add_dsp_python_package_to_sys_path("testuser")
        assert sys.path.count("/pkg/Python") == 1
        assert len(sys.path) == length_after_first_call

    def test_does_not_reinsert_existing_entry_at_front(self, mocker, restore_sys_path):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        sys.path.append("/pkg/Python")
        dsp._add_dsp_python_package_to_sys_path("testuser")
        assert sys.path.count("/pkg/Python") == 1
        assert sys.path[0] != "/pkg/Python"

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp._add_dsp_python_package_to_sys_path("")


@pytest.fixture
def fake_mw_prefs(mocker):
    """Install a fake ``mw_context.mw_prefs`` module so the dynamic imports in
    dsp resolve without the real support package being present."""
    mw_context = types.ModuleType("mw_context")
    mw_prefs = types.ModuleType("mw_context.mw_prefs")
    mw_prefs.default_config_filename = mocker.Mock(
        return_value="/some/path/mw_pref.json"
    )
    mw_prefs.startup = mocker.Mock()
    mw_context.mw_prefs = mw_prefs
    mocker.patch.dict(
        sys.modules,
        {"mw_context": mw_context, "mw_context.mw_prefs": mw_prefs},
    )
    return mw_prefs


class TestGetDefaultPrefFileLocation:
    def test_returns_default_config_filename(
        self, mocker, fake_mw_prefs, restore_sys_path
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        result = dsp.get_default_pref_file_location("testuser")
        assert result == "/some/path/mw_pref.json"
        fake_mw_prefs.default_config_filename.assert_called_once_with(verbose=True)

    def test_inserts_package_location_on_sys_path(
        self, mocker, fake_mw_prefs, restore_sys_path
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        dsp.get_default_pref_file_location("testuser")
        assert sys.path.count("/pkg/Python") == 1

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.get_default_pref_file_location("")


class TestStartSavingMatlabPreferences:
    def test_calls_startup_with_config_path(
        self, mocker, fake_mw_prefs, restore_sys_path
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        dsp.start_saving_matlab_preferences("testuser", "/cfg/mw_pref.json")
        fake_mw_prefs.startup.assert_called_once_with("/cfg/mw_pref.json", verbose=True)

    def test_does_not_duplicate_sys_path_entry_when_called_twice(
        self, mocker, fake_mw_prefs, restore_sys_path
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        dsp.start_saving_matlab_preferences("testuser", "/cfg/mw_pref.json")
        dsp.start_saving_matlab_preferences("testuser", "/cfg/mw_pref.json")
        assert sys.path.count("/pkg/Python") == 1

    def test_sets_startup_shutdown_config_env_var(
        self, mocker, fake_mw_prefs, restore_sys_path
    ):
        mocker.patch(
            "resources.notebooks.mwhelpers.dsp.get_dsp_python_package_location",
            return_value=Path("/pkg/Python"),
        )
        mocker.patch.dict("os.environ", {}, clear=False)
        dsp.start_saving_matlab_preferences("testuser", "/cfg/mw_pref.json")
        assert dsp.os.environ["MW_STARTUP_SHUTDOWN_CONFIG"] == "/cfg/mw_pref.json"

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            dsp.start_saving_matlab_preferences("", "/cfg/mw_pref.json")


class TestRequiredEnvVars:
    def test_returns_expected_env_vars(self, mocker):
        mock_context = mocker.Mock(
            workspaceId="12345",
            workspaceUrl="my-workspace.cloud.databricks.com",
            clusterId="0123-456789-abcdef",
            apiUrl="https://my-workspace.cloud.databricks.com/api",
            apiToken="secret-token",
            user="testuser@example.com",
        )
        result = dsp.required_env_vars(dbx_context=mock_context)
        assert result["MW_ORG_ID"] == "12345"
        assert result["MW_HOST"] == "https://my-workspace.cloud.databricks.com"
        assert result["MW_CLUSTER_ID"] == "0123-456789-abcdef"
        assert result["MW_API_URL"] == "https://my-workspace.cloud.databricks.com/api"
        expected_token = base64.b64encode(b"secret-token").decode("utf-8")
        assert result["MW_API_TOKEN_B64"] == expected_token
        assert result["MW_DBX_USERNAME"] == "testuser@example.com"
        assert result["SPARK_CONNECT_MODE_ENABLED"] == "1"

    def test_returns_exactly_seven_keys(self, mocker):
        mock_context = mocker.Mock(
            workspaceId="1",
            workspaceUrl="host",
            clusterId="cid",
            apiUrl="url",
            apiToken="tok",
            user="u",
        )
        result = dsp.required_env_vars(dbx_context=mock_context)
        assert set(result.keys()) == {
            "MW_ORG_ID",
            "MW_HOST",
            "MW_CLUSTER_ID",
            "MW_API_URL",
            "MW_API_TOKEN_B64",
            "MW_DBX_USERNAME",
            "SPARK_CONNECT_MODE_ENABLED",
        }

    def test_raises_when_no_context_passed(self):
        with pytest.raises(ValueError, match="Databricks Context must be passed in"):
            dsp.required_env_vars(dbx_context=None)
