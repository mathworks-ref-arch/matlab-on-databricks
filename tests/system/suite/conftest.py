# Copyright 2026 The MathWorks, Inc.

"""Shared pytest fixtures for system tests running on Databricks."""

import os
import time

import matlab.engine
import pytest


@pytest.fixture(scope="session")
def matlab_engine_timeout():
    """
    Timeout in seconds for waiting on the shared MATLAB engine.
    """
    return 300


@pytest.fixture(scope="session")
def matlab_eng(matlab_engine_timeout):
    """
    Wait for and connect to the shared MATLAB engine started by matlab-proxy.

    The engine name is passed via MATLAB_ENGINE_NAME env var from run_tests.py.
    The MATLAB session already has DSP, pyenv, and Spark Connect configured
    via the matlab-proxy startup script (onDatabricksSetup).
    """
    engine_name = os.environ.get("MATLAB_ENGINE_NAME", "MatlabSystemTest")

    start_time = time.time()
    while time.time() - start_time < matlab_engine_timeout:
        if engine_name in matlab.engine.find_matlab():
            break
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        if elapsed % 30 == 0:
            print(f"Waiting for MATLAB engine '{engine_name}'... ({elapsed}s)")
    else:
        pytest.fail(
            f"MATLAB engine '{engine_name}' not found after {matlab_engine_timeout}s"
        )

    eng = matlab.engine.connect_matlab(engine_name)
    yield eng
    # Don't close as matlab-proxy owns the session lifecycle
