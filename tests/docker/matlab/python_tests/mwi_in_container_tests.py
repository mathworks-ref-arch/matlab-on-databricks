# Copyright 2026 The MathWorks, Inc.
# These tests are designed to run INSIDE the docker container

import os
import socket
import time
import unittest
import warnings

# Mock missing databricks modules to prevent ImportErrors.
from resources.notebooks.mwhelpers import dbx, matlab, matlab_proxy


class TestMWIInstallation(unittest.TestCase):
    def test_get_installed_toolboxes(self):
        """
        Verify that 'get_installed_toolboxes' returns a list of installed products.
        """
        result = matlab.installed_toolboxes(username="root")
        self.assertEqual(
            result,
            ["MATLAB", "Database Toolbox"],
            f"Expected toolboxes: ['MATLAB', 'Database Toolbox'], Actual toolboxes: {result}",
        )

    def test_get_matlab_version(self):
        """
        Verify that 'get_matlab_version' returns a valid version string.
        """
        result = matlab.version()
        expected_release = os.environ.get("MATLAB_RELEASE")
        self.assertIn(
            expected_release,
            result,
            f"Expected {expected_release} to be present in {result}",
        )

    def test_get_matlab_root(self):
        """
        Verify that 'get_matlab_root' returns a valid MATLAB root path.
        """
        result = matlab.root()
        expected_path = f"/opt/matlab/{os.environ.get('MATLAB_RELEASE')}"
        self.assertEqual(
            result,
            expected_path,
            f"Expected path: {expected_path}, Actual path: {result}",
        )


class TestMWIMATLABProxy(unittest.TestCase):
    username = "proxy_user"
    port = None

    def setUp(self):
        # Suppress ResourceWarning caused by subprocess.Popen in mwi.start_matlab_session
        # leaving a process running (which is intended behavior for the proxy server)
        warnings.simplefilter("ignore", category=ResourceWarning)

    def check_port(self, port, timeout=10):
        """
        Helper function to poll a local port to see if it is listening.

        Args:
            port (int/str): The port number to check.
            timeout (int): Max seconds to wait for the port to open.

        Returns:
            bool: True if port is open, False if timeout occurred.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", int(port))) == 0:
                    return True
            time.sleep(1)
        return False

    def test_matlab_session_lifecycle(self):
        """
        Full integration test for the session lifecycle:
        1. Start the session.
        2. Verify the port is listening.
        3. Verify the user directory was created.
        4. Verify the session is tracked in the server list.
        5. Stop the session.
        6. Verify the session is removed from the server list.
        """
        # Start MATLAB session
        self.port = matlab_proxy.start(
            username=self.username, dbx_context=dbx.get_context()
        )
        self.assertIsNotNone(self.port)
        # Ensure port is listening
        self.assertTrue(
            self.check_port(self.port), f"No service is listening on port {self.port}"
        )
        # Ensure user home is created
        self.assertTrue(os.path.isdir(f"/home/{self.username}"))
        # Get running MATLAB proxy servers
        servers = matlab_proxy.list_servers_ports(username=self.username)
        self.assertEqual(
            servers,
            [self.port],
            f"Expected running servers: [{self.port}], Actual servers: {servers}",
        )
        # Stop MATLAB session
        matlab_proxy.stop(username=self.username, port=int(self.port))
        # Ensure that there are no running MATLAB proxy servers
        servers = matlab_proxy.list_servers_ports(username=self.username)
        self.assertEqual(
            servers, [], f"Expected running servers: [], Actual servers: {servers}"
        )

    def tearDown(self):
        """
        Ensure that the MATLAB session is stopped even if the test fails.
        """
        if self.port:
            servers = matlab_proxy.list_servers_ports(username=self.username)
            if self.port in servers:
                matlab_proxy.stop(username=self.username, port=int(self.port))
