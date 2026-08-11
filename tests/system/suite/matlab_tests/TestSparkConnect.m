% Copyright 2026 The MathWorks, Inc.
classdef TestSparkConnect < matlab.unittest.TestCase
    % System tests for MATLAB Spark Connect on Databricks.

    methods (Test)

        function testGetDatabricksSessionReturnsSparkSession(testCase)
            % getDatabricksSession should return a valid PySparkSession
            spark = getDatabricksSession(verbose=false);
            testCase.assertNotEmpty(spark, ...
                "getDatabricksSession should return a session");
            testCase.assertClass(spark, 'databricks.PySparkSession');
        end

        function testSparkSqlRoundTrip(testCase)
            % Workflow: create data via SQL, read it back
            spark = getDatabricksSession(verbose=false);

            df = spark.sql("SELECT 1 AS id, 'hello' AS value");
            result = table(df);

            testCase.assertEqual(height(result), 1, ...
                "Query should return exactly one row");
            testCase.assertEqual(result.id, int32(1));
            testCase.assertEqual(string(result.value), "hello");
        end

        function testSparkRangeAndCollect(testCase)
            % Workflow: Validate DataFrame creation and row count
            spark = getDatabricksSession(verbose=false);

            df = spark.range(10);
            count = df.count();

            testCase.assertEqual(count, int64(10), ...
                "spark.range(10) should produce 10 rows");
        end

        function testSparkConnectModeEnabled(testCase)
            % SPARK_CONNECT_MODE_ENABLED must be set after setup
            val = getenv("SPARK_CONNECT_MODE_ENABLED");
            testCase.assertEqual(val, '1', ...
                "SPARK_CONNECT_MODE_ENABLED should be '1'");
        end

    end
end
