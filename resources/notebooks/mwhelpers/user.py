# Copyright 2026 The MathWorks Inc.

"""Functions related to user management on the Databricks cluster."""

import hashlib
import re
import subprocess
from pathlib import Path

# adduser and shadow-utils limit usernames to 32 characters (the historical
# utmp limit), even though glibc's LOGIN_NAME_MAX is larger. CreateUser.sh
# enforces the same limit. The local part of an email address may be up to 64
# octets (RFC 5321), so sanitized names can legitimately overflow this.
_MAX_USERNAME_LENGTH = 32

# Number of hash characters appended to disambiguate truncated usernames.
# 8 hex characters give 4.3 billion values, which makes collisions negligible
# at workspace scale while leaving enough of the original name to be readable.
_HASH_SUFFIX_LENGTH = 8

# Separates a hash from whatever it is attached to, be that a truncated stem
# ("johnsmith_719b59f3") or the prefix alone ("u_719b59f3").
_HASH_SEPARATOR = "_"

# Accounts below this UID are system accounts by convention (see UID_MIN in
# /etc/login.defs); MATLAB must never be run as one of them.
_MIN_REGULAR_UID = 1000

# The single decoration used by this module. It marks a name that could not be
# used verbatim, whether because it did not start with a letter ("u_123john")
# or because it had to be replaced by a hash entirely ("u_18a68f29").
_USERNAME_PREFIX = "u_"

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


def _username_hash(raw_username: str) -> str:
    """Return a short, stable hash of the whole Databricks identity.

    Hashing the whole identity (rather than the sanitized or truncated form)
    means two identities that sanitize to the same text still map to different
    Linux users -- including two that differ only by email domain. The input is
    lowercased so that a difference in capitalization alone does not hand the
    same person two accounts.

    ``hashlib`` is required here: the builtin ``hash()`` is salted per process,
    so it would return a different username on every cluster restart and orphan
    the previous home directory.
    """
    digest = hashlib.sha256(raw_username.lower().encode("utf-8")).hexdigest()
    return digest[:_HASH_SUFFIX_LENGTH]


def _hashed_username(raw_username: str) -> str:
    """Return a fully hashed username, e.g. "u_2d1757f5".

    This is the terminal fallback: the result is always a valid Linux username,
    is always well within ``_MAX_USERNAME_LENGTH``, and cannot collide with a
    system account, so it never needs further checking.
    """
    return f"{_USERNAME_PREFIX}{_username_hash(raw_username)}"


def _is_reserved_username(username: str) -> bool:
    """Return True if the name belongs to an existing system account.

    Databricks images ship differing sets of system accounts, so the check is
    made against the live passwd database rather than a hardcoded list. A name
    that is free, or that belongs to a regular account we created earlier, is
    not reserved -- so repeated calls keep returning the same username.

    If the lookup itself fails (no ``getent`` available, for instance), fall
    back to treating the name as usable rather than failing the notebook.
    """
    if not username:
        return False

    try:
        if not exists(username):
            return False
        return uid(username) < _MIN_REGULAR_UID
    except Exception:
        return False


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


def to_valid_linux_username(raw_username: str | None) -> str:
    """Convert a Databricks identity into a username Linux will accept.

    The result always satisfies the rules enforced by ``scripts/CreateUser.sh``:
    it starts with a lowercase letter, contains only lowercase letters, digits,
    "_" and "-", and is at most 32 characters long. The mapping is
    deterministic, so the same identity always yields the same Linux user.

    Every name that cannot be used verbatim carries the same "u_" marker.

    Examples:
        "john@mw.com"                -> "john"
        "john.doe@company.com"       -> "johndoe"
        "123john@company.com"        -> "u_123john"        (no leading letter)
        "sys@company.com"            -> "u_18a68f29"       (system account)
        "<36-char-local-part>@x.com" -> "averylongfirstnameavery_719b59f3"
    """
    if not raw_username:
        return ""

    # If the identity is an email address, keep only the local part.
    # Example: "john@mw.com" -> "john"
    username = raw_username.split("@")[0] if "@" in raw_username else raw_username

    # The local part of an email may contain characters that are not valid in a
    # Linux username (e.g. "." in "john.doe" or "!%+" and other specials).
    # Strip everything except lowercase/uppercase letters, digits, "_" and "-".
    # Example: "john.doe" -> "johndoe"
    username = re.sub(r"[^A-Za-z0-9_-]", "", username)

    # Linux usernames are conventionally lowercase.
    username = username.lower()

    # A username must start with an alphabetic character; prefix "u_" if it
    # starts with anything else (e.g. "123john" -> "u_123john"). An address whose
    # local part is made up entirely of stripped characters is not a valid email
    # address, so the empty case here is unreachable in practice; the check is
    # written to tolerate it rather than raise IndexError.
    if not username or not username[0].isalpha():
        username = _USERNAME_PREFIX + username

    # Never hand back the name of a system account: "sys@company.com" would
    # otherwise resolve to the real "sys" user (UID 3, HOME=/dev). Prefixing it
    # instead ("u_sys") would just be another guess that could itself be taken,
    # so switch to the hashed name, which cannot collide with a system account
    # and therefore needs no further checking.
    if _is_reserved_username(username):
        return _hashed_username(raw_username)

    # Clamp to the length Linux accepts, keeping a readable stem and appending a
    # hash so that two long identities do not share a single Linux account.
    # This runs last because the steps above can lengthen the name.
    if len(username) > _MAX_USERNAME_LENGTH:
        stem_length = _MAX_USERNAME_LENGTH - _HASH_SUFFIX_LENGTH - len(_HASH_SEPARATOR)
        username = (
            username[:stem_length] + _HASH_SEPARATOR + _username_hash(raw_username)
        )

    return username
