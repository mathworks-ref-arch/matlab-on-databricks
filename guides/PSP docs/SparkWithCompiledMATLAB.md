
# Use Spark with Compiled MATLAB Code

This guide shows how to perform Spark operations with compiled MATLAB code. This is useful when you want to combine Spark and MATLAB, develop or experiment quickly, and scale performance-critical sections of your MATLAB code.

Requirements:

- MATLAB and MATLAB Compiler SDK, installed on the cluster where you compile your MATLAB code. Your administrator can install MATLAB Compiler SDK by including it in the Docker image they used to [Set Up MATLAB](../guides/admin/set-up-matlab-in-databricks.md).

- Simulink Compiler (Optional). Required to scale Simulink code.

- MATLAB Runtime, installed on the cluster where you want to run your MATLAB code. Your administrator can install MATLAB Runtime using the instructions in [Install MATLAB Runtime](./PSP%20docs/InstallMATLABRuntime.md).  Note: It is possible to run MATLAB and Spark on the same cluster, in which case you do not need MATLAB Runtime. However, to prevent MATLAB and Spark being busy at the same time, MathWorks recommends you run Spark on a different cluster, where you must install MATLAB Runtime.

- The MATLAB Interface for Databricks package. To install the package, follow the set up instructions in [Run MATLAB Interactively on Databricks](./run-matlab-interactively-on-databricks.md). (In particular, you must complete [Step 3: Install the MATLAB Interface for Databricks package](../run-matlab-interactively-on-databricks.md#step-3-install-matlab-interface-for-databricks-package)).

## Get Started

Copy this example to another location so you can experiment and write to it.

```matlabsession
copyfile(databricksRoot("examples", "DatabricksConnectWorkflow", "CompiledMATLAB"), "/home/<username>/CompiledMATLAB")
```

Change folder to `home/<username>/CompiledMATLAB`:

```matlab
cd("home/<username>/CompiledMATLAB")
```

This folder contains some trivial example MATLAB functions: `plusPi`, `doMath`, and
`addStringCol`.

Build a Python wheel:

```matlab
PSB = buildLibrary();
```

This builds a wheel file and a file `<package_name>_ZipArtifact.zip`. In this example the file is named `my.example_Artifact.zip`.

The function `addStringCol` expects a table with two columns, of types `integer` and `double`:

```matlab
function T_OUT = addStringCol(T_IN)
    % addStringCol

    T_OUT = T_IN;
    T_OUT.hello = string(T_IN.id) + "_hello_" + string(T_IN.did);
end
```

Use the following steps to build and run:

```matlabsession
>> spark = getDatabricksSession
spark = 
  PySparkSession with properties:

         ClusterId: "0304-180309-4l3lotrb"
    RuntimeVersion: "17.3"
        Serverless: "false"
>> R = spark.range(1e3)
R = 
  DataFrame with no properties.
>> DF = R.withColumn('did', matlab.pyspark.sql.functions.randn())
DF = 
  DataFrame with no properties.
>> DF.printSchema
root
 |-- id: long (nullable = false)
 |-- did: double (nullable = false)
 ```

To add the artifact to the current Spark session, and import the generated Python functions into the MATLAB environment, use the `addArtifact` method of the `PythonSparkBuilder` object.

```matlabsession
PSB.addArtifact(spark);
```

Now you can use MATLAB to call a MATLAB function, compiled into a Python library, in Databricks.

```matlabsession
>> OUT = DF.mapInPandas("addStringCol")
OUT = 
  DataFrame with no properties.

>> OUT.show(10, false)
+---+-------------------+----------------+
|id |did                |hello           |
+---+-------------------+----------------+
|0  |-0.7208682031019744|0_hello_-0.72087|
|1  |1.1940700163708902 |1_hello_1.1941  |
|2  |-2.727349160372737 |2_hello_-2.7273 |
|3  |1.270339150176543  |3_hello_1.2703  |
|4  |0.6858066765685452 |4_hello_0.68581 |
|5  |-0.8616134822263833|5_hello_-0.86161|
|6  |1.3108976149587273 |6_hello_1.3109  |
|7  |1.9688320133711728 |7_hello_1.9688  |
|8  |-0.5911113396114568|8_hello_-0.59111|
|9  |0.10349332957650109|9_hello_0.10349 |
+---+-------------------+----------------+
only showing top 10 rows

>> T = table(OUT);
```

You can now use and modify data in the table `T`.

To convert the table back into a Spark DataFrame, run:

```matlab
% Make some change to table
T.str_id = string(T.id);

% Convert it to a Spark DataFrame
>> DF_NEW = matlab.sparkutils.table2dataset(T, spark)
DF_NEW = 
  DataFrame with no properties.
>> DF_NEW.printSchema
root
 |-- id: long (nullable = true)
 |-- did: double (nullable = true)
 |-- hello: string (nullable = true)
 |-- str_id: string (nullable = true)

% Write it in Spark
DF_NEW.write.format('parquet').save('/Volumes/main/default/myvolume/Scratch/new_data')
```

Note: Some restrictions apply to this workflow. For example, it is not
possible to use `mapInPandas` with a table and additional arguments. For details, see [Limitations with Databricks Connect (Databricks)](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/limitations).

----
Copyright 2026 The MathWorks, Inc.
