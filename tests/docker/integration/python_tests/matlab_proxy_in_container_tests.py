# Copyright 2026 The MathWorks, Inc.
# These tests are designed to run INSIDE the docker container

import os
import socket
import time
import warnings

from resources.notebooks.mwhelpers import dbx, matlab_proxy


def _wait_for_port(port, timeout=10):
    """Poll a local port to see if it is listening."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", int(port))) == 0:
                return True
        time.sleep(1)
    return False


def test_matlab_session_lifecycle():
    warnings.simplefilter("ignore", category=ResourceWarning)
    port = None
    username = "proxy_user"
    try:
        port = matlab_proxy.start(username=username, dbx_context=dbx.get_context())

        assert port, "Failed to start MATLAB proxy, port returned empty"
        assert _wait_for_port(port), f"No service is listening on port {port}"

        assert os.path.isdir(f"/home/{username}"), (
            f"Home directory for {username} was not created"
        )

        servers = matlab_proxy.list_servers_ports(username=username)
        assert servers == [port], (
            f"Expected running servers: [{port}], Actual servers: {servers}"
        )

        matlab_proxy.stop(username=username, port=int(port))

        servers = matlab_proxy.list_servers_ports(username=username)
        assert servers == [], f"Expected running servers: [], Actual servers: {servers}"
    except Exception:
        # Ensure cleanup on failure
        if port:
            servers = matlab_proxy.list_servers_ports(username=username)
            if port in servers:
                matlab_proxy.stop(username=username, port=int(port))
        raise
