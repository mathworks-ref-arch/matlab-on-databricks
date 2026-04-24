# Copyright 2026 The MathWorks, Inc.
# These tests are designed to run INSIDE the docker container

import os

from resources.notebooks.mwhelpers import matlab


def test_root():
    actual_path = matlab.root()
    expected_path = f"/opt/matlab/{os.environ.get('MATLAB_RELEASE')}"
    assert actual_path == expected_path, f"Expected {expected_path}, got {actual_path}"


def test_version():
    actual_version = matlab.version()
    expected_version = os.environ.get("MATLAB_RELEASE")
    assert expected_version in actual_version, (
        f"Expected {expected_version} in {actual_version}"
    )


def test_installed_toolboxes():
    toolboxes = matlab.installed_toolboxes(username="root")
    assert toolboxes == ["MATLAB", "Database Toolbox"], (
        f"Expected ['MATLAB', 'Database Toolbox'], got {toolboxes}"
    )


def test_run_code_with_matlab_batch():
    code = "disp(40 + 2)"
    success, output = matlab.run_code_with_matlab_batch(username="root", code=code)
    assert success, f"MATLAB execution failed. Output: {output}"
    assert "42" in output, f"Expected '42' in output, got: {output}"
