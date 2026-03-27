# Copyright 2026 The MathWorks, Inc.

import codecs
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from . import matlab, subprocess_shim, user


def exists() -> bool:
    """Check whether the MATLAB Package Manager executable is on PATH.

    Returns:
        bool: True if ``mpm`` is found on PATH, False otherwise.
    """
    return shutil.which("mpm") is not None


def info(username: str) -> tuple[bool, str]:
    """Returns the version information about MATLAB Package Manager

    bool : true if found, false if not found
    str: additional textual information
    """
    try:
        mpm_exe_on_path = shutil.which("mpm")
        if mpm_exe_on_path is None:
            return (False, "MATLAB Package Manager is not on PATH")

        resolved_path = str(Path(mpm_exe_on_path).resolve())

        mpm_version = version(username)
        if mpm_version:
            return (True, f"{mpm_version} installed at: {str(resolved_path)}")
        else:
            return (
                False,
                f"MATLAB Package Manager version (unknown) installed at: {str(resolved_path)}",
            )

    except Exception as e:
        return (False, f"MATLAB Package Manager is not installed, error: {e}")


def version(username: str) -> Optional[str]:
    """
    Returns the output of calling "mpm --version" as the specified user.
    """
    _env = os.environ.copy()
    output = subprocess_shim.run(
        uid=user.uid(username),
        command=["mpm", "--version"],
        env=_env,
    )

    if output.returncode != 0:
        return None

    if _version := output.stdout.strip():
        return _version
    else:
        return None


def install(input_file_location: str):
    """Installs MATLAB toolboxes using `mpm` and streams the output in real-time.

    This function executes the MATLAB Package Manager (`mpm`) install command
    as a subprocess. It is implemented as a generator, using `subprocess.Popen`
    to capture the output stream as it happens. This allows the calling
    function to display installation progress line-by-line, rather than
    waiting for the entire process to complete.

    Both standard output and standard error from the `mpm` command are merged
    into a single stream and yielded.

    Args:
        input_file_location (str): The absolute path to the `mpm` input file
            (e.g., 'products.txt') that lists the toolboxes to install.

    Yields:
        str: A single, stripped line of output from the `mpm` command.

    Raises:
        ValueError: If `input_file_location` is None or an empty string.
        RuntimeError: If the `mpm` process returns a non-zero exit code,
            indicating a failure during installation.
    """
    if not input_file_location:
        raise ValueError("Input file location is required")

    command = ["mpm", "install", f"--inputfile={input_file_location}"]
    process = subprocess.Popen(
        command,
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )

    for line in iter(process.stdout.readline, ""):
        yield line.strip()
    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(f"Failed with exit code {return_code}")


def save_file(uploaded_file) -> str:
    """Saves the uploaded file to disk and returns the file location.

    Args:
        uploaded_file: The file object containing the file content and metadata.
    Returns:
        str: The location where the file is saved on disk.
    Raises:
        Exception for every failure case.
    """
    filename = uploaded_file.get("metadata").get("name")
    content_bytes = uploaded_file.get("content")
    file_content = _decode(filename, content_bytes)

    file_location = _save_mpm_input_file(filename, file_content)
    if file_content:
        return file_location
    else:
        raise RuntimeError("Failed to save mpm input file.")


################################################
## Helper Functions
################################################


def _decode(filename: str, content: bytes) -> str:
    """Validate the MPM file format and content.

    Args:
        filename (str): The name of the file being validated.
        content (bytes): The content of the file.

    Returns:
        str: Empty string if valid, error message otherwise.
    """
    # Validate that the file is of type .txt only
    file_extension = os.path.splitext(filename)[1]
    if file_extension != ".txt":
        raise ValueError(
            f"Unsupported file extension: {file_extension}, expected: .txt"
        )

    try:
        decoded_content = codecs.decode(content, encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError("File encoding error: UTF-8 decoding failed")

    if not _is_valid(decoded_content):
        raise ValueError("File content validation failed")

    return decoded_content


def _is_valid(file_content: str) -> bool:
    """Check if the parsed MPM file content contains at least one valid item.

    Args:
        file_content (str): The content of the MPM input file to validate.

    Returns:
        bool: True if at least one product, support package, or optional feature
              is present in the file content, False otherwise.
    """
    products, support_packages, optional_features = _parse_mpm_input_file(file_content)

    # Return False if there is nothing in any of the lists, True otherwise
    return (
        False
        if all([not products, not support_packages, not optional_features])
        else True
    )


def _save_mpm_input_file(
    filename: str, content: str, path_prefix: str = "/tmp/mathworks"
) -> str:
    file_location = f"{path_prefix}_{filename}"
    with open(f"{file_location}", "w") as f:
        f.write(content)

        # Append destinationFolder string to the file
        f.write(f"\n\ndestinationFolder={matlab.root()}")
    print(f"File saved and configured at: {file_location}")
    return file_location


def _parse_mpm_input_file(file_content: str):
    """Parse an MPM input file and extract products, support packages, and optional features."""
    products = []
    support_packages = []
    optional_features = []

    current_section = None

    for line in file_content.splitlines():
        line = line.strip()
        if line == "## PRODUCTS":
            current_section = "products"
        elif line == "## SUPPORT PACKAGES":
            current_section = "support_packages"
        elif line == "## OPTIONAL FEATURES":
            current_section = "optional_features"
        elif line.startswith("#product."):
            if current_section == "products":
                products.append(line.replace("#product.", "").replace("_", " "))
            elif current_section == "support_packages":
                support_packages.append(line.replace("#product.", "").replace("_", " "))
            elif current_section == "optional_features":
                optional_features.append(
                    line.replace("#product.", "").replace("_", " ")
                )

    return products, support_packages, optional_features
