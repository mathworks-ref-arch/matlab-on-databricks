# Copyright 2026 The MathWorks, Inc.

import re

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


class TestToValidLinuxUsername:
    # Mirrors the validation performed by scripts/CreateUser.sh so the Python
    # and shell layers cannot drift apart.
    VALID_USERNAME_REGEX = re.compile(r"^[a-z][-a-z0-9_]*$")
    MAX_USERNAME_LENGTH = 32

    def assert_valid_linux_username(self, username):
        assert self.VALID_USERNAME_REGEX.match(username), (
            f"'{username}' would be rejected by CreateUser.sh"
        )
        assert len(username) <= self.MAX_USERNAME_LENGTH

    @pytest.fixture
    def no_reserved_names(self, mocker):
        """Stub out the reserved-name check so sanitization is tested alone.

        Keeps these cases hermetic: without it they would consult the passwd
        database of whichever machine or image the tests run on.
        """
        return mocker.patch(
            "resources.notebooks.mwhelpers.user._is_reserved_username",
            return_value=False,
        )

    @pytest.mark.parametrize(
        "user_input, expected_output",
        [
            ("testuser@company.com", "testuser"),
            ("admin", "admin"),
            ("john.doe@company.com", "johndoe"),
            ("first.last", "firstlast"),
            ("weird!%+name@company.com", "weirdname"),
            ("user_name-1@company.com", "user_name-1"),
            ("John.Doe@company.com", "johndoe"),
            # "u_" is the single prefix used for any name that does not begin
            # with a letter, even when that produces a doubled separator.
            ("123john@company.com", "u_123john"),
            ("-user@company.com", "u_-user"),
            ("_user@company.com", "u__user"),
        ],
    )
    def test_returns_username(self, no_reserved_names, user_input, expected_output):
        assert user.to_valid_linux_username(user_input) == expected_output

    @pytest.mark.parametrize(
        "user_input, expected_output",
        [
            # "root" is present on every Linux distribution, so this exercises
            # the real passwd lookup without depending on the image in use.
            ("root@company.com", "u_96b5d910"),
            # Capitalization alone must not hand the same person a second
            # account, so the hash input is lowercased.
            ("Root@company.com", "u_96b5d910"),
            # A bare identity with no domain hashes to something different,
            # because it is a different identity.
            ("root", "u_4813494d"),
        ],
    )
    def test_replaces_reserved_system_account_with_hashed_name(
        self, user_input, expected_output
    ):
        assert user.to_valid_linux_username(user_input) == expected_output
        self.assert_valid_linux_username(user.to_valid_linux_username(user_input))

    @pytest.mark.parametrize("reserved_name", ["sys", "bin", "daemon", "nobody"])
    def test_replaces_reserved_name_for_images_that_ship_it(
        self, mocker, reserved_name
    ):
        """These accounts are not guaranteed on every image, so the passwd
        lookup is mocked rather than relying on the host."""
        mocker.patch(
            "resources.notebooks.mwhelpers.user._is_reserved_username",
            side_effect=lambda name: name == reserved_name,
        )
        username = user.to_valid_linux_username(f"{reserved_name}@company.com")
        # Shape, not a literal: pins "u_" + 8 hex chars without recomputing the
        # hash from the implementation under test.
        assert re.fullmatch(r"u_[0-9a-f]{8}", username), username
        assert reserved_name not in username
        self.assert_valid_linux_username(username)

    def test_reserved_names_from_different_domains_do_not_collide(self, mocker):
        """Two different people whose local part is a system account name must
        not be funnelled onto one shared Linux account."""
        mocker.patch(
            "resources.notebooks.mwhelpers.user._is_reserved_username",
            side_effect=lambda name: name == "sys",
        )
        first = user.to_valid_linux_username("sys@team-a.com")
        assert first != user.to_valid_linux_username("sys@team-b.com")

    def test_hashed_fallback_is_not_rechecked_against_passwd(self, mocker):
        """The hashed name is terminal: it cannot name a system account, so the
        lookup must not run again on it."""
        is_reserved = mocker.patch(
            "resources.notebooks.mwhelpers.user._is_reserved_username",
            side_effect=lambda name: name == "sys",
        )
        user.to_valid_linux_username("sys@company.com")
        is_reserved.assert_called_once_with("sys")

    def test_reuses_regular_account_created_earlier(self, mocker):
        """A previously created MATLAB user has a regular UID, so its name must
        be returned unchanged -- otherwise a restart would strand its home
        directory."""
        mocker.patch("resources.notebooks.mwhelpers.user.exists", return_value=True)
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=30000)
        assert user.to_valid_linux_username("testuser@company.com") == "testuser"

    @pytest.mark.parametrize(
        "user_input, expected_output",
        [
            # 36-character local part -> truncated to 23 chars + "_" + 8 hash chars.
            (
                "averylongfirstname.averylonglastname@company.com",
                "averylongfirstnameavery_719b59f3",
            ),
            # RFC 5321 caps an email local part at 64 octets, which cannot fit
            # in a 32-character Linux username.
            ("a" * 64 + "@company.com", "aaaaaaaaaaaaaaaaaaaaaaa_da9ec695"),
            # Databricks service principals appear as a bare 36-character UUID
            # with no domain, and start with a digit often enough to matter.
            (
                "7f3a2b1c-9d8e-4f5a-6b7c-0d1e2f3a4b5c",
                "u_7f3a2b1c-9d8e-4f5a-6b_2d02de2d",
            ),
        ],
    )
    def test_truncates_long_username_with_hash_suffix(
        self, no_reserved_names, user_input, expected_output
    ):
        username = user.to_valid_linux_username(user_input)
        # The expected values are hardcoded on purpose: they pin the hash to
        # hashlib over the per-process-salted builtin hash(), and pin its input
        # to the original identity rather than the truncated stem.
        assert username == expected_output
        assert len(username) == self.MAX_USERNAME_LENGTH
        self.assert_valid_linux_username(username)

    @pytest.mark.parametrize(
        "first_input, second_input",
        [
            # Same local part, different domain: without the domain in the hash
            # these would collide on one Linux account.
            (
                "averylongfirstname.averylonglastname@company.com",
                "averylongfirstname.averylonglastname@other-company.com",
            ),
            # Local parts that share their first 40 characters, so truncation
            # alone would merge them.
            (
                "averylongfirstname.averylonglastnameSMITH@company.com",
                "averylongfirstname.averylonglastnameJONES@company.com",
            ),
        ],
    )
    def test_long_usernames_do_not_collide(
        self, no_reserved_names, first_input, second_input
    ):
        assert user.to_valid_linux_username(
            first_input
        ) != user.to_valid_linux_username(second_input)

    def test_is_deterministic(self, no_reserved_names):
        identity = "a" * 64 + "@company.com"
        assert user.to_valid_linux_username(identity) == user.to_valid_linux_username(
            identity
        )

    def test_long_username_ignores_capitalization(self, no_reserved_names):
        """The same identity in different case must map to one Linux user, which
        requires the hash input to be lowercased like the rest of the name."""
        upper = user.to_valid_linux_username(
            "AVeryLongFirstName.AVeryLongLastName@Company.com"
        )
        assert upper == user.to_valid_linux_username(
            "averylongfirstname.averylonglastname@company.com"
        )

    @pytest.mark.parametrize("user_input", ["", None])
    def test_returns_empty_string_for_missing_identity(self, user_input):
        assert user.to_valid_linux_username(user_input) == ""


class TestIsReservedUsername:
    def test_returns_true_for_system_account(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.exists", return_value=True)
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=3)
        assert user._is_reserved_username("sys") is True

    def test_returns_false_for_regular_account(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.exists", return_value=True)
        mocker.patch("resources.notebooks.mwhelpers.user.uid", return_value=1000)
        assert user._is_reserved_username("testuser") is False

    def test_returns_false_when_user_does_not_exist(self, mocker):
        mocker.patch("resources.notebooks.mwhelpers.user.exists", return_value=False)
        assert user._is_reserved_username("nosuchuser") is False

    def test_returns_false_for_empty_username(self):
        assert user._is_reserved_username("") is False

    def test_returns_false_when_lookup_fails(self, mocker):
        """A broken or absent getent must not stop the notebook."""
        mocker.patch(
            "resources.notebooks.mwhelpers.user.exists",
            side_effect=FileNotFoundError("getent not found"),
        )
        assert user._is_reserved_username("sys") is False

    def test_detects_root_on_any_distribution(self):
        """Live passwd lookup against an account every distribution ships."""
        assert user._is_reserved_username("root") is True
