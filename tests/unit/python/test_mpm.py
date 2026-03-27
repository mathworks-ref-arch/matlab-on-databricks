# Copyright 2026 The MathWorks, Inc.

from pathlib import Path

import pytest

from resources.notebooks.mwhelpers import mpm


class TestMpmInstall:
    def test_streams_output_on_success(self, mocker, tmp_path):
        mock_file_path = tmp_path / "mpm_input.txt"
        mock_process = mocker.MagicMock()
        expected_output = [
            "Reading input file...\n",
            "Resolving dependencies...\n",
        ]
        mock_process.stdout.readline.side_effect = expected_output + [""]
        mock_process.wait.return_value = 0
        mock_popen = mocker.patch(
            "resources.notebooks.mwhelpers.mpm.subprocess.Popen",
            return_value=mock_process,
        )
        expected_command = ["mpm", "install", f"--inputfile={mock_file_path}"]

        output_lines = list(mpm.install(mock_file_path))

        assert output_lines == [line.strip() for line in expected_output]
        mock_popen.assert_called_once()
        call_args, call_kwargs = mock_popen.call_args
        assert call_args[0] == expected_command
        assert call_kwargs["text"] is True
        mock_process.stdout.close.assert_called_once()
        mock_process.wait.assert_called_once()

    @pytest.mark.parametrize("invalid_input", [None, ""])
    def test_raises_value_error_for_invalid_input(self, mocker, invalid_input):
        mock_popen = mocker.patch("resources.notebooks.mwhelpers.mpm.subprocess.Popen")
        with pytest.raises(ValueError, match="Input file location is required"):
            list(mpm.install(invalid_input))
        mock_popen.assert_not_called()

    def test_raises_exception_on_failure(self, mocker):
        mock_process = mocker.MagicMock()
        mock_process.stdout.readline.side_effect = ["An error occurred.\n", ""]
        mock_process.wait.return_value = 127
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.subprocess.Popen",
            return_value=mock_process,
        )

        with pytest.raises(RuntimeError, match="Failed with exit code 127"):
            list(mpm.install("/tmp/products.txt"))
        mock_process.wait.assert_called_once()


class TestMpmSaveFile:
    def test_succeeds_with_valid_file(self, mocker):
        mock_uploaded_file = {
            "metadata": {"name": "products.txt"},
            "content": b"## PRODUCTS\n#product.MATLAB",
        }
        expected_path = "/tmp/mathworks_products.txt"
        mock_save = mocker.patch(
            "resources.notebooks.mwhelpers.mpm._save_mpm_input_file",
            return_value=expected_path,
        )

        result = mpm.save_file(mock_uploaded_file)

        assert result == expected_path
        mock_save.assert_called_once_with(
            "products.txt", "## PRODUCTS\n#product.MATLAB"
        )

    def test_fails_on_validation_error(self):
        mock_uploaded_file = {
            "metadata": {"name": "bad_file.zip"},
            "content": b"invalid content",
        }
        with pytest.raises(ValueError, match="Unsupported file extension: .zip"):
            mpm.save_file(mock_uploaded_file)

    def test_fails_on_save_error(self, mocker):
        mock_uploaded_file = {
            "metadata": {"name": "products.txt"},
            "content": b"## PRODUCTS\n#product.MATLAB",
        }
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm._save_mpm_input_file",
            side_effect=IOError("Permission denied"),
        )
        with pytest.raises(IOError, match="Permission denied"):
            mpm.save_file(mock_uploaded_file)


class TestParseMpmInputFile:
    def test_parses_all_sections(self):
        content = (
            "## PRODUCTS\n"
            "#product.Simulink\n"
            "#product.MATLAB\n"
            "## SUPPORT PACKAGES\n"
            "#product.Some_Support_Package\n"
            "## OPTIONAL FEATURES\n"
            "#product.Some_Add_On"
        )
        products, support_packages, optional_features = mpm._parse_mpm_input_file(
            content
        )
        assert products == ["Simulink", "MATLAB"]
        assert support_packages == ["Some Support Package"]
        assert optional_features == ["Some Add On"]

    def test_returns_empty_lists_for_empty_content(self):
        products, support_packages, optional_features = mpm._parse_mpm_input_file("")
        assert products == []
        assert support_packages == []
        assert optional_features == []


class TestIsValid:
    def test_returns_true_when_products_present(self):
        assert mpm._is_valid("## PRODUCTS\n#product.MATLAB") is True

    def test_returns_false_when_no_products(self):
        assert mpm._is_valid("## PRODUCTS\n# just a comment") is False

    def test_returns_false_for_empty_string(self):
        assert mpm._is_valid("") is False


class TestDecode:
    def test_accepts_valid_txt_file(self):
        result = mpm._decode("products.txt", b"## PRODUCTS\n#product.MATLAB")
        assert "## PRODUCTS" in result

    def test_rejects_non_txt_extension(self):
        with pytest.raises(ValueError, match="Unsupported file extension"):
            mpm._decode("products.zip", b"content")

    def test_rejects_invalid_utf8(self):
        with pytest.raises(ValueError, match="UTF-8 decoding failed"):
            mpm._decode("products.txt", b"\xff\xfe")

    def test_rejects_invalid_content(self):
        with pytest.raises(ValueError, match="File content validation failed"):
            mpm._decode("products.txt", b"no valid mpm content here")


class TestMpmExists:
    def test_returns_true_when_mpm_on_path(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.shutil.which",
            return_value="/usr/local/bin/mpm",
        )
        assert mpm.exists() is True

    def test_returns_false_when_mpm_not_on_path(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.shutil.which",
            return_value=None,
        )
        assert mpm.exists() is False


class TestMpmInfo:
    def test_returns_false_when_mpm_not_on_path(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.shutil.which", return_value=None
        )

        result = mpm.info("testuser")

        assert result == (False, "MATLAB Package Manager is not on PATH")

    def test_returns_true_with_version(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.shutil.which",
            return_value="/usr/local/bin/mpm",
        )
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.resolve.return_value = "/usr/local/bin/mpm"
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.Path",
            return_value=mock_path_instance,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.version",
            return_value="1.2.3",
        )

        result = mpm.info("testuser")

        assert result == (True, "1.2.3 installed at: /usr/local/bin/mpm")

    def test_returns_false_when_version_unknown(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.shutil.which",
            return_value="/usr/local/bin/mpm",
        )
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.resolve.return_value = "/usr/local/bin/mpm"
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.Path",
            return_value=mock_path_instance,
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.version",
            return_value=None,
        )

        result = mpm.info("testuser")

        assert result == (
            False,
            "MATLAB Package Manager version (unknown) installed at: /usr/local/bin/mpm",
        )

    def test_returns_false_on_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.mpm.shutil.which",
            side_effect=OSError("something went wrong"),
        )

        result = mpm.info("testuser")

        assert result[0] is False
        assert "MATLAB Package Manager is not installed, error:" in result[1]


class TestMpmVersion:
    def test_returns_version_string_on_success(self, mocker):
        mock_output = mocker.MagicMock()
        mock_output.returncode = 0
        mock_output.stdout = "mpm 1.2.3"
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_output,
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1000)

        result = mpm.version("testuser")

        assert result == "mpm 1.2.3"

    def test_returns_none_on_nonzero_exit_code(self, mocker):
        mock_output = mocker.MagicMock()
        mock_output.returncode = 1
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_output,
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1000)

        result = mpm.version("testuser")

        assert result is None

    def test_returns_none_on_empty_stdout(self, mocker):
        mock_output = mocker.MagicMock()
        mock_output.returncode = 0
        mock_output.stdout = "   "
        mocker.patch(
            "resources.notebooks.mwhelpers.subprocess_shim.run",
            return_value=mock_output,
        )
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1000)

        result = mpm.version("testuser")

        assert result is None


class TestSaveMpmInputFile:
    def test_saves_file_with_destination_folder(self, mocker, tmp_path):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="/opt/matlab/R2026a",
        )
        prefix = str(tmp_path / "mathworks")
        content = "## PRODUCTS\n#product.MATLAB"

        result = mpm._save_mpm_input_file("products.txt", content, path_prefix=prefix)

        assert result == f"{prefix}_products.txt"
        with open(result) as f:
            saved = f.read()
        assert saved.startswith(content)
        assert "destinationFolder=/opt/matlab/R2026a" in saved

    def test_uses_custom_path_prefix(self, mocker, tmp_path):
        mocker.patch(
            "resources.notebooks.mwhelpers.matlab.root",
            return_value="/opt/matlab/R2026a",
        )
        custom_prefix = str(tmp_path / "custom_prefix")
        content = "## PRODUCTS\n#product.Simulink"

        result = mpm._save_mpm_input_file(
            "input.txt", content, path_prefix=custom_prefix
        )

        assert result == f"{custom_prefix}_input.txt"
        assert Path(result).exists()
