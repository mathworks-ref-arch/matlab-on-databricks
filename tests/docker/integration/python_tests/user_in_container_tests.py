# Copyright 2026 The MathWorks, Inc.
# These tests are designed to run INSIDE the docker container

import os

from resources.notebooks.mwhelpers import user


def test_create_user_lifecycle():
    username = "test_user"

    uid = user.create(username)

    assert user.exists(username), f"User {username} should exist after creation"
    assert user.uid(username) == uid, (
        f"UID mismatch: expected {uid}, got {user.uid(username)}"
    )

    home_path = user.home_folder(username)
    assert os.path.isdir(home_path), f"Home directory {home_path} was not created"

    stat_info = os.stat(home_path)
    assert stat_info.st_uid == uid, (
        f"Home directory owner UID {stat_info.st_uid} does not match user UID {uid}"
    )
