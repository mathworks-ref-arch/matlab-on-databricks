# Copyright 2026 The MathWorks, Inc.

import logging
import time

logger = logging.getLogger(__name__)


def wait_for_process(host, process_substr, timeout=30):
    """
    Waits for a specific process to start running inside the container.

    Args:
        host: The Docker container object (from docker-py).
        process_substr (str): A substring to match against running processes (via 'ps').
        timeout (int): Maximum time to wait in seconds. Defaults to 30.

    Raises:
        ValueError: If the process does not start within the timeout.
    """
    logger.info(f"Waiting for process '{process_substr}' to start...")
    try:
        wait_for(
            lambda: process_substr in host.check_output("ps -ax -o cmd="),
            timeout=timeout,
        )
    except TimeoutError as e:
        logger.error(f"Process '{process_substr}' failed to start within {timeout}s")
        raise ValueError(
            f"The process with {process_substr} substring did not start running within {timeout}s"
        ) from e


def wait_for(bool_func, timeout=60, interval=0.3, description=None):
    """
    Generic polling helper that waits for a condition to become True.

    Args:
        bool_func (callable): A function that returns a boolean.
        timeout (int): Maximum time to wait in seconds. Defaults to 60.
        interval (float): Time to sleep between checks in seconds. Defaults to 0.3.
        description (str): Description of the condition being waited for. Defaults to None.

    Raises:
        TimeoutError: If the condition is not met within the timeout.
    """
    deadline = time.time() + timeout
    while time.time() <= deadline:
        if bool_func():
            return
        time.sleep(interval)

    desc = description if description else repr(bool_func)
    raise TimeoutError(f"The condition {desc} is still false after {timeout} seconds")


def run_matlab_code(host, code, check=True):
    """
    Executes MATLAB code inside the container using batch mode.

    Args:
        host: The testinfra host object.
        code (str): The MATLAB code to execute.
        check (bool): If True, raise RuntimeError on non-zero exit code. Defaults to True.

    Returns:
        ExecResult: The result object containing exit code and output.

    Raises:
        RuntimeError: If check is True and the MATLAB execution returns a non-zero exit code.
    """
    matlab_cmd = f'matlab -batch "{code}"'
    result = host.run(matlab_cmd)
    logger.info(
        f"MATLAB execution details:\n"
        f"Command:\n{matlab_cmd}\n"
        f"\nResult:\n{result.stdout}\n{result.stderr}"
    )
    if check and result.exit_status != 0:
        raise RuntimeError("MATLAB execution failed.\n")
    return result


def run_matlab_test(host, test_file_path):
    """
    Runs a specific MATLAB test file inside the container.

    Args:
        host: The testinfra host object.
        test_file_path (str): Path to the MATLAB test file inside the container.

    Returns:
        ExecResult: The result of the execution.
    """
    return run_matlab_code(host, f"assertSuccess(runtests('{test_file_path}'))")


def run_python_test(host, test_file_path, python_bin_path):
    """
    Runs a python test file inside the container.

    It changes directory to the test file's location to ensure relative imports
    work correctly, then invokes 'unittest' on the file.

    Args:
        host: The testinfra host object.
        test_file_path (str): Path to the Python test file inside the container.
        python_bin_path (str): Path to the directory containing the python3 executable.

    Returns:
        ExecResult: The result of the execution.
    """
    python_cmd = (
        f"export PATH={python_bin_path}:$PATH; "
        f'cd "$(dirname "{test_file_path}")" && '
        f'python3 -m unittest -v "$(basename "{test_file_path}")" 2>&1'
    )
    result = host.run(python_cmd)
    logger.info(
        f"Python execution details:\n"
        f"Command:\n{python_cmd}\n"
        f"\nResult:\n{result.stdout}\n{result.stderr}"
    )
    if result.exit_status != 0:
        raise RuntimeError("Python execution failed.\n")
    return result
