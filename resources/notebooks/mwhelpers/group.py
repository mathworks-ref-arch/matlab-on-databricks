# Copyright 2026 The MathWorks, Inc.

"""Functions related to the Linux group of MATLAB users on the Databricks cluster."""

import grp
import pwd
import subprocess

# matlab_proxy.start adds every user it starts a MATLAB session for to this group.
# The cluster keep-alive looks for MATLAB sessions of all its members.
MWI_USERS_GROUP = "mwi-users"


def mwi_users_group_members() -> list[str]:
    """Returns the members of the group, or an empty list if the group does not exist.

    Only supplementary members are listed, which is how users are added to it.
    """
    try:
        return grp.getgrnam(MWI_USERS_GROUP).gr_mem
    except KeyError:
        # The group does not exist yet, e.g. because no user was created yet
        return []


def add_user_to_mwi_users_group(username: str) -> None:
    """Adds the user to the MATLAB users group, creating the group if needed.

    Does nothing if the user is already a member, so that ``/etc/group`` is not
    rewritten, and possibly locked against a concurrent session start, every time.

    Failures are reported but not raised: the MATLAB session still works, only the
    cluster keep-alive will not see it.
    """
    try:
        pwd.getpwnam(username)
    except KeyError:
        print(
            f"Warning: user {username} does not exist, so it was not added to group "
            f"{MWI_USERS_GROUP}. The cluster may auto-terminate on idle."
        )
        return

    if username in mwi_users_group_members():
        return
    try:
        for command in (
            ["groupadd", "-f", MWI_USERS_GROUP],
            ["usermod", "-aG", MWI_USERS_GROUP, username],
        ):
            subprocess.run(command, check=True, capture_output=True, text=True)
        return
    except subprocess.CalledProcessError as e:
        reason = e.stderr.strip() or str(e)
    except OSError as e:
        reason = str(e)

    # A concurrent session start may have added the user while this one failed.
    if username in mwi_users_group_members():
        return
    print(
        f"Warning: could not add user {username} to group {MWI_USERS_GROUP} "
        f"({reason}). The cluster may auto-terminate on idle."
    )
