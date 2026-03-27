# Scale Compiled MATLAB for Production Workflows

This guide shows how to scale compiled MATLAB&reg; and Simulink&reg; code across your Databricks cluster. MathWorks recommends this workflow if you want to scale production code for frequent or time-consuming computations, or if you want to run MATLAB code in Databricks notebooks, across multiple nodes.

You use the MATLAB Compiler SDK&trade; to compile your MATLAB code, then you run this code in parallel across the Databricks cluster using MATLAB Runtime and Spark.

Note: This workflow is useful for scaling compiled MATLAB code across multiple nodes. If you only want to scale MATLAB code on one node, you can use also use [Parallel Computing Toolbox (MathWorks)](https://www.mathworks.com/products/parallel-computing.html). Some of your workflows might be more suitable for Spark, and others for Parallel Computing Toolbox. However, MathWorks does not recommend you use both Parallel Computing Toolbox and Spark together, as this can lead to oversubscription of your compute resources.

## Table of Contents

- [Requirements](#requirements)
- [Get Started](#get-started)
- [Build Python Wheel](#build-wheel)
  - [Generate Schema](#generate-schema)
  - [Compile Code](#compile-code)
- [Copy Wheel File to Shared Storage](#copy-wheel-to-shared-storage)
- [Import Example Notebooks to Databricks Workspace](#import-example-notebooks-to-databricks-workspace)
- [Use User Defined Functions](#use-user-defined-functions)

## Requirements

- MATLAB and MATLAB Compiler SDK, installed on the cluster where you will compile your MATLAB code. Your administrator can install MATLAB Compiler SDK by including it in the Docker image they used to [Set Up MATLAB on Databricks](../guides/admin/set-up-matlab-on-databricks.md).

- MATLAB Runtime, installed on the cluster where you scale your code. Your administrator can install MATLAB Runtime using the instructions in [Install MATLAB Runtime](./PSP%20docs/InstallMATLABRuntime.md). The version of MATLAB Runtime must match the version of MATLAB Compiler SDK you use to compile your code.

- Simulink Compiler (Optional). Required to scale Simulink code.

- The MATLAB Interface for Databricks package. To install the package, follow the set up instructions in [Run MATLAB Interactively on Databricks](./run-matlab-interactively-on-databricks.md). (In particular, you must complete [Step 3: Install the MATLAB Interface for Databricks package](../run-matlab-interactively-on-databricks.md#step-3-install-matlab-interface-for-databricks-package)).

## Get Started

In this example you begin with a MATLAB function and use Compiler SDK to compile it as Python wheel package. Then you run this code using Spark on a cluster that has MATLAB Runtime installed. The wheel contains variants of your MATLAB function that you can apply to a Spark DataFrame, for example `<function-name>_mapInPandas` and `<function-name>_applyInPandas`.  

MathWorks recommends you use MATLAB functions that take a table as an input argument and return a table, as these can be converted to and from Spark DataFrames. If your compiled function uses arguments that are not tables, the compiler process also generates user-defined functions (UDFs) you can use with Spark and SQL. You can use these to operate on columns of a table or DataFrame, instead of the whole table or DataFrame.

## Build Wheel

### Generate Schema

In this section, you generate a Spark schema. The schema describes the data types your function uses. You call the `generateFunctionSchema` function with the name of your MATLAB function, as well as any input arguments for your function.

In this section you use the function `addStringCol`, which is one of several example functions. Run the following command in MATLAB to copy the examples to a new folder.

```matlabsession
copyfile(getSparkApiRoot('examples'), '/home/<username>/examples')
```

Then navigate to this folder.

```matlabsession
cd('/home/<username>/examples/compiler')
```

First you generate some sample input. You create a table with two columns. One contains integers, and the other contains doubles.

```matlab

id = int64(1:10)';
did = (1:10)';
DF_T = table(id, did);

```

You use the example function `addStringCol` to take the table as input and insert the `_hello_` string.

Note: The function takes a table as an argument and returns a table. In Databricks, a method operates on a DataFrame and produces a DataFrame. When you compile your code using the workflow in this guide, the build process generates code to convert a DataFrame to a MATLAB table, pass that MATLAB table to your function, and then convert the resulting table back to a DataFrame.

```matlab
function T_OUT = addStringCol(T_IN)
    T_OUT = T_IN;
    T_OUT.hello = string(T_IN.id) + "_hello_" + string(T_IN.did);
end

```

Using the function and sample input, you generate a function schema that you use with Spark. Note: Generating the schema executes the code in the function.

```matlab
generateFunctionSchema("addStringCol", {DF_T})
```

The schema is generated as a new file named `addStringCol.schema` file in your current directory.

Spark does not preserve the ordering of a table. If order is important, sort the DataFrame that results from a Spark operation manually using Spark functions `orderBy` or `sort`. For example, if you provide a table containing a time vector with corresponding values as input to a Simulink model, these must be sorted. Simulink only accepts a monotonically increasing time vector as input.

This is an example of how you can sort data you use in the MATLAB function:

```matlab
    % Sort the time. Data is a table and t is the column with the timestamps. 
    data = sortrows(data, 't');

    % Reset to zero starting time
    data.t = data.t - data.t(1);
```

### Compile Code

Create an options object for MATLAB Compiler, then compile the code:

```matlab
% First create the opts object
opts = compiler.build.PythonPackageOptions(...
    ["plusPi.m", "doMath.m", "addStringCol.m"], ... % the files to compile
    "OutputDir", "_build", ...                 % the output directory
    "PackageName", "my.example");                     % the package name

% Then compile the code (note the `spark` in the function name)
PSB = compiler.build.spark.pythonPackage(opts);
```

This code creates a wheel and puts it in the `dist` subfolder of your output directory.

```bash
$ dir _build/dist/
my.example-25.2.0-py3-none-any.whl
```

## Copy Wheel to Shared Storage

To run the wheel file, copy it to a volume or workspace path (specified by the argument `destinationFolder`) where it is accessible from different clusters.

```matlab
copyfile(PSB.getWheelFile(), <destinationFolder>)
```

## Import Example Notebooks to Databricks Workspace

To call your compiled function, you must install your wheel file in your Notebook. To do this, you use example notebooks that were created when you built your wheel file.

Import the example notebooks:

```matlab
PSB.uploadExampleNotebooks("/Users/jane@example.com/myExamples/")
```

This imports one example notebook for each compiled MATLAB function into your destination folder.

Open the notebook you want to use, and uncomment and modify the line containing the `%pip install` command. Replace the path with the full path to your wheel file in your destination folder.

Open the notebook and run all the cells. The cells:

- Import available functions. For this example the functions are `mapInPandas` and `applyInPandas`. When your MATLAB function does not take table inputs, the compile process also creates user defined functions that operate on a scalar and that you can apply to a single column. See the next section for details.
- Create some example data, with the correct data types.
- Run examples that use the functions in a Spark context.

You can also replace the sample data with your own. You can run the notebook on a cluster with MATLAB Runtime installed. (To do a simple test, you can also run the notebook on the same cluster running your MATLAB desktop. Only use this method for testing with small amounts of data.). After customizing and testing your notebook, you can execute it as a Databricks job.  

## Use User Defined Functions

To perform operations on one or more columns in a SQL table or DataFrame, instead of the whole table or DataFrame, you can use user defined functions (UDFs). These functions operate on a scalar value.

Building your wheel generates some helper functions that register your MATLAB function as UDFs. These helper functions have names of the form (`<fcn_name>_reg_udf*`).

For example, this is the helper function for the `plusPi` function in the examples folder:

```python
def plusPi_reg_udf(spark, name='plusPi_udf'):
    """ Register the function plusPi as a UDF
    A second argument can be used to specify the name to be used."""
    spark.udf.register(name, plusPi, DoubleType())
```

The registered UDF has a name of the form
(`<fcn_name>_udf`). You can choose a different name using a second argument.

For example:

```python
# Register as UDF
plusPi_reg_udf(spark)

# Use the UDF on the temporary table
UDF1 = spark.sql('SELECT X, plusPi_udf(X) FROM temptest_plusPi')
UDF1.show(5, False)
```

There are also helper functions that register UDFs you can use with DataFrames and Pandas series:

For DataFrames:

```python
def plusPi_reg_udf_DataFrame():
    """ Returns a UDF function for use with DataFrames."""
    return udf(plusPi, DoubleType())
```

```python
# Register as UDF for DataFrames
plusPi_udf_df = plusPi_reg_udf_DataFrame()

# Use in a DataFrame select statement
UDF2 = DF.select('X', plusPi_udf_df('X'))
UDF2.show(5, False)
```

For Pandas series:

```python
def plusPi_reg_udf_series():
    """ Register the function plusPi_series as a pandas_udf function.
    It may be used as follows:
      plusPi_pandas_udf = regUDFSeries()
      DF.select(plusPi_pandas_udf(col('X')))
    """
    return pandas_udf(plusPi_series, DoubleType())
```

```python
# Register as UDF for Pandas series
plusPi_udf_series = plusPi_reg_udf_series()

# Use in a DataFrame select statement
UDF3 = DF.select('X', plusPi_udf_series(col('X')))
UDF3.show(5, False)
```

----
Copyright 2026 The MathWorks, Inc.
