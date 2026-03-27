# Use Spark in MATLAB

To perform Spark operations on your data in Databricks, you can use MATLAB to call Spark API functions using Databricks Connect. Spark scales and executes the functions across your Databricks cluster and returns the results in MATLAB. MathWorks recommends this approach for quick development, experimentation, and testing.

## Table of Contents

- [Requirements](#requirements)
- [Get Started](#get-started)
- [Use the MATLAB Spark API](#use-the-matlab-spark-api)
  - [Syntax in PySpark](#syntax-in-pyspark)
  - [Syntax in MATLAB](#syntax-in-matlab)
  - [Notes on Syntax](#notes-on-syntax)
- [Limitations](#limitations)

## Requirements

- Mathworks recommends you use this workflow with a cluster using Databricks Runtime [17.3 or later (Databricks Connect Release Notes)](https://docs.databricks.com/aws/en/release-notes/dbconnect/).

- You require the MATLAB Interface for Databricks package. To install the package, follow the set up instructions in [Run MATLAB Interactively on Databricks](./run-matlab-interactively-on-databricks.md). (In particular, you must complete [Step 3: Install the MATLAB Interface for Databricks package](../run-matlab-interactively-on-databricks.md#step-3-install-matlab-interface-for-databricks-package)).

## Get Started

This example shows how to create a Spark session and perform some Spark operations using the MATLAB Spark API.

Create a Spark session and use it to create a DataFrame with a range of numbers (1,100000), add a new column of random numbers, and show the first three rows (0,1,2).

```matlab
spark = getDatabricksSession()
R = spark.range(1e5);
DF = R.withColumn("newCol", matlab.pyspark.sql.functions.randn());
DF.show(3)
```

### Managing Spark Sessions

When you create a Databricks Connect session using `getDatabricksSession()`, the function uses the underlying Databricks Connect library to create the session. If you call this function a second time with the same arguments, the function returns the existing session.

Sometimes, a session might become `stale`, and unusable. To resolve this, clear any existing objects containing a session, for example by using `clear spark`, and then create a new session. You will lose any server-side content such as DataFrames.

## Use the MATLAB Spark API

This section shows how to connect to Spark from MATLAB, and describes similarities with PySpark. To see a complete list of the operations you can perform using Spark in MATLAB, see the [MATLAB Spark API Reference](./SparkApiRef.md).

### Note on converting DataFrames to tables

When you make Spark calls from MATLAB, the Spark dataset object returned to
MATLAB is effectively a "handle" to the data and the data still
resides on the Spark cluster.

The object only becomes a value in the MATLAB space and uses a significant amount of memory when you convert the object to a MATLAB datatype. Therefore, to minimize the use of your MATLAB memory and data transfer bandwidth between the cluster and MATLAB, perform any Spark filtering or data reduction
operations using the Spark APIs on the dataset object before you convert it to a MATLAB datatype such as tables.

Spark does not preserve the ordering of a table. If order is important, sort the resulting DataFrame manually using  Spark functions `orderBy` or `sort`.

### Syntax in PySpark

When working in Python using PySpark, you use the following syntax.

To load a DataFrame:

```python
df = spark.sql("SELECT * FROM main.default.outages")
df.printSchema()
# root
#  |-- Region: string (nullable = true)
#  |-- OutageTime: timestamp (nullable = true)
#  |-- Loss: double (nullable = true)
#  |-- Customers: double (nullable = true)
#  |-- RestorationTime: timestamp (nullable = true)
#  |-- Cause: string (nullable = true)

print(f'Rows: {df.count()}')
# Rows: 1468
```

To pick a column:

```python
c1 = df['Region']
# Column<'Region'>

# Alternatively
c1_ = df.Region
```

To pick a few columns of a DataFrame:

```python
df2 = df[['Region', 'Loss']]
df2.printSchema()
# root
#  |-- Region: string (nullable = true)
#  |-- Loss: double (nullable = true) 
```

To Filter a DataFrame according to columns:

```python
filter_column = df['Cause'].isin("winter storm", "attack")
# Column<'(Cause IN (winter storm, attack))'>

# Alternatively
filter_column_ = df.Cause.isin("winter storm", "attack")
# Column<'(Cause IN (winter storm, attack))'>

filtered_df = df[filter_column]
print(f'Rows: {filtered_df.count()}')
# Rows: 439

# Alternative, all in one:
filtered_df_ = df[df['Cause'].isin("winter storm", "attack")]
print(f'Rows: {filtered_df_.count()}')
# Rows: 439
```

### Syntax in MATLAB

In MATLAB, you use syntax that is similar to the dot-notation variant. A hidden `bracket` function allows you to use the Python bracket (`[]`). You do not need to call this function directly, but it will explain some of the
code better in the following examples.

To load a DataFrame, you use the same syntax as in PySpark.

```matlabsession
>> df = spark.sql("SELECT * FROM main.default.outages");
>> df.printSchema()

df = 
  DataFrame with no properties.
root
 |-- Region: string (nullable = true)
 |-- OutageTime: timestamp (nullable = true)
 |-- Loss: double (nullable = true)
 |-- Customers: double (nullable = true)
 |-- RestorationTime: timestamp (nullable = true)
 |-- Cause: string (nullable = true)


>> df.count()
ans =
  int64
   1468
```

To pick a column:

```matlabsession
>> c1 = df.Region
c1 = 
  Column with properties:

    Label: "Column<'Region'>"
    
% Alternatively
>> c1_ = df.bracket("Region")
c1_ = 
  Column with properties:

    Label: "Column<'Region'>"
```

To pick a few columns of a DataFrame:

```matlabsession
>> df2 = df.(["Region", "Loss"])
df2 = 
  DataFrame with no properties.
>> df2.printSchema()
root
 |-- Region: string (nullable = true)
 |-- Loss: double (nullable = true)

% Alternative 1
>> df2_1 = df.({'Region', 'Loss'})
df2_1 = 
  DataFrame with no properties.
>> df2_1.printSchema()
root
 |-- Region: string (nullable = true)
 |-- Loss: double (nullable = true)

% Alternative 2
>> df2_2 = df.bracket({'Region', 'Loss'})
df2_2 = 
  DataFrame with no properties.
>> df2_2.printSchema
root
 |-- Region: string (nullable = true)
 |-- Loss: double (nullable = true)
```

To filter a DataFrame according to columns:

```matlabsession
>> filter_column = df.Cause.isin("winter storm", "attack")
filter_column = 
  Column with properties:

    Label: "Column<'in(Cause, winter storm, attack)'>"
    
% Alternatively
>> filter_column = df.bracket('Cause').isin("winter storm", "attack")
filter_column = 
  Column with properties:

    Label: "Column<'in(Cause, winter storm, attack)'>"

>> filtered_df = df.(filter_column)
filtered_df = 
  DataFrame with no properties.
>> filtered_df.count()
ans =
  int64
   439

% Alternative, all in one
>> filtered_df = df.(df.Cause.isin("winter storm", "attack"))
filtered_df = 
  DataFrame with no properties.
>> filtered_df.count()
ans =
  int64
   439
```

### Notes on Syntax

#### Column indexing

Column indexing in Apache Spark is zero-based. The MATLAB Spark API uses the same, although this is not typical of MATLAB. This makes MATLAB easier to use for users who are familiar with Spark in other languages.

In Python:

```python
df = spark.sql("SELECT * FROM main.default.outages")
df.printSchema()
# root
#  |-- Region: string (nullable = true)
#  |-- OutageTime: timestamp (nullable = true)
#  |-- Loss: double (nullable = true)
#  |-- Customers: double (nullable = true)
#  |-- RestorationTime: timestamp (nullable = true)
#  |-- Cause: string (nullable = true)

df[0]
# Column<'Region'>

df[2]
# Column<'Loss'>
```

In MATLAB:

```matlabsession
>> df = spark.sql("SELECT * FROM main.default.outages");
>> df.printSchema()

df = 
  DataFrame with no properties.
root
 |-- Region: string (nullable = true)
 |-- OutageTime: timestamp (nullable = true)
 |-- Loss: double (nullable = true)
 |-- Customers: double (nullable = true)
 |-- RestorationTime: timestamp (nullable = true)
 |-- Cause: string (nullable = true)

>> df.(0)
ans = 
  Column with properties:

    Label: "Column<'Region'>"

>> df.(2)
ans = 
  Column with properties:

    Label: "Column<'Loss'>"
```

You cannot use a numbered column with plain
dot-notation. For example, `df.0` fails, but `df.(0)` works.

#### Chaining Dots

Overloading `.` relies on the mixin class
`matlab.mixin.indexing.RedefinesDot`. The `Dataframe` class inherits from this
class. The `Dataframe` uses the arguments after the dot, and tries to apply them with the `bracket`
method, enabling a streamlined workflow.

In the previous example, you chained several operations:

```matlab
filter_col = df.Cause.isin("winter storm", "attack")
```

The first part, `df.Cause`, returns a `Column` object, so the second method
`issin()` operates on a `Column` rather than a `Dataframe` object.

You can see the operations like this:

```matlab
tmp_col = df.Cause
filter_col = tmp_col.isin("winter storm", "attack")
```

The second part, `isin`, calls a method on the resulting `Column` object. This operation relies on syntactic sugar to call a method or retrieve a field, if possible.

Another example is:

```matlabsession
>> df.Region.string
ans = 
    "Column<'Region'>"
```

Some combinations do not work.

As an alternative to the first example, you can either split up as in the example above, or you can explicitly use the `bracket` method.

```matlab
filter_col = df.bracket('Cause').isin("winter storm", "attack")
```

In this example, the first part, `df.bracket('Cause')` returns a column,
and the next operation is applied on that.

#### Non-named Columns

As you see in the example, an operation like `df.Region` is similar to Python's
`df['region']`. When you refer to a column that is not simply a name, use the dynamic field name. This is similar to how you can use a variable with a field name
to retrieve a field from a struct:

```matlab
myField = 'Age';
age = myStruct.(myField);
```

In this case, as with the filtered `Dataframe`, you must use a dynamic field name.

```matlab
filtered_df = df.(filter_column)
```

#### Unsupported Column Names

You can retrieve all column names, but you cannot retrieve all column names using the dot notation.

##### Other Fields or Methods

If there is a dataset with a name `col`, you cannot retrieve this using `df.col`,
because `col` is already a method, which takes precedence.

```matlabsession
>> df_ = spark.range(10);
>> df = df_.withColumn('col', df_.id).withColumn('columns', df_.id)
df = 
  DataFrame with no properties.
>> df.show(3)
+---+---+-------+
| id|col|columns|
+---+---+-------+
|  0|  0|      0|
|  1|  1|      1|
|  2|  2|      2|
+---+---+-------+
only showing top 3 rows
```

Different options can be evaluated:

```matlabsession
>> df.col
Error using matlab.pyspark.sql.dataframe.Dataframe/col (line 27)
Invalid argument list. Function requires 1 more input(s). 

>> df.('col')
Error using matlab.pyspark.sql.dataframe.Dataframe/col (line 27)
Invalid argument list. Function requires 1 more input(s). 

>> df.bracket('col')
ans = 
  Column with no properties.
```

In this example, only the last function works.

The case for `columns` is different. This operation does not error, as it does not need arguments. However, it will not return a column object, as you might expect.

```matlabsession
>> df.columns
ans = 
  1×3 string array
    "id"    "col"    "columns"
>> df.('columns')
ans = 
  1×3 string array
    "id"    "col"    "columns"
>> df.bracket('columns')
ans = 
  Column with no properties.
```

## Limitations

To see a list of limitations, see [Limitations of Databricks Connect (Databricks)](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/limitations).

 ---------------
Copyright 2026 The MathWorks, Inc.
