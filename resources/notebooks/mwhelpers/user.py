# Copyright 2026 The MathWorks Inc.

"""Functions related to user management on the Databricks cluster."""

import subprocess
from pathlib import Path

################################################
## Start Private functions ##
################################################


def _get_passwd_entry_for_user(username: str, field_index: int = 0) -> str:
    """Returns the result of searching Name Service Switch Library PASSWD.
    Returns empty string if the user is not found.

    passwd output format (1-indexed to match field_index convention):
        field 1: username
        field 2: password (x)
        field 3: UID
        field 4: GID
        field 5: GECOS
        field 6: home_directory
        field 7: login_shell

    Args:
        username: The username to look up.
        field_index: 1-indexed field number to extract, or 0 to return the full line.
                     E.g., field_index=3 returns UID, field_index=6 returns home_directory.
    """

    if not username:
        raise ValueError("Aborting, no username provided.")

    execution_result = subprocess.run(
        ["getent", "passwd", username], capture_output=True, text=True
    )
    if execution_result.returncode != 0:
        # Implies the user was not found
        return ""

    if field_index == 0:
        return execution_result.stdout.strip()
    else:
        return execution_result.stdout.strip().split(":")[field_index - 1]


def _call_CreateUser_script(username: str) -> str:
    """Creates a user with the given username."""

    if not username:
        raise ValueError("Aborting, no username provided.")

    script_path = Path(__file__).parent / "scripts" / "CreateUser.sh"
    result = subprocess.run(
        [str(script_path), "-u", username],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error creating user: {result.stderr}")

    return result.stdout.strip()


################################################
## End Private functions ##
################################################


def create(username: str) -> int:
    """Create a user with the given username."""
    """ If the user already exists, it returns the UID of the user."""
    if not username:
        raise ValueError("Aborting, no username provided.")

    print(f"Creating user: {username}")
    call_result = _call_CreateUser_script(username)
    if call_result:
        return uid(username)

    raise RuntimeError(f"Unable to create user: {username}")


def exists(username: str) -> bool:
    """Returns true if the user exists on the system, false otherwise."""
    if not username:
        raise ValueError("Aborting, no username provided.")
    return _get_passwd_entry_for_user(username) != ""


def home_folder(username: str, create_if_not_exists: bool = False) -> Path:
    """Get the home folder for the provided username, if user exists."""
    if not username:
        raise ValueError("Aborting, no username provided.")

    if _home_folder := _get_passwd_entry_for_user(username, field_index=6):
        return Path(_home_folder)

    if create_if_not_exists:
        create(username)
        return home_folder(username)

    raise RuntimeError(f"Unable to find home folder for user {username}")


def uid(username: str, create_if_not_exists: bool = False) -> int:
    """Get the UID of the user from passwd entry for user"""
    if not username:
        raise ValueError("Aborting, no username provided.")

    if _uid := _get_passwd_entry_for_user(username, field_index=3):
        return int(_uid)

    if create_if_not_exists:
        return create(username)

    raise RuntimeError(f"Unable to find UID for user {username}")
