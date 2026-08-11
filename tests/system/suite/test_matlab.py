# Copyright 2026 The MathWorks, Inc.

from pathlib import Path

MATLAB_TEST_DIR = Path(__file__).parent / "matlab_tests"


def test_matlab(matlab_eng):
    matlab_eng.eval(
        f"results = runtests('{MATLAB_TEST_DIR}'); assertSuccess(results);",
        nargout=0,
    )
