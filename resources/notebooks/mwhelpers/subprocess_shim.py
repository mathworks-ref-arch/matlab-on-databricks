# Copyright 2026 The MathWorks, Inc.
import shlex
import subprocess


def run_runuser(
    username: str,
    command: str,
    env: dict[str, str],
    whitelist_env_vars: str = "",
    debug: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run a command as a specific user and return the output.
        whitelist_env_vars is a comma separated string of environment variable names that should be whitelisted and
            passed to the command being executed as the user. This is required because by default, when using 'runuser',
            the environment variables are not passed to the command being executed for security reasons.
            By whitelisting specific environment variables, we can ensure that only the necessary environment variables
            are passed to the command, while keeping the rest of the environment variables secure.
    """

    whitelist_command = ""
    if whitelist_env_vars:
        whitelist_command = f"--whitelist-environment={whitelist_env_vars}"

    full_command = shlex.split(
        f"runuser -l {username} {shlex.quote(whitelist_command)} -c {shlex.quote(command)}"
    )
    if debug:
        print(f"Running command: {full_command}")
    output = subprocess.run(full_command, env=env, capture_output=True, text=True)
    return output


def run(
    uid: int, command: list[str], env: dict[str, str], debug: bool = False
) -> subprocess.CompletedProcess:
    """Run a command as a specific user and return the output.

    Uses the subprocess 'user' parameter (Python 3.9+) instead of the deprecated
    'preexec_fn' approach. preexec_fn is unsafe in multithreaded programs because
    it runs between fork() and exec(), where only async-signal-safe functions are
    allowed. The 'user' parameter handles setuid safely within the subprocess module.
    """
    if debug:
        print(f"Waiting for command to complete: {command}")
    output = subprocess.run(command, env=env, user=uid, capture_output=True, text=True)
    return output


def spawn(
    uid: int, command: list[str], env: dict[str, str], debug: bool = False
) -> subprocess.Popen:
    """Spawn a long-running background process as a specific user.

    Uses the subprocess 'user' parameter (Python 3.9+) instead of the deprecated
    'preexec_fn' approach for thread safety. See run() docstring for details.
    """
    if debug:
        print(f"Spawning process with command: {command}")
    return subprocess.Popen(
        command, env=env, user=uid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
