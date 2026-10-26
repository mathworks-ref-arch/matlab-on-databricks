# Copyright 2026 The MathWorks, Inc.

import pytest

JDBC_DRIVER_DIR = "/drivers/jdbc"
JDBC_DRIVER_CLASS = "com.databricks.client.jdbc.Driver"


def _find_driver_jars(host):
    """
    Returns the paths of all Databricks JDBC driver JAR files in the driver folder.
    """
    result = host.run(
        f"find {JDBC_DRIVER_DIR} -maxdepth 1 -name 'databricks-jdbc-*.jar'"
    )
    return result.stdout.split()


@pytest.mark.parametrize("docker_host", [{"command": "sleep infinity"}], indirect=True)
class TestJdbcDriver:
    def test_driver_dir_env_var(self, docker_host):
        """
        Verifies that MW_DATABRICKS_JDBC_DRIVER_DIR points to the JDBC driver folder.
        """
        actual_value = docker_host.environment().get(
            "MW_DATABRICKS_JDBC_DRIVER_DIR", ""
        )
        assert actual_value == JDBC_DRIVER_DIR, (
            f"Expected MW_DATABRICKS_JDBC_DRIVER_DIR={JDBC_DRIVER_DIR}, but got {actual_value}"
        )

    def test_single_driver_jar(self, docker_host):
        """
        Verifies that exactly one Databricks JDBC driver JAR file is present.
        """
        jars = _find_driver_jars(docker_host)
        assert len(jars) == 1, (
            f"Expected exactly one databricks-jdbc-*.jar in {JDBC_DRIVER_DIR}, but found {jars}"
        )

    def test_driver_license(self, docker_host):
        """
        Verifies that the JDBC driver license is included next to the driver.
        """
        assert docker_host.file(f"{JDBC_DRIVER_DIR}/LICENSE").is_file, (
            f"JDBC driver license not found at {JDBC_DRIVER_DIR}/LICENSE"
        )

    @pytest.mark.parametrize("file_name", ["databricks-jdbc-*.jar", "LICENSE"])
    def test_driver_files_readable_by_non_root_user(self, docker_host, file_name):
        """
        Verifies that the non-root user can read the JDBC driver files.
        """
        result = docker_host.run(
            f"runuser -u ubuntu -- sh -c 'cat {JDBC_DRIVER_DIR}/{file_name} > /dev/null'"
        )
        assert result.exit_status == 0, (
            f"User ubuntu cannot read {JDBC_DRIVER_DIR}/{file_name}: {result.stderr}"
        )

    def test_driver_class_registered(self, docker_host):
        """
        Verifies that the JAR file registers the Databricks OSS JDBC driver class.
        """
        jars = _find_driver_jars(docker_host)
        assert jars, f"No databricks-jdbc-*.jar found in {JDBC_DRIVER_DIR}"
        registered = docker_host.check_output(
            f"unzip -p {jars[0]} META-INF/services/java.sql.Driver"
        )
        assert JDBC_DRIVER_CLASS in registered, (
            f"Expected {JDBC_DRIVER_CLASS} to be registered in {jars[0]}, but got {registered}"
        )
