# Copyright 2026 The MathWorks, Inc.

import pytest

from resources.notebooks.mwhelpers import user


class TestExists:
    def test_returns_true_when_user_exists(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(
                returncode=0, stdout="testuser:x:1001:1001::/home/testuser:/bin/bash\n"
            ),
        )
        assert user.exists("testuser") is True

    def test_returns_false_when_user_not_found(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(returncode=2, stdout=""),
        )
        assert user.exists("nonexistent") is False

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            user.exists("")


class TestUid:
    def test_returns_uid_when_user_exists(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(
                returncode=0, stdout="testuser:x:1001:1001::/home/testuser:/bin/bash"
            ),
        )
        assert user.uid("testuser") == 1001

    def test_raises_runtime_error_when_user_not_found(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(returncode=2, stdout=""),
        )
        with pytest.raises(RuntimeError, match="Unable to find UID"):
            user.uid("nonexistent")

    def test_creates_user_when_create_if_not_exists_is_true(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(returncode=2, stdout=""),
        )
        mock_create = mocker.patch(
            "resources.notebooks.mwhelpers.user.create",
            return_value=1001,
        )
        result = user.uid("newuser", create_if_not_exists=True)
        assert result == 1001
        mock_create.assert_called_once_with("newuser")

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            user.uid("")


class TestHomeFolder:
    def test_returns_home_folder_when_user_exists(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user._get_passwd_entry_for_user",
            return_value="/home/testuser",
        )
        from pathlib import Path

        assert user.home_folder("testuser") == Path("/home/testuser")

    def test_raises_runtime_error_when_user_not_found(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user._get_passwd_entry_for_user",
            return_value="",
        )
        with pytest.raises(RuntimeError, match="Unable to find home folder"):
            user.home_folder("nonexistent")

    def test_creates_user_when_create_if_not_exists_is_true(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user._get_passwd_entry_for_user",
            side_effect=["", "/home/newuser"],
        )
        mock_create = mocker.patch(
            "resources.notebooks.mwhelpers.user.create",
            return_value=1001,
        )
        from pathlib import Path

        result = user.home_folder("newuser", create_if_not_exists=True)
        assert result == Path("/home/newuser")
        mock_create.assert_called_once_with("newuser")

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            user.home_folder("")


class TestCreate:
    def test_creates_user_and_returns_uid(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user._call_CreateUser_script",
            return_value="User created successfully",
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.user.uid",
            return_value=1001,
        )
        assert user.create("newuser") == 1001

    def test_raises_runtime_error_on_script_failure(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user._call_CreateUser_script",
            return_value="",
        )
        with pytest.raises(RuntimeError, match="Unable to create user"):
            user.create("baduser")

    def test_raises_value_error_when_username_empty(self):
        with pytest.raises(ValueError, match="no username provided"):
            user.create("")


class TestGetPasswdEntry:
    def test_returns_full_entry_when_field_index_zero(self, mocker):
        passwd_line = "testuser:x:1001:1001::/home/testuser:/bin/bash"
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(returncode=0, stdout=passwd_line),
        )
        assert user._get_passwd_entry_for_user("testuser") == passwd_line

    def test_returns_specific_field_by_index(self, mocker):
        passwd_line = "testuser:x:1001:1001::/home/testuser:/bin/bash"
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(returncode=0, stdout=passwd_line),
        )
        # field_index=3 returns UID (third field, 0-indexed in split = index 2)
        assert user._get_passwd_entry_for_user("testuser", field_index=3) == "1001"

    def test_returns_empty_string_when_user_not_found(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.user.subprocess.run",
            return_value=mocker.Mock(returncode=2, stdout=""),
        )
        assert user._get_passwd_entry_for_user("nonexistent") == ""
