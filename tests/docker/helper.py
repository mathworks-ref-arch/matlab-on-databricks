# Copyright 2026 The MathWorks, Inc.

import ast
import logging
import time
from pathlib import Path

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
        raise RuntimeError(
            f"MATLAB execution failed.\n"
            f"Stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
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


def discover_test_functions(local_test_file):
    """
    Discovers all test_* functions in a Python file using AST parsing.

    Args:
        local_test_file (str or Path): Path to the Python test file on the host.

    Returns:
        list[str]: Sorted list of test function names.
    """
    source = Path(local_test_file).read_text()
    tree = ast.parse(source)
    return sorted(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def run_python_function(host, test_file, function_name, python_bin_path):
    """
    Runs a specific Python test function inside the container.

    Args:
        host: The testinfra host object.
        test_file (str): Filename of the test module (e.g. 'matlab_in_container_tests').
        function_name (str): Name of the function to call.
        python_bin_path (str): Path to the directory containing the python3 executable.

    Returns:
        ExecResult: The result object containing exit code and output.
    """
    cmd = (
        f"export PATH={python_bin_path}:$PATH; "
        f'python3 -c "from {test_file} import {function_name}; {function_name}()"'
    )
    result = host.run(cmd)
    logger.info(
        f"Python test '{function_name}' details:\n"
        f"Stdout:\n{result.stdout}\n"
        f"Stderr:\n{result.stderr}\n"
        f"Exit Status: {result.exit_status}"
    )
    return result
