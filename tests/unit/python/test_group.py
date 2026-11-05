# Copyright 2026 The MathWorks, Inc.

import subprocess

import pytest

from resources.notebooks.mwhelpers import group


class TestMwiUsersGroupMembers:
    def test_returns_members_of_mwi_users_group(self, mocker):
        mock_getgrnam = mocker.patch(
            "resources.notebooks.mwhelpers.group.grp.getgrnam",
            return_value=mocker.Mock(gr_mem=["alice", "bob"]),
        )

        assert group.mwi_users_group_members() == ["alice", "bob"]
        mock_getgrnam.assert_called_once_with("mwi-users")

    def test_returns_empty_list_when_group_has_no_members(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.group.grp.getgrnam",
            return_value=mocker.Mock(gr_mem=[]),
        )

        assert group.mwi_users_group_members() == []

    def test_returns_empty_list_when_group_does_not_exist(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.group.grp.getgrnam",
            side_effect=KeyError("getgrnam(): name not found: 'mwi-users'"),
        )

        assert group.mwi_users_group_members() == []

    def test_reads_group_from_the_system(self, monkeypatch):
        """Live group lookup against a group every distribution ships."""
        monkeypatch.setattr(group, "MWI_USERS_GROUP", "root")
        assert isinstance(group.mwi_users_group_members(), list)


class TestAddUserToMwiUsersGroup:
    @pytest.fixture(autouse=True)
    def mock_getpwnam(self, mocker):
        """Make the test users exist, whatever the machine running the tests has."""
        return mocker.patch("resources.notebooks.mwhelpers.group.pwd.getpwnam")

    def test_creates_group_and_adds_user(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.group.mwi_users_group_members",
            return_value=["alice"],
        )
        mock_run = mocker.patch("resources.notebooks.mwhelpers.group.subprocess.run")

        group.add_user_to_mwi_users_group("bob")

        assert [c.args[0] for c in mock_run.call_args_list] == [
            ["groupadd", "-f", "mwi-users"],
            ["usermod", "-aG", "mwi-users", "bob"],
        ]
        for c in mock_run.call_args_list:
            assert c.kwargs["check"] is True

    def test_does_nothing_when_user_is_already_a_member(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.group.mwi_users_group_members",
            return_value=["bob"],
        )
        mock_run = mocker.patch("resources.notebooks.mwhelpers.group.subprocess.run")

        group.add_user_to_mwi_users_group("bob")

        mock_run.assert_not_called()

    def test_warns_with_stderr_when_command_fails(self, mocker, capsys):
        mocker.patch(
            "resources.notebooks.mwhelpers.group.mwi_users_group_members",
            return_value=[],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.group.subprocess.run",
            side_effect=subprocess.CalledProcessError(
                6, "usermod", stderr="usermod: user 'bob' does not exist\n"
            ),
        )

        group.add_user_to_mwi_users_group("bob")

        output = capsys.readouterr().out
        assert "Warning: could not add user bob to group mwi-users" in output
        # The trailing newline of stderr must not break the warning across lines
        assert "(usermod: user 'bob' does not exist). " in output

    def test_warns_when_command_is_missing(self, mocker, capsys):
        mocker.patch(
            "resources.notebooks.mwhelpers.group.mwi_users_group_members",
            return_value=[],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.group.subprocess.run",
            side_effect=FileNotFoundError("No such file or directory: 'groupadd'"),
        )

        group.add_user_to_mwi_users_group("bob")

        assert "No such file or directory: 'groupadd'" in capsys.readouterr().out

    def test_warns_and_skips_commands_when_user_does_not_exist(
        self, mocker, mock_getpwnam, capsys
    ):
        mock_getpwnam.side_effect = KeyError("getpwnam(): name not found: 'bob'")
        mock_run = mocker.patch("resources.notebooks.mwhelpers.group.subprocess.run")

        group.add_user_to_mwi_users_group("bob")

        mock_run.assert_not_called()
        assert "Warning: user bob does not exist" in capsys.readouterr().out

    def test_does_not_warn_when_concurrent_start_added_the_user(self, mocker, capsys):
        # Not a member before the commands run, but a member after they fail.
        mocker.patch(
            "resources.notebooks.mwhelpers.group.mwi_users_group_members",
            side_effect=[[], ["bob"]],
        )
        mocker.patch(
            "resources.notebooks.mwhelpers.group.subprocess.run",
            side_effect=subprocess.CalledProcessError(
                10, "usermod", stderr="usermod: cannot lock /etc/group\n"
            ),
        )

        group.add_user_to_mwi_users_group("bob")

        assert capsys.readouterr().out == ""
