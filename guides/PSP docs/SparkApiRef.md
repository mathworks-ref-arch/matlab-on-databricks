# MATLAB Interface *for Apache Spark* (matlab.pyspark) - API Reference

This document includes API reference information for the following namespaces or functions:

* [matlab.pyspark.sql.column](#matlabpysparksqlcolumn)
* [matlab.pyspark.sql.dataframe](#matlabpysparksqldataframe)
* [matlab.pyspark.sql.functions](#matlabpysparksqlfunctions)
* [matlab.pyspark.sql.session](#matlabpysparksqlsession)
* [matlab.sparkutils.table2dataset](#matlabsparkutilstable2dataset)

Do not use classes, methods and functions that include the terms `private` or `internal` in their namespace.

## Index

* MATLAB Interface *for Apache Spark* (matlab.pyspark)
  * [matlab.pyspark.sql.column](#matlabpysparksqlcolumn)
    * [matlab.pyspark.sql.column.Column](#matlabpysparksqlcolumncolumn)
      * [matlab.pyspark.sql.column.Column.Column](#matlabpysparksqlcolumncolumncolumn)
      * [matlab.pyspark.sql.column.Column.alias](#matlabpysparksqlcolumncolumnalias)
      * [matlab.pyspark.sql.column.Column.and](#matlabpysparksqlcolumncolumnand)
      * [matlab.pyspark.sql.column.Column.asc](#matlabpysparksqlcolumncolumnasc)
      * [matlab.pyspark.sql.column.Column.asc_nulls_first](#matlabpysparksqlcolumncolumnasc_nulls_first)
      * [matlab.pyspark.sql.column.Column.asc_nulls_last](#matlabpysparksqlcolumncolumnasc_nulls_last)
      * [matlab.pyspark.sql.column.Column.astype](#matlabpysparksqlcolumncolumnastype)
      * [matlab.pyspark.sql.column.Column.between](#matlabpysparksqlcolumncolumnbetween)
      * [matlab.pyspark.sql.column.Column.bitwiseAND](#matlabpysparksqlcolumncolumnbitwiseand)
      * [matlab.pyspark.sql.column.Column.bitwiseOR](#matlabpysparksqlcolumncolumnbitwiseor)
      * [matlab.pyspark.sql.column.Column.bitwiseXOR](#matlabpysparksqlcolumncolumnbitwisexor)
      * [matlab.pyspark.sql.column.Column.cast](#matlabpysparksqlcolumncolumncast)
      * [matlab.pyspark.sql.column.Column.contains](#matlabpysparksqlcolumncolumncontains)
      * [matlab.pyspark.sql.column.Column.desc](#matlabpysparksqlcolumncolumndesc)
      * [matlab.pyspark.sql.column.Column.desc_nulls_first](#matlabpysparksqlcolumncolumndesc_nulls_first)
      * [matlab.pyspark.sql.column.Column.desc_nulls_last](#matlabpysparksqlcolumncolumndesc_nulls_last)
      * [matlab.pyspark.sql.column.Column.divide](#matlabpysparksqlcolumncolumndivide)
      * [matlab.pyspark.sql.column.Column.endswith](#matlabpysparksqlcolumncolumnendswith)
      * [matlab.pyspark.sql.column.Column.eq](#matlabpysparksqlcolumncolumneq)
      * [matlab.pyspark.sql.column.Column.ge](#matlabpysparksqlcolumncolumnge)
      * [matlab.pyspark.sql.column.Column.gt](#matlabpysparksqlcolumncolumngt)
      * [matlab.pyspark.sql.column.Column.ilike](#matlabpysparksqlcolumncolumnilike)
      * [matlab.pyspark.sql.column.Column.isNaN](#matlabpysparksqlcolumncolumnisnan)
      * [matlab.pyspark.sql.column.Column.isNotNull](#matlabpysparksqlcolumncolumnisnotnull)
      * [matlab.pyspark.sql.column.Column.isNull](#matlabpysparksqlcolumncolumnisnull)
      * [matlab.pyspark.sql.column.Column.isin](#matlabpysparksqlcolumncolumnisin)
      * [matlab.pyspark.sql.column.Column.le](#matlabpysparksqlcolumncolumnle)
      * [matlab.pyspark.sql.column.Column.like](#matlabpysparksqlcolumncolumnlike)
      * [matlab.pyspark.sql.column.Column.lt](#matlabpysparksqlcolumncolumnlt)
      * [matlab.pyspark.sql.column.Column.minus](#matlabpysparksqlcolumncolumnminus)
      * [matlab.pyspark.sql.column.Column.mrdivide](#matlabpysparksqlcolumncolumnmrdivide)
      * [matlab.pyspark.sql.column.Column.mtimes](#matlabpysparksqlcolumncolumnmtimes)
      * [matlab.pyspark.sql.column.Column.multiply](#matlabpysparksqlcolumncolumnmultiply)
      * [matlab.pyspark.sql.column.Column.ne](#matlabpysparksqlcolumncolumnne)
      * [matlab.pyspark.sql.column.Column.not](#matlabpysparksqlcolumncolumnnot)
      * [matlab.pyspark.sql.column.Column.or](#matlabpysparksqlcolumncolumnor)
      * [matlab.pyspark.sql.column.Column.otherwise_](#matlabpysparksqlcolumncolumnotherwise_)
      * [matlab.pyspark.sql.column.Column.over](#matlabpysparksqlcolumncolumnover)
      * [matlab.pyspark.sql.column.Column.plus](#matlabpysparksqlcolumncolumnplus)
      * [matlab.pyspark.sql.column.Column.rdivide](#matlabpysparksqlcolumncolumnrdivide)
      * [matlab.pyspark.sql.column.Column.rem](#matlabpysparksqlcolumncolumnrem)
      * [matlab.pyspark.sql.column.Column.rlike](#matlabpysparksqlcolumncolumnrlike)
      * [matlab.pyspark.sql.column.Column.startswith](#matlabpysparksqlcolumncolumnstartswith)
      * [matlab.pyspark.sql.column.Column.string](#matlabpysparksqlcolumncolumnstring)
      * [matlab.pyspark.sql.column.Column.times](#matlabpysparksqlcolumncolumntimes)
      * [matlab.pyspark.sql.column.Column.toPy](#matlabpysparksqlcolumncolumntopy)
      * [matlab.pyspark.sql.column.Column.uminus](#matlabpysparksqlcolumncolumnuminus)
      * [matlab.pyspark.sql.column.Column.when](#matlabpysparksqlcolumncolumnwhen)
  * [matlab.pyspark.sql.dataframe](#matlabpysparksqldataframe)
    * [matlab.pyspark.sql.dataframe.DataFrameNaFunctions](#matlabpysparksqldataframedataframenafunctions)
      * [matlab.pyspark.sql.dataframe.DataFrameNaFunctions.DataFrameNaFunctions](#matlabpysparksqldataframedataframenafunctionsdataframenafunctions)
      * [matlab.pyspark.sql.dataframe.DataFrameNaFunctions.drop](#matlabpysparksqldataframedataframenafunctionsdrop)
      * [matlab.pyspark.sql.dataframe.DataFrameNaFunctions.fill](#matlabpysparksqldataframedataframenafunctionsfill)
      * [matlab.pyspark.sql.dataframe.DataFrameNaFunctions.toPy](#matlabpysparksqldataframedataframenafunctionstopy)
    * [matlab.pyspark.sql.dataframe.Dataframe](#matlabpysparksqldataframedataframe)
      * [matlab.pyspark.sql.dataframe.Dataframe.Dataframe](#matlabpysparksqldataframedataframedataframe)
      * [matlab.pyspark.sql.dataframe.Dataframe.agg](#matlabpysparksqldataframedataframeagg)
      * [matlab.pyspark.sql.dataframe.Dataframe.alias](#matlabpysparksqldataframedataframealias)
      * [matlab.pyspark.sql.dataframe.Dataframe.bracket](#matlabpysparksqldataframedataframebracket)
      * [matlab.pyspark.sql.dataframe.Dataframe.cache](#matlabpysparksqldataframedataframecache)
      * [matlab.pyspark.sql.dataframe.Dataframe.col](#matlabpysparksqldataframedataframecol)
      * [matlab.pyspark.sql.dataframe.Dataframe.columns](#matlabpysparksqldataframedataframecolumns)
      * [matlab.pyspark.sql.dataframe.Dataframe.count](#matlabpysparksqldataframedataframecount)
      * [matlab.pyspark.sql.dataframe.Dataframe.createOrReplaceTempView](#matlabpysparksqldataframedataframecreateorreplacetempview)
      * [matlab.pyspark.sql.dataframe.Dataframe.describe](#matlabpysparksqldataframedataframedescribe)
      * [matlab.pyspark.sql.dataframe.Dataframe.distinct](#matlabpysparksqldataframedataframedistinct)
      * [matlab.pyspark.sql.dataframe.Dataframe.dotAssign](#matlabpysparksqldataframedataframedotassign)
      * [matlab.pyspark.sql.dataframe.Dataframe.dotListLength](#matlabpysparksqldataframedataframedotlistlength)
      * [matlab.pyspark.sql.dataframe.Dataframe.dotReference](#matlabpysparksqldataframedataframedotreference)
      * [matlab.pyspark.sql.dataframe.Dataframe.drop](#matlabpysparksqldataframedataframedrop)
      * [matlab.pyspark.sql.dataframe.Dataframe.dropDuplicates](#matlabpysparksqldataframedataframedropduplicates)
      * [matlab.pyspark.sql.dataframe.Dataframe.dropna](#matlabpysparksqldataframedataframedropna)
      * [matlab.pyspark.sql.dataframe.Dataframe.filter](#matlabpysparksqldataframedataframefilter)
      * [matlab.pyspark.sql.dataframe.Dataframe.groupBy](#matlabpysparksqldataframedataframegroupby)
      * [matlab.pyspark.sql.dataframe.Dataframe.isEmpty](#matlabpysparksqldataframedataframeisempty)
      * [matlab.pyspark.sql.dataframe.Dataframe.join](#matlabpysparksqldataframedataframejoin)
      * [matlab.pyspark.sql.dataframe.Dataframe.limit](#matlabpysparksqldataframedataframelimit)
      * [matlab.pyspark.sql.dataframe.Dataframe.mapInPandas](#matlabpysparksqldataframedataframemapinpandas)
      * [matlab.pyspark.sql.dataframe.Dataframe.na](#matlabpysparksqldataframedataframena)
      * [matlab.pyspark.sql.dataframe.Dataframe.orderBy](#matlabpysparksqldataframedataframeorderby)
      * [matlab.pyspark.sql.dataframe.Dataframe.printSchema](#matlabpysparksqldataframedataframeprintschema)
      * [matlab.pyspark.sql.dataframe.Dataframe.repartition](#matlabpysparksqldataframedataframerepartition)
      * [matlab.pyspark.sql.dataframe.Dataframe.repartitionByRange](#matlabpysparksqldataframedataframerepartitionbyrange)
      * [matlab.pyspark.sql.dataframe.Dataframe.sample](#matlabpysparksqldataframedataframesample)
      * [matlab.pyspark.sql.dataframe.Dataframe.schema](#matlabpysparksqldataframedataframeschema)
      * [matlab.pyspark.sql.dataframe.Dataframe.select](#matlabpysparksqldataframedataframeselect)
      * [matlab.pyspark.sql.dataframe.Dataframe.show](#matlabpysparksqldataframedataframeshow)
      * [matlab.pyspark.sql.dataframe.Dataframe.sort](#matlabpysparksqldataframedataframesort)
      * [matlab.pyspark.sql.dataframe.Dataframe.summary](#matlabpysparksqldataframedataframesummary)
      * [matlab.pyspark.sql.dataframe.Dataframe.table](#matlabpysparksqldataframedataframetable)
      * [matlab.pyspark.sql.dataframe.Dataframe.table_R2023b](#matlabpysparksqldataframedataframetable_r2023b)
      * [matlab.pyspark.sql.dataframe.Dataframe.toDF](#matlabpysparksqldataframedataframetodf)
      * [matlab.pyspark.sql.dataframe.Dataframe.toPandas](#matlabpysparksqldataframedataframetopandas)
      * [matlab.pyspark.sql.dataframe.Dataframe.toPy](#matlabpysparksqldataframedataframetopy)
      * [matlab.pyspark.sql.dataframe.Dataframe.transform](#matlabpysparksqldataframedataframetransform)
      * [matlab.pyspark.sql.dataframe.Dataframe.where](#matlabpysparksqldataframedataframewhere)
      * [matlab.pyspark.sql.dataframe.Dataframe.withColumn](#matlabpysparksqldataframedataframewithcolumn)
      * [matlab.pyspark.sql.dataframe.Dataframe.withColumnRenamed](#matlabpysparksqldataframedataframewithcolumnrenamed)
      * [matlab.pyspark.sql.dataframe.Dataframe.write](#matlabpysparksqldataframedataframewrite)
  * [matlab.pyspark.sql.functions](#matlabpysparksqlfunctions)
    * [matlab.pyspark.sql.functions.abs](#matlabpysparksqlfunctionsabs)
    * [matlab.pyspark.sql.functions.acos](#matlabpysparksqlfunctionsacos)
    * [matlab.pyspark.sql.functions.add_months](#matlabpysparksqlfunctionsadd_months)
    * [matlab.pyspark.sql.functions.array](#matlabpysparksqlfunctionsarray)
    * [matlab.pyspark.sql.functions.asc](#matlabpysparksqlfunctionsasc)
    * [matlab.pyspark.sql.functions.asin](#matlabpysparksqlfunctionsasin)
    * [matlab.pyspark.sql.functions.atan](#matlabpysparksqlfunctionsatan)
    * [matlab.pyspark.sql.functions.ceil](#matlabpysparksqlfunctionsceil)
    * [matlab.pyspark.sql.functions.col](#matlabpysparksqlfunctionscol)
    * [matlab.pyspark.sql.functions.column](#matlabpysparksqlfunctionscolumn)
    * [matlab.pyspark.sql.functions.concat](#matlabpysparksqlfunctionsconcat)
    * [matlab.pyspark.sql.functions.current_date](#matlabpysparksqlfunctionscurrent_date)
    * [matlab.pyspark.sql.functions.current_timestamp](#matlabpysparksqlfunctionscurrent_timestamp)
    * [matlab.pyspark.sql.functions.date_add](#matlabpysparksqlfunctionsdate_add)
    * [matlab.pyspark.sql.functions.date_format](#matlabpysparksqlfunctionsdate_format)
    * [matlab.pyspark.sql.functions.date_sub](#matlabpysparksqlfunctionsdate_sub)
    * [matlab.pyspark.sql.functions.dayofmonth](#matlabpysparksqlfunctionsdayofmonth)
    * [matlab.pyspark.sql.functions.dayofweek](#matlabpysparksqlfunctionsdayofweek)
    * [matlab.pyspark.sql.functions.dayofyear](#matlabpysparksqlfunctionsdayofyear)
    * [matlab.pyspark.sql.functions.desc](#matlabpysparksqlfunctionsdesc)
    * [matlab.pyspark.sql.functions.floor](#matlabpysparksqlfunctionsfloor)
    * [matlab.pyspark.sql.functions.from_unixtime](#matlabpysparksqlfunctionsfrom_unixtime)
    * [matlab.pyspark.sql.functions.from_utc_timestamp](#matlabpysparksqlfunctionsfrom_utc_timestamp)
    * [matlab.pyspark.sql.functions.hour](#matlabpysparksqlfunctionshour)
    * [matlab.pyspark.sql.functions.lit](#matlabpysparksqlfunctionslit)
    * [matlab.pyspark.sql.functions.make_date](#matlabpysparksqlfunctionsmake_date)
    * [matlab.pyspark.sql.functions.make_timestamp](#matlabpysparksqlfunctionsmake_timestamp)
    * [matlab.pyspark.sql.functions.make_timestamp_ltz](#matlabpysparksqlfunctionsmake_timestamp_ltz)
    * [matlab.pyspark.sql.functions.make_timestamp_ntz](#matlabpysparksqlfunctionsmake_timestamp_ntz)
    * [matlab.pyspark.sql.functions.max](#matlabpysparksqlfunctionsmax)
    * [matlab.pyspark.sql.functions.mean](#matlabpysparksqlfunctionsmean)
    * [matlab.pyspark.sql.functions.min](#matlabpysparksqlfunctionsmin)
    * [matlab.pyspark.sql.functions.minute](#matlabpysparksqlfunctionsminute)
    * [matlab.pyspark.sql.functions.monotonically_increasing_id](#matlabpysparksqlfunctionsmonotonically_increasing_id)
    * [matlab.pyspark.sql.functions.month](#matlabpysparksqlfunctionsmonth)
    * [matlab.pyspark.sql.functions.percent_rank](#matlabpysparksqlfunctionspercent_rank)
    * [matlab.pyspark.sql.functions.pow](#matlabpysparksqlfunctionspow)
    * [matlab.pyspark.sql.functions.product](#matlabpysparksqlfunctionsproduct)
    * [matlab.pyspark.sql.functions.rand](#matlabpysparksqlfunctionsrand)
    * [matlab.pyspark.sql.functions.randn](#matlabpysparksqlfunctionsrandn)
    * [matlab.pyspark.sql.functions.rank](#matlabpysparksqlfunctionsrank)
    * [matlab.pyspark.sql.functions.round](#matlabpysparksqlfunctionsround)
    * [matlab.pyspark.sql.functions.row_number](#matlabpysparksqlfunctionsrow_number)
    * [matlab.pyspark.sql.functions.second](#matlabpysparksqlfunctionssecond)
    * [matlab.pyspark.sql.functions.spark_partition_id](#matlabpysparksqlfunctionsspark_partition_id)
    * [matlab.pyspark.sql.functions.sum](#matlabpysparksqlfunctionssum)
    * [matlab.pyspark.sql.functions.to_date](#matlabpysparksqlfunctionsto_date)
    * [matlab.pyspark.sql.functions.to_timestamp](#matlabpysparksqlfunctionsto_timestamp)
    * [matlab.pyspark.sql.functions.transform](#matlabpysparksqlfunctionstransform)
    * [matlab.pyspark.sql.functions.unix_timestamp](#matlabpysparksqlfunctionsunix_timestamp)
    * [matlab.pyspark.sql.functions.weekofyear](#matlabpysparksqlfunctionsweekofyear)
    * [matlab.pyspark.sql.functions.when](#matlabpysparksqlfunctionswhen)
    * [matlab.pyspark.sql.functions.window](#matlabpysparksqlfunctionswindow)
    * [matlab.pyspark.sql.functions.year](#matlabpysparksqlfunctionsyear)
  * [matlab.pyspark.sql.session](#matlabpysparksqlsession)
    * [matlab.pyspark.sql.session.SparkSession](#matlabpysparksqlsessionsparksession)
      * [matlab.pyspark.sql.session.SparkSession.SparkSession](#matlabpysparksqlsessionsparksessionsparksession)
      * [matlab.pyspark.sql.session.SparkSession.addArtifact](#matlabpysparksqlsessionsparksessionaddartifact)
      * [matlab.pyspark.sql.session.SparkSession.catalog](#matlabpysparksqlsessionsparksessioncatalog)
      * [matlab.pyspark.sql.session.SparkSession.createDataFrame](#matlabpysparksqlsessionsparksessioncreatedataframe)
      * [matlab.pyspark.sql.session.SparkSession.delete](#matlabpysparksqlsessionsparksessiondelete)
      * [matlab.pyspark.sql.session.SparkSession.range](#matlabpysparksqlsessionsparksessionrange)
      * [matlab.pyspark.sql.session.SparkSession.read](#matlabpysparksqlsessionsparksessionread)
      * [matlab.pyspark.sql.session.SparkSession.session_id](#matlabpysparksqlsessionsparksessionsession_id)
      * [matlab.pyspark.sql.session.SparkSession.sql](#matlabpysparksqlsessionsparksessionsql)
      * [matlab.pyspark.sql.session.SparkSession.stop](#matlabpysparksqlsessionsparksessionstop)
      * [matlab.pyspark.sql.session.SparkSession.table](#matlabpysparksqlsessionsparksessiontable)
      * [matlab.pyspark.sql.session.SparkSession.toPy](#matlabpysparksqlsessionsparksessiontopy)
      * [matlab.pyspark.sql.session.SparkSession.version](#matlabpysparksqlsessionsparksessionversion)
  * [matlab.sparkutils](#matlabsparkutils)
    * [matlab.sparkutils.table2dataset](#matlabsparkutilstable2dataset)

## Help

### matlab.pyspark.sql.column

### matlab.pyspark.sql.column.Column

Superclass: matlab.pyspark.internal.PyWrapper

```text
Column - A pyspark column
```

#### matlab.pyspark.sql.column.Column.Column

```text
Column - A pyspark column
```

#### matlab.pyspark.sql.column.Column.alias

```text
alias Returns the column aliased with a new name or names
 
  Example:
    R = spark.range(10);
    R.select(R.('id').alias('new_Id')).show(3)
```

#### matlab.pyspark.sql.column.Column.and

```text
and - Find logical AND
    This MATLAB function performs a logical AND of inputs A and B and
    returns an array or a table containing elements set to either logical 1
    (true) or logical 0 (false).

    Syntax
      A & B
      and(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/LocateNonzeroValuesExample')
      openExample('matlab/TruthTableForLogicalANDExample')
      openExample('matlab/LogicalANDOfTablesExample')

    See also any, all, bitand, xor, or, not

    Introduced in MATLAB before R2006a
    Documentation for and
       doc and
```

#### matlab.pyspark.sql.column.Column.asc

```text
asc - Ascending sort of column
```

#### matlab.pyspark.sql.column.Column.asc_nulls_first

```text
asc_nulls_first - Ascending sort of column
```

#### matlab.pyspark.sql.column.Column.asc_nulls_last

```text
asc_nulls_last - Ascending sort of column
```

#### matlab.pyspark.sql.column.Column.astype

```text
astype - Sames as cast
```

#### matlab.pyspark.sql.column.Column.between

```text
between
```

#### matlab.pyspark.sql.column.Column.bitwiseAND

```text
bitwiseAND
```

#### matlab.pyspark.sql.column.Column.bitwiseOR

```text
bitwiseOR
```

#### matlab.pyspark.sql.column.Column.bitwiseXOR

```text
bitwiseXOR
```

#### matlab.pyspark.sql.column.Column.cast

```text
COL Cast the type of a column
 
  Example:
 
      % C1 is a column with a number but in string form
 
      % Cast it to an integer
      newCol = C1.cast('int');
```

#### matlab.pyspark.sql.column.Column.contains

```text
contains
```

#### matlab.pyspark.sql.column.Column.desc

```text
desc - Descending sort of column
```

#### matlab.pyspark.sql.column.Column.desc_nulls_first

```text
desc_nulls_first - Descending sort of column
```

#### matlab.pyspark.sql.column.Column.desc_nulls_last

```text
desc_nulls_last - Descending sort of column
```

#### matlab.pyspark.sql.column.Column.divide

```text
matlab.pyspark.sql.column.Column/divide is a function.
    col = divide(obj, other)
```

#### matlab.pyspark.sql.column.Column.endswith

```text
endswith
```

#### matlab.pyspark.sql.column.Column.eq

```text
eq - Determine equality
    This MATLAB function returns a logical array or a table of logical
    values with elements set to logical 1 (true) where inputs A and B are
    equal; otherwise, the element is logical 0 (false).

    Syntax
      A == B
      eq(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/EqualityOfTwoVectorsExample')
      openExample('matlab/FindCharactersInStringExample')
      openExample('matlab/FindValuesInCategoricalArrayExample')
      openExample('matlab/CompareFloatingPointNumbersExample')
      openExample('matlab/CompareDatetimeValuesExample')
      openExample('matlab/CompareTablesExample')

    See also isapprox, ge, gt, le, lt, ne

    Introduced in MATLAB before R2006a
    Documentation for eq
       doc eq
```

#### matlab.pyspark.sql.column.Column.ge

```text
ge - Determine greater than or equal to
    This MATLAB function returns a logical array or a table of logical
    values with elements set to logical 1 (true) where A is greater than or
    equal to B; otherwise, the element is logical 0 (false).

    Syntax
      A >= B
      ge(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/TestVectorElementsExample')
      openExample('matlab/ReplaceElementsofMatrixExample')
      openExample('matlab/CompareValuesinCategoricalArrayExample')
      openExample('matlab/TestComplexNumbersExample')
      openExample('matlab/TestDurationValuesGeExample')
      openExample('matlab/CompareTablesGEExample')

    See also eq, lt, gt, le, ne

    Introduced in MATLAB before R2006a
    Documentation for ge
       doc ge
```

#### matlab.pyspark.sql.column.Column.gt

```text
gt - Determine greater than
    This MATLAB function returns a logical array or a table of logical
    values with elements set to logical 1 (true) where A is greater than B;
    otherwise, the element is logical 0 (false).

    Syntax
      A > B
      gt(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/TestVectorElementsGreaterThanExample')
      openExample('matlab/ReplaceElementsofMatrixGreaterExample')
      openExample('matlab/CompareValuesinCategoricalArrayGreaterExample')
      openExample('matlab/TestComplexNumbersGreaterExample')
      openExample('matlab/CompareDatesExample')
      openExample('matlab/CompareTablesGTExample')

    See also eq, ge, lt, le, ne

    Introduced in MATLAB before R2006a
    Documentation for gt
       doc gt
```

#### matlab.pyspark.sql.column.Column.ilike

```text
ilike SQL ilike command
```

#### matlab.pyspark.sql.column.Column.isNaN

```text
isNaN
```

#### matlab.pyspark.sql.column.Column.isNotNull

```text
isNull
```

#### matlab.pyspark.sql.column.Column.isNull

```text
isNull
```

#### matlab.pyspark.sql.column.Column.isin

```text
isin - Column of booleans showing whether each element in the Column is contained in cols
```

#### matlab.pyspark.sql.column.Column.le

```text
le - Determine less than or equal to
    This MATLAB function returns a logical array or a table of logical
    values with elements set to logical 1 (true) where A is less than or
    equal to B; otherwise, the element is logical 0 (false).

    Syntax
      A <= B
      le(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/TestVectorElementsLessThanOrEqualExample')
      openExample('matlab/ReplaceElementsOfMatrixLessThanOrEqualExample')
      openExample('matlab/CompareValuesInCategoricalArrayLessThanOrEqualExample')
      openExample('matlab/TestComplexNumbersLessThanEqualExample')
      openExample('matlab/TestDurationValuesExample')
      openExample('matlab/CompareTablesLEExample')

    See also eq, ge, gt, lt, ne

    Introduced in MATLAB before R2006a
    Documentation for le
       doc le
```

#### matlab.pyspark.sql.column.Column.like

```text
like SQL like command
```

#### matlab.pyspark.sql.column.Column.lt

```text
lt - Determine less than
    This MATLAB function returns an array or a table of logical values with
    elements set to logical 1 (true) where A is less than B; otherwise, the
    element is logical 0 (false).

    Syntax
      A < B
      lt(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/TestVectorElementsLessThanExample')
      openExample('matlab/ReplaceElementsofMatrixLessThanExample')
      openExample('matlab/CompareValuesinCategoricalArrayLessThanExample')
      openExample('matlab/TestComplexNumbersLessThanExample')
      openExample('matlab/CompareDatesLessThanExample')
      openExample('matlab/CompareTablesLTExample')

    See also eq, ge, gt, le, ne

    Introduced in MATLAB before R2006a
    Documentation for lt
       doc lt
```

#### matlab.pyspark.sql.column.Column.minus

```text
minus - Subtraction
    This MATLAB function subtracts array B from array A by subtracting
    corresponding elements.

    Syntax
      C = A - B
      C = minus(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/SubtractScalarfromArrayExample')
      openExample('matlab/SubtractTwoArraysExample')
      openExample('matlab/SubtractRowAndColumnVectorsExample')
      openExample('matlab/SubtractMeanFromMatrixExample')
      openExample('matlab/SubtractTablesExample')

    See also plus, diff, uminus

    Introduced in MATLAB before R2006a
    Documentation for minus
       doc minus
```

#### matlab.pyspark.sql.column.Column.mrdivide

```text
mrdivide - Solve systems of linear equations xA = B for x
    This MATLAB function solves the system of linear equations x*A = B for
    x.

    Syntax
      x = B/A
      x = mrdivide(B,A)

    Input Arguments
      A - Operands
        vectors | full matrices | sparse matrices
      B - Operands
        vectors | full matrices | sparse matrices

    Output Arguments
      x - Solution
        vector | full matrix | sparse matrix

    Examples
      openExample('matlab/SystemofEquationsMrDivideExample')
      openExample('matlab/LeastSquaresonanUnderdeterminedSystemExample')

    See also mldivide, ldivide, rdivide, inv, transpose, decomposition

    Introduced in MATLAB before R2006a
    Documentation for mrdivide
       doc mrdivide
```

#### matlab.pyspark.sql.column.Column.mtimes

```text
mtimes - Matrix multiplication
    This MATLAB function is the matrix product of A and B.

    Syntax
      C = A*B
      C = mtimes(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices
      B - Operands
        scalars | vectors | matrices

    Output Arguments
      C - Product
        scalar | vector | matrix

    Examples
      openExample('matlab/MultiplyTwoVectorsExample')
      openExample('matlab/MultiplyTwoArraysExample')

    See also colon, times, dot, cross, pagemtimes, tensorprod

    Introduced in MATLAB before R2006a
    Documentation for mtimes
       doc mtimes
```

#### matlab.pyspark.sql.column.Column.multiply

```text
matlab.pyspark.sql.column.Column/multiply is a function.
    col = multiply(obj, other)
```

#### matlab.pyspark.sql.column.Column.ne

```text
ne - Determine inequality
    This MATLAB function returns a logical array or a table of logical
    values with elements set to logical 1 (true) where inputs A and B are
    not equal; otherwise, the element is logical 0 (false).

    Syntax
      A ~= B
      ne(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/InequalityOfTwoVectorsExample')
      openExample('matlab/FindCharactersInStringNotEqualExample')
      openExample('matlab/FindValuesInCategoricalArrayNotEqualExample')
      openExample('matlab/CompareFloatingPointNumbersNotEqualExample')
      openExample('matlab/InequalityOfTwoDatetimeArraysExample')
      openExample('matlab/CompareTablesNEExample')

    See also ge, gt, le, lt, eq

    Introduced in MATLAB before R2006a
    Documentation for ne
       doc ne
```

#### matlab.pyspark.sql.column.Column.not

```text
not - Find logical NOT
    This MATLAB function returns a logical array or a table of logical
    values of the same size as A.

    Syntax
      ~A
      not(A)

    Input Arguments
      A - Input array
        scalar | vector | matrix | multidimensional array | table |
        timetable

    Examples
      openExample('matlab/LogicalNegationOfMatrixExample')
      openExample('matlab/ConditionalCodeExecutionExample')
      openExample('matlab/LogicalNOTOfTableExample')

    See also any, all, bitcmp, xor, and, or

    Introduced in MATLAB before R2006a
    Documentation for not
       doc not
```

#### matlab.pyspark.sql.column.Column.or

```text
or - Find logical OR
    This MATLAB function performs a logical OR of inputs A and B and returns
    an array or a table containing elements set to either logical 1 (true)
    or logical 0 (false).

    Syntax
      A | B
      or(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/LocateZerosInMatricesExample')
      openExample('matlab/TruthTableForLogicalORExample')
      openExample('matlab/LogicalOROfTablesExample')

    See also any, all, bitor, xor, and, not

    Introduced in MATLAB before R2006a
    Documentation for or
       doc or
```

#### matlab.pyspark.sql.column.Column.otherwise_

```text
otherwise_ Used with when condition
 
  With added underscore, as otherwise is a reserved word in MATLAB            %
 
  df = spark.createDataFrame('[(2, "Alice"), (5, "Bob")]', schema=cellstr(["age", "name"]));
  df.select(df.name, ...
      matlab.pyspark.sql.functions.when(df.age > 3, int32(1)).otherwise_(int32(0))).show()
```

#### matlab.pyspark.sql.column.Column.over

```text
matlab.pyspark.sql.column.Column/over is a function.
    col = over(obj, window)
```

#### matlab.pyspark.sql.column.Column.plus

```text
plus - Add numbers, append strings
    This MATLAB function adds arrays A and B by adding corresponding
    elements.

    Syntax
      C = A + B
      C = plus(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/AddScalartoArrayExample')
      openExample('matlab/ConcatenateStringsExample')
      openExample('matlab/AddTwoArraysExample')
      openExample('matlab/AddRowAndColumnVectorsExample')
      openExample('matlab/AddVectorToMatrixExample')
      openExample('matlab/AddTablesExample')

    See also minus, sum, cumsum, uplus, append

    Introduced in MATLAB before R2006a
    Documentation for plus
       doc plus
```

#### matlab.pyspark.sql.column.Column.rdivide

```text
rdivide - Right array division
    This MATLAB function divides each element of A by the corresponding
    element of B.

    Syntax
      x = A./B
      x = rdivide(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/DivideTwoNumericArraysRDivideExample')
      openExample('matlab/IntegerDivisionExample')
      openExample('matlab/DivideScalarbyArrayExample')
      openExample('matlab/RdivideRowAndColumnVectorsExample')
      openExample('matlab/RightDivideTablesExample')

    See also ldivide, mldivide, mrdivide, idivide

    Introduced in MATLAB before R2006a
    Documentation for rdivide
       doc rdivide
```

#### matlab.pyspark.sql.column.Column.rem

```text
rem Reminder of obj to other, i.e. obj % other
 
   obj should be a column, and other can be a column, a number
   or a string
```

#### matlab.pyspark.sql.column.Column.rlike

```text
rlike SQL rlike command
```

#### matlab.pyspark.sql.column.Column.startswith

```text
startswith
```

#### matlab.pyspark.sql.column.Column.string

```text
string - String array
    You can represent text in MATLAB using string arrays where each element
    of a string array stores a sequence of characters.

    Creation
      Create Strings
        str = "text"
        str = ["text1" "text2" ...]
        str = "text1" + "text2"

      Convert Arrays
        str = string(A)

      Convert Dates and Times
        str = string(D,datefmt)
        str = string(D,datefmt,locale)

      Input Arguments
        A - Input array
          array
        D - Date or duration array
          datetime array | duration array | calendarDuration array
        datefmt - Date Format and Locale
          character vectors | string scalars
        locale - Locale
          character vector | string scalar

      Output Arguments
        str - Output array
          string array

    Object Functions
      contains       - Determine if pattern is in strings
      count          - Count occurrences of pattern in strings
      endsWith       - Determine if strings end with pattern
      matches        - Determine if pattern matches strings
      startsWith     - Determine if strings start with pattern
      compose        - Format data into multiple strings
      erase          - Delete substrings within strings
      eraseBetween   - Delete substrings between start and end points
      extract        - Extract substrings from strings
      extractAfter   - Extract substrings after specified positions
      extractBefore  - Extract substrings before specified positions
      extractBetween - Extract substrings between start and end points
      insertAfter    - Insert strings after specified substrings
      insertBefore   - Insert strings before specified substrings
      lower          - Convert strings to lowercase
      pad            - Add leading or trailing characters to strings
      replace        - Find and replace one or more substrings
      replaceBetween - Replace substrings between start and end points
      reverse        - Reverse order of characters in strings
      splitlines     - Split strings at newline characters
      strip          - Remove leading and trailing characters from strings
      upper          - Convert strings to uppercase
      eq             - Determine equality
      ge             - Determine greater than or equal to
      gt             - Determine greater than
      le             - Determine less than or equal to
      lt             - Determine less than
      ne             - Determine inequality

    Examples
      openExample('matlab/CreateStringExample')
      openExample('matlab/CreateStringArrayExample')
      openExample('matlab/SplitStringAndFindUniqueWordsExample')
      openExample('matlab/CreateStringFromCharacterVectorExample')
      openExample('matlab/CreateStringArrayFromCellArrayExample')
      openExample('matlab/ConvertNumbersToStringArraysExample')
      openExample('matlab/ConvertStringsThatRepresentNumbersExample')
      openExample('matlab/ConvertDurationArrayToStringArrayExample')
      openExample('matlab/ConvertLocalizedDatetimeToStringExample')

    See also append, contains, matches, startsWith, replace, replaceBetween,
      split, extract, extractBetween, char, cellstr, strlength, isstring,
      strings, compose, sprintf

    Introduced in MATLAB in R2016b
    Documentation for string
       doc string
```

#### matlab.pyspark.sql.column.Column.times

```text
times - Multiplication
    This MATLAB function multiplies arrays A and B by multiplying
    corresponding elements.

    Syntax
      C = A.*B
      C = times(A,B)

    Input Arguments
      A - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables
      B - Operands
        scalars | vectors | matrices | multidimensional arrays | tables |
        timetables

    Examples
      openExample('matlab/MultiplyTwoVectorsTimesExample')
      openExample('matlab/MultiplyTwoArraysTimesExample')
      openExample('matlab/MultiplyRowAndColumnVectorsExample')
      openExample('matlab/MultiplyTablesExample')

    See also mtimes

    Introduced in MATLAB before R2006a
    Documentation for times
       doc times
```

#### matlab.pyspark.sql.column.Column.toPy

```text
matlab.pyspark.sql.column.Column/toPy is a function.
    pyObj = toPy(obj)
```

#### matlab.pyspark.sql.column.Column.uminus

```text
uminus - Unary minus
    This MATLAB function negates the elements of A and stores the result in
    C.

    Syntax
      C = -A
      C = uminus(A)

    Input Arguments
      A - Input array
        scalar | vector | matrix | multidimensional array

    Examples
      openExample('matlab/NegateElementsofMatrixExample')

    See also minus, uplus

    Introduced in MATLAB before R2006a
    Documentation for uminus
       doc uminus
```

#### matlab.pyspark.sql.column.Column.when

```text
when condition/value choice
```

### matlab.pyspark.sql.dataframe

### matlab.pyspark.sql.dataframe.DataFrameNaFunctions

Superclass: matlab.pyspark.internal.PyWrapper

```text
DataFrameNaFunctions Pyspark DataFrameNaFunctions wrapper
```

#### matlab.pyspark.sql.dataframe.DataFrameNaFunctions.DataFrameNaFunctions

```text
DataFrameNaFunctions Pyspark DataFrameNaFunctions wrapper
```

#### matlab.pyspark.sql.dataframe.DataFrameNaFunctions.drop

```text
drop Drop rows
```

#### matlab.pyspark.sql.dataframe.DataFrameNaFunctions.fill

```text
fill Fill columns with default value
 
   df is some table with missing double values in Customers
   column. Fill them with 0.0 like this:
     df2 = df.na.fill(0.0, subset="Customers")
```

#### matlab.pyspark.sql.dataframe.DataFrameNaFunctions.toPy

```text
matlab.pyspark.sql.dataframe.DataFrameNaFunctions/toPy is a function.
    pyObj = toPy(obj)
```

### matlab.pyspark.sql.dataframe.Dataframe

Superclasses: matlab.pyspark.internal.PyWrapper, matlab.mixin.indexing.RedefinesDot

```text
Dataframe Pyspark DataFrame wrapper
  
  This class is a wrapper for the pyspark Dataframe class,
  matlab.pyspark.sql.dataframe.Dataframe, and implements a large part
  of its methods.
```

#### matlab.pyspark.sql.dataframe.Dataframe.Dataframe

```text
Dataframe Pyspark DataFrame wrapper
  
  This class is a wrapper for the pyspark Dataframe class,
  matlab.pyspark.sql.dataframe.Dataframe, and implements a large part
  of its methods.
```

#### matlab.pyspark.sql.dataframe.Dataframe.agg

```text
agg Aggregation method
 
  TODO: Currently only support columns, not dictionary
```

#### matlab.pyspark.sql.dataframe.Dataframe.alias

```text
alias Returns a new DataFrame with an alias set.
 
  Example:
  import matlab.pyspark.sql.functions.col
  import matlab.pyspark.sql.functions.desc
 
  spark = getDatabricksSession;
  df = spark.createDataFrame('[(14, "Tom"), (23, "Alice"), (16, "Bob")]', schema={'age', 'name'});
  df_as1 = df.alias("df_as1");
  df_as2 = df.alias("df_as2");
  joined_df = df_as1.join(df_as2, on=col("df_as1.name") == col("df_as2.name"), how='inner');
  joined_df.select("df_as1.name", "df_as2.name", "df_as2.age").sort(desc("df_as1.name")).show()
    +-----+-----+---+
    | name| name|age|
    +-----+-----+---+
    |  Tom|  Tom| 14|
    |  Bob|  Bob| 16|
    |Alice|Alice| 23|
    +-----+-----+---+
```

#### matlab.pyspark.sql.dataframe.Dataframe.bracket

```text
bracket Implement the df[arg] method
 
  This function is not targeted at general usage. It's supposed
  to handle bracket ([]) operations in Python in MATLAB.
  As an example:
    Python - df['a']
    MATLAB - df.bracket('a')
 
  Examples:
    % column foo
    DF.bracket('foo')  
    % column foo
    DF.bracket("foo")
    % fourth column (zero-based index)
    DF.bracket(3)      
 
    % DataFrame with foo and bar columns
    DF.bracket({"foo", "bar"})  
    % DataFrame with foo and bar columns
    DF.bracket(["foo", "bar"])
 
    % DataFrame filtered through column
    DF.bracket(aColumn)
    % DataFrame filtered through column
    DF.bracket(DF.bracket("foo").isin("3", "4"))
```

#### matlab.pyspark.sql.dataframe.Dataframe.cache

```text
cache - Cache Dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.col

```text
col Retrieving a column from a Dataframe
 
  Whereas this can retrieve a column, the dot-notation can also be
  used for many, use cases.
 
     c1 = DF.col('age')
     c2 = DF.age
 
   c1 and c2 will refer to the same column here.
 
  Please refer to the document DataframeColumns.md in the
  matlab-spark-api/Documentation directory for more information.
```

#### matlab.pyspark.sql.dataframe.Dataframe.columns

```text
columns - Return column names
```

#### matlab.pyspark.sql.dataframe.Dataframe.count

```text
count Counts the number of rows
```

#### matlab.pyspark.sql.dataframe.Dataframe.createOrReplaceTempView

```text
createOrReplaceTempView Create a temporary view
```

#### matlab.pyspark.sql.dataframe.Dataframe.describe

```text
describe Describe columns (statistics)
```

#### matlab.pyspark.sql.dataframe.Dataframe.distinct

```text
distinct - Returns a new DataFrame containing the distinct rows in this DataFrame.
```

#### matlab.pyspark.sql.dataframe.Dataframe.dotAssign

```text
dotAssign  Overload dot indexed assignment
     obj = dotAssign(obj, indexOp, varargin) is called by MATLAB
     for indexed assignment statements that begin with dot. Classes
     that inherit from RedefinesDot must implement this protected
     method. The dotAssign method must interpret the
     IndexingOperation argument indexOp, modify the obj argument
     based on the right-hand side values in varargin, and return
     the modified object.
 
     In a simple assignment such as
         obj.label = val;
     MATLAB calls dotAssign with the object obj and an
     IndexingOperation with a single element whose Type property is
     Dot and Name property is the string "label". The third input
     argument to dotAssign is the right-hand side value val.
 
     In a compound comma-separated list assignment such as
         [obj.(var){:}] = rhs{:};
     MATLAB first calls dotListLength on obj to determine how many
     inputs the object expects to receive in dotAssign. Assuming
     that the right-hand side provides enough values, dotAssign
     will be called with an IndexingOperation with two elements
     describing the Dot and Brace indexing in the statement. The
     values from the right-hand side are passed to dotAssign as
     varargin.
 
     The dotAssign method is not called for properties and
     methods that are accessible in the present context.
 
     Class authors can often handle compound indexing expressions
     by forwarding some or all of the later indexing operations to
     another object. For more information, look for 'forwarding
     indexing' in the documentation.
 
     See also dotListLength, dotReference,
              matlab.indexing.IndexingOperation

Help for matlab.pyspark.sql.dataframe.Dataframe/dotAssign is inherited from superclass matlab.mixin.indexing.RedefinesDot
```

#### matlab.pyspark.sql.dataframe.Dataframe.dotListLength

```text
Assuming our methods will always return a value
```

#### matlab.pyspark.sql.dataframe.Dataframe.dotReference

```text
dotReference  Overload dot indexed reference
     varargout = dotReference(obj, indexOp) is called by MATLAB for
     indexed reference expressions that begin with dot. Classes
     that inherit from RedefinesDot must implement this protected
     method. The dotReference method must interpret the
     IndexingOperation argument indexOp and return the correct
     number of requested outputs as varargout.
 
     In a simple statement such as 
         y = obj.label; 
     MATLAB calls dotReference with the object obj and an
     IndexingOperation with a single element whose Type property is
     Dot and whose Name property is the string "label".
 
     In a compound reference statement such as 
         [y1, y2, y3] = obj.(var).subprop
     MATLAB calls dotReference with an IndexingOperation array with
     two elements whose Type properties are each Dot, and requests
     three outputs. The Name property of the first element is the
     value of the variable "var" and the Name property of the
     second element is the string "subprop".
 
     The dotReference method is not called for properties and
     methods that are accessible in the present context.
 
     Class authors can often handle compound indexing expressions
     by forwarding some or all of the later indexing operations to
     another object. For more information, look for 'forwarding
     indexing' in the documentation.
 
     See also dotAssign, dotListLength, 
              matlab.indexing.IndexingOperation

Help for matlab.pyspark.sql.dataframe.Dataframe/dotReference is inherited from superclass matlab.mixin.indexing.RedefinesDot
```

#### matlab.pyspark.sql.dataframe.Dataframe.drop

```text
drop Drop certain columns from Dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.dropDuplicates

```text
dropDuplicates Drop duplicates
```

#### matlab.pyspark.sql.dataframe.Dataframe.dropna

```text
dropna Drop rows with NULL or NaN values
```

#### matlab.pyspark.sql.dataframe.Dataframe.filter

```text
filter Filter rows in a dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.groupBy

```text
GROUPBY Group dataset by certain columns
 
  This will return a new RelationalGroupDataset
```

#### matlab.pyspark.sql.dataframe.Dataframe.isEmpty

```text
isEmpty Returns true for empty dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.join

```text
join Database join
 
  Some syntax examples:
 
  R = spark.range(4)
  DF1 = R.withColumn("A", R.col('id').cast('string'))
  DF2 = R.withColumn("B", R.col('id').cast('double'))
  DF1.join(DF2).show()
  DF1.join(DF2, how="outer").show()
  DF1.join(DF2, how="left").show()
  DF1.join(DF2, on=DF1.col('id')==DF2.col('id'),how="left").show()
```

#### matlab.pyspark.sql.dataframe.Dataframe.limit

```text
limit - Limit size of dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.mapInPandas

```text
mapInPandas - Run mapInPandas on a function and a schema
 
  This method applies mapInPandas on a specific function and
  schema. In the general case it's called like this:
 
    DF_OUT = DF.mapInPandas("someFunc", schema="someSchema);
 
  someFunc and someSchema must be available in the python environment.
 
  An alternative way of calling it, in the case a function was
  generated from MATLAB code (see PythonSparkBuilder).
 
    DF_OUT = DF.mapInPandas("myFunc");
 
  This calling will assume that the values available in the python
  environment are myFunc_mapInPandas and myFunc_output_schema.
```

#### matlab.pyspark.sql.dataframe.Dataframe.na

```text
na Get na object
```

#### matlab.pyspark.sql.dataframe.Dataframe.orderBy

```text
orderBy Sort a dataframe by columns
 
  This is an alias for sort
```

#### matlab.pyspark.sql.dataframe.Dataframe.printSchema

```text
printSchema Display the Dataset's underlying schema in the console
 
  Example:
 
      DS.printSchema()
```

#### matlab.pyspark.sql.dataframe.Dataframe.repartition

```text
matlab.pyspark.sql.dataframe.Dataframe/repartition is a function.
    df = repartition(obj, numPartitions, arg)
```

#### matlab.pyspark.sql.dataframe.Dataframe.repartitionByRange

```text
repartitionByRange 
  
  import matlab.pyspark.sql.Window
  df = spark.createDataFrame('[(2, "Alice"), (5, "Bob")]', ...
       schema=cellstr(["age", "name"]))
  df.repartitionByRange(2, "age") ...
      .select("age", "name", matlab.pyspark.sql.functions.spark_partition_id()).show()
```

#### matlab.pyspark.sql.dataframe.Dataframe.sample

```text
sample Create a temporary view
```

#### matlab.pyspark.sql.dataframe.Dataframe.schema

```text
schema Return MATLAB representation of Dataframe schema
```

#### matlab.pyspark.sql.dataframe.Dataframe.select

```text
SELECT Method to select columns by name
 
  SELECT(obj,columns) will return a new dataset that contains only the
  Example:
 
      % Create a dataset
      myLocation = '/test/*.parquet');
      myDataSet = spark...
          .read.format('parquet')...
          .option('header','true')...
          .option('inferSchema','true')...
          .load(myLocation);
 
      % Select a subset of the Dataset with just a few columns
      newDataSet = myDataSet.select("UniqueCarrier", "Day", "Month");
```

#### matlab.pyspark.sql.dataframe.Dataframe.show

```text
show - Show a Dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.sort

```text
sort Sort a dataframe by columns
```

#### matlab.pyspark.sql.dataframe.Dataframe.summary

```text
summary Show summary of all/chosen columns
```

#### matlab.pyspark.sql.dataframe.Dataframe.table

```text
table - Convert Spark DataFrame to MATLAB table
```

#### matlab.pyspark.sql.dataframe.Dataframe.table_R2023b

```text
table - Convert Spark dataframe to MATLAB table
 
  This methods is necessary to handle release R2023b and earlier,
  as these releases have no conversion from Pandas Dataframe to MATLAB
  table.
```

#### matlab.pyspark.sql.dataframe.Dataframe.toDF

```text
toDF - Rename columns of a Dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.toPandas

```text
toPandas Return Python Pandas Dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.toPy

```text
matlab.pyspark.sql.dataframe.Dataframe/toPy is a function.
    pyObj = toPy(obj)
```

#### matlab.pyspark.sql.dataframe.Dataframe.transform

```text
transform Returns a new DataFrame. Concise syntax for chaining custom transformations.
 
  Here's a simple example on how the transform function can be used on
  Dataframes, either with MATLAB functions, or with Python functions.
 
      function DF_new = tf1(DF)
          import matlab.pyspark.sql.functions.lit
          DF_new = DF.withColumn("hello", lit("Hello"));
      end
     
      function pyTransform = tf2()
          funcDef = ...
              "def myfunc(DF):" + ...
              "    return DF.withColumn('doubled', DF['id'] * 2)";
          funcReturn = "a = myfunc";
          pyTransform = pyrun([funcDef, funcReturn], "a");
      end
 
      R = spark.range(5);
      DF = R.transform(@tf1).transform(tf2());
      DF.show()
      +---+-----+-------+
      | id|hello|doubled|
      +---+-----+-------+
      |  0|Hello|      0|
      |  1|Hello|      2|
      |  2|Hello|      4|
      |  3|Hello|      6|
      |  4|Hello|      8|
      +---+-----+-------+
```

#### matlab.pyspark.sql.dataframe.Dataframe.where

```text
where Filter rows in a dataframe (alias for filter)
```

#### matlab.pyspark.sql.dataframe.Dataframe.withColumn

```text
withColumn - Add a new column
```

#### matlab.pyspark.sql.dataframe.Dataframe.withColumnRenamed

```text
WITHCOLUMNRENAMED Rename one column in dataframe
```

#### matlab.pyspark.sql.dataframe.Dataframe.write

```text
matlab.pyspark.sql.dataframe.Dataframe/write is a function.
    writer = write(obj)
```

### matlab.pyspark.sql.functions

### matlab.pyspark.sql.functions.abs

```text
abs Absolute value
```

### matlab.pyspark.sql.functions.acos

```text
acos Arc cosine value
```

### matlab.pyspark.sql.functions.add_months

```text
add_months Add months to a column
```

### matlab.pyspark.sql.functions.array

```text
array Concatenate columns to an array
```

### matlab.pyspark.sql.functions.asc

```text
asc Returns sorted column, ascending
```

### matlab.pyspark.sql.functions.asin

```text
asin Arcsine value
```

### matlab.pyspark.sql.functions.atan

```text
atan Arc tangens value
```

### matlab.pyspark.sql.functions.ceil

```text
ceil Take ceil (rounding) of column
```

### matlab.pyspark.sql.functions.col

```text
col - Get column by name
```

### matlab.pyspark.sql.functions.column

```text
column Return a column from a name
```

### matlab.pyspark.sql.functions.concat

```text
concat Concatenates several columns
```

### matlab.pyspark.sql.functions.current_date

```text
current_date Current date
```

### matlab.pyspark.sql.functions.current_timestamp

```text
current_timestamp Current timestamp
```

### matlab.pyspark.sql.functions.date_add

```text
date_add Add days to a column
```

### matlab.pyspark.sql.functions.date_format

```text
date_format Convert time/date column to string column
```

### matlab.pyspark.sql.functions.date_sub

```text
date_sub Sbutract days from a column
```

### matlab.pyspark.sql.functions.dayofmonth

```text
dayofmonth Extract dayofmonth from a column
```

### matlab.pyspark.sql.functions.dayofweek

```text
dayofweek Extract dayofweek from a column
```

### matlab.pyspark.sql.functions.dayofyear

```text
dayofyear Extract dayofyear from a column
```

### matlab.pyspark.sql.functions.desc

```text
desc Returns sorted column, descending
```

### matlab.pyspark.sql.functions.floor

```text
floor Take floor (rounding) of column
```

### matlab.pyspark.sql.functions.from_unixtime

```text
from_unixtime Convert column from unix time
```

### matlab.pyspark.sql.functions.from_utc_timestamp

```text
from_utc_timestamp Convert time/date from UTC to TZ
```

### matlab.pyspark.sql.functions.hour

```text
hour Extract hour from a column
```

### matlab.pyspark.sql.functions.lit

```text
LIT Creates a column containing a constant value
 
  This function will return a new column with a literal value.
```

### matlab.pyspark.sql.functions.make_date

```text
make_date Create date column
```

### matlab.pyspark.sql.functions.make_timestamp

```text
make_timestamp Create a timestamp column
  
  This function exclusively uses named arguments. Any errors due to
  using invalid combinations, e.g. 'date' and 'year', will be handled
  by the underlying Spark libraries
 
  Example:
  spark = getDatabricksSession();
  data = {
      {2023, 1, 2, 14, 20, 12.345, 'UTC'},
      {2023, 1, 2, 14, 20, 12.345, 'America/New_York'},
      {2023, 1, 2, 14, 20, 12.345, 'Europe/Berlin'},
      {2023, 1, 2, 14, 20, 12.345, 'Asia/Calcutta'},
      };
  columns = {'year', 'month', 'day', 'hour', 'min', 'sec', 'tz'};
  df = spark.createDataFrame(data, schema=columns);
  df = df.withColumn("ts_no_tz", matlab.pyspark.sql.functions.make_timestamp(years="year", month="month", days="day", hours="hour", mins="min", secs="sec"));
  df = df.withColumn("ts_with_tz", matlab.pyspark.sql.functions.make_timestamp(years="year", month="month", days="day", hours="hour", mins="min", secs="sec", timezone="tz"));
  df.show(10, false)
 
  See also https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.make_timestamp.html
```

### matlab.pyspark.sql.functions.make_timestamp_ltz

```text
make_timestamp_ltz Create a timestamp column
  
  This function exclusively uses named arguments. Any errors due to
  using invalid combinations, e.g. 'date' and 'year', will be handled
  by the underlying Spark libraries
 
  Example:
  spark = getDatabricksSession();
  data = {
      {2023, 1, 2, 14, 20, 12.345, 'UTC'},
      {2023, 1, 2, 14, 20, 12.345, 'America/New_York'},
      {2023, 1, 2, 14, 20, 12.345, 'Europe/Berlin'},
      {2023, 1, 2, 14, 20, 12.345, 'Asia/Calcutta'},
      };
  columns = {'year', 'month', 'day', 'hour', 'min', 'sec', 'tz'};
  df = spark.createDataFrame(data, schema=columns);
  df = df.withColumn("ts_no_tz", matlab.pyspark.sql.functions.make_timestamp_ltz(years="year", month="month", days="day", hours="hour", mins="min", secs="sec"));
  df = df.withColumn("ts_with_tz", matlab.pyspark.sql.functions.make_timestamp_ltz(years="year", month="month", days="day", hours="hour", mins="min", secs="sec", timezone="tz"));
  df.show(10, false)
 
  See also https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.make_timestamp_ltz.html
```

### matlab.pyspark.sql.functions.make_timestamp_ntz

```text
make_timestamp_ntz Create a timestamp column
  
  This function exclusively uses named arguments. Any errors due to
  using invalid combinations, e.g. 'date' and 'year', will be handled
  by the underlying Spark libraries
 
  Example:
  spark = getDatabricksSession();
  data = {
      {2023, 1, 2, 14, 20, 12.345, 'UTC'},
      {2023, 1, 2, 14, 20, 12.345, 'America/New_York'},
      {2023, 1, 2, 14, 20, 12.345, 'Europe/Berlin'},
      {2023, 1, 2, 14, 20, 12.345, 'Asia/Calcutta'},
      };
  columns = {'year', 'month', 'day', 'hour', 'min', 'sec', 'tz'};
  df = spark.createDataFrame(data, schema=columns);
  % Please note the timezone is not used in withColumn method (not supported with this method)
  df = df.withColumn("ts_no_tz", matlab.pyspark.sql.functions.make_timestamp_ntz(years="year", month="month", days="day", hours="hour", mins="min", secs="sec"));
  df.show(10, false)
 
  See also https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.make_timestamp_ntz.html
```

### matlab.pyspark.sql.functions.max

```text
max Max value
```

### matlab.pyspark.sql.functions.mean

```text
mean Mean value
```

### matlab.pyspark.sql.functions.min

```text
min Minimum value
```

### matlab.pyspark.sql.functions.minute

```text
minute Extract minute from a column
```

### matlab.pyspark.sql.functions.monotonically_increasing_id

```text
monotonically_increasing_id Monotonically increasing ID
 
  Add something to this if necessary
```

### matlab.pyspark.sql.functions.month

```text
month Extract month from a column
```

### matlab.pyspark.sql.functions.percent_rank

```text
percent_rank Creates a percent_rank column
 
  import matlab.pyspark.sql.Window
  df = spark.createDataFrame('[1, 1, 2, 3, 3, 4]', schema={'value'});
  w = Window.orderBy("value");
  df.withColumn("pr", matlab.pyspark.sql.functions.percent_rank().over(w)).show()
```

### matlab.pyspark.sql.functions.pow

```text
pow Power function
```

### matlab.pyspark.sql.functions.product

```text
product Aggregate function: returns the product of the values in a group.
 
  df = spark.sql("SELECT id % 3 AS mod3, id AS value FROM RANGE(10)");
  df.groupBy('mod3').agg(matlab.pyspark.sql.functions.product('value')).orderBy('mod3').show();
```

### matlab.pyspark.sql.functions.rand

```text
rand Creates a random column, uniformly distributed.
```

### matlab.pyspark.sql.functions.randn

```text
randn Creates a random column, normally distributed.
```

### matlab.pyspark.sql.functions.rank

```text
rank Creates a rank column
 
  import matlab.pyspark.sql.Window    
  df = spark.createDataFrame('[1, 1, 2, 3, 3, 4]', schema={'value'});
  w = Window.orderBy("value")
  df.withColumn("drank", matlab.pyspark.sql.functions.rank().over(w)).show();
```

### matlab.pyspark.sql.functions.round

```text
round Round a column
```

### matlab.pyspark.sql.functions.row_number

```text
row_number Creates a row_number column
 
  import matlab.pyspark.sql.Window    
  df = spark.range(3)
  w = Window.orderBy(df.id.desc())
  df.withColumn("desc_order", matlab.pyspark.sql.functions.row_number().over(w)).show()
```

### matlab.pyspark.sql.functions.second

```text
second Extract second from a column
```

### matlab.pyspark.sql.functions.spark_partition_id

```text
spark_partition_id Creates a spark_partition_id column
 
  spark.range(0,10,1,5).select("*", matlab.pyspark.sql.functions.spark_partition_id()).show()
```

### matlab.pyspark.sql.functions.sum

```text
sum Creates a sum of a column
```

### matlab.pyspark.sql.functions.to_date

```text
to_date Convert column to date
```

### matlab.pyspark.sql.functions.to_timestamp

```text
to_timestamp Convert column to timestamp
```

### matlab.pyspark.sql.functions.transform

```text
transform Transforms column into new column
 
  The transformation that is applied is done by an operation that can
  already be applied to a column, e.g. col * 2
 
  Example for using transforms. 
 
  function DF = test2_transform(spark)
 
      import matlab.pyspark.sql.functions.transform
      DF = spark.range(10);
      DF = DF ...
          .withColumn('doubled', transform(DF.('id'), @tf1)) ...
          .withColumn('stringed', transform(DF.('id'), @(x) x.cast('string')));
      % DF = DF ...
      %     .withColumn("add_3", transform(DF.('id'), tf2(3)));
  end
 
  function new_col = tf1(col)
      % tf1 - Double a column in MATLAB code
      new_col = col * 2;
  end
 
  function pyTransform = tf2(num)
      % tf2 Add num to a column in Python code
 
      funcDef = ...
          "def adder(col):" + ...
          "    return (col + " + string(num) + ")";
          % "    return (col + 2.5)";
      funcReturn = "a = adder";
 
      pyTransform = pyrun([funcDef, funcReturn], "a");
 
  end
```

### matlab.pyspark.sql.functions.unix_timestamp

```text
unix_timestamp Convert column to timestamp
```

### matlab.pyspark.sql.functions.weekofyear

```text
weekofyear Extract weekofyear from a column
```

### matlab.pyspark.sql.functions.when

```text
when condition/value choice
```

### matlab.pyspark.sql.functions.window

```text
window Bucketize into windows
```

### matlab.pyspark.sql.functions.year

```text
year Extract year from a column
```

### matlab.pyspark.sql.session

### matlab.pyspark.sql.session.SparkSession

Superclass: matlab.pyspark.internal.PyWrapper

```text
SparkSession - Base class for a Python SparkSession
```

#### matlab.pyspark.sql.session.SparkSession.SparkSession

```text
SparkSession - Base class for a Python SparkSession
```

#### matlab.pyspark.sql.session.SparkSession.addArtifact

```text
addArtifact  Add an artifact to a Spark session
 
  Only works with Spark Connect
 
  Please refer to corresponding pyspark documentation
```

#### matlab.pyspark.sql.session.SparkSession.catalog

```text
matlab.pyspark.sql.session.SparkSession/catalog is a function.
    sparkCatalog = catalog(obj)
```

#### matlab.pyspark.sql.session.SparkSession.createDataFrame

```text
createDataFrame Create a Spark DataFrame from a MATLAB table
  Data can be of type cell array, MATLAB table or py.pandas.DataFrame.
  An optional schema can currently only be specified as a scalar string.
  samplingRatio is not supported as it only applies to RDD-based DataFrames
  verifySchema is not supported when using Spark/Databricks Connect.
 
  A matlab.pyspark.sql.dataframe.Dataframe is returned.
 
  Example:
    LastName = {'Sanchez';'Johnson';'Li';'Diaz';'Brown'};
    Age = [38;43;38;40;49];
    Smoker = logical([1;0;1;0;1]);
    Height = [71;69;64;67;64];
    Weight = [176;163;131;133;119];
    BloodPressure = [124 93; 109 77; 125 83; 117 75; 122 80];
    T = table(LastName,Age,Smoker,Height,Weight,BloodPressure)
 
    spark = getDatabricksSession;
    df = spark.sparkSession.createDataFrame(T);
    df.show
    +--------+----+------+------+------+---------------+---------------+
    |LastName| Age|Smoker|Height|Weight|BloodPressure_1|BloodPressure_2|
    +--------+----+------+------+------+---------------+---------------+
    | Sanchez|38.0|  true|  71.0| 176.0|          124.0|           93.0|
    | Johnson|43.0| false|  69.0| 163.0|          109.0|           77.0|
    |      Li|38.0|  true|  64.0| 131.0|          125.0|           83.0|
    |    Diaz|40.0| false|  67.0| 133.0|          117.0|           75.0|
    |   Brown|49.0|  true|  64.0| 119.0|          122.0|           80.0|
    +--------+----+------+------+------+---------------+---------------+
   
  See also: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.createDataFrame.html
```

#### matlab.pyspark.sql.session.SparkSession.delete

```text
delete - Delete files or objects
    This MATLAB function deletes filename from disk, without requesting
    verification.

    Syntax
      delete filename
      delete filename1 ... filenameN
      delete(___,ResolveSymbolicLinks=tf)
      delete(obj)

    Input Arguments
      filename - Name of file to delete
        character vector | string scalar
      obj - Object
        single object | array of objects
      tf - Remove target of symbolic link
        false or 0 (default) | true or 1

    Examples
      openExample('matlab/DeleteFilesInFolderExample')
      openExample('matlab/DeleteGraphicsObjectsExample')

    See also clear, dir, recycle, rmdir, delete

    Introduced in MATLAB before R2006a
    Documentation for delete
       doc delete
```

#### matlab.pyspark.sql.session.SparkSession.range

```text
range - Return a dataframe range
 
  obj, start, end_, step, numPartitions
```

#### matlab.pyspark.sql.session.SparkSession.read

```text
read  Get a DataFrameReader
 
  Please refer to corresponding pyspark documentation
```

#### matlab.pyspark.sql.session.SparkSession.session_id

```text
V Return spark session_id
```

#### matlab.pyspark.sql.session.SparkSession.sql

```text
sql - Execute a SQL statement
 
  This version doesn't support additional arguments for binding special
  variables. When applicable, this can be achieved by formatting the
  string correspondingly instead, e.g. using sprintf statements.
```

#### matlab.pyspark.sql.session.SparkSession.stop

```text
matlab.pyspark.sql.session.SparkSession/stop is a function.
    stop(obj)
```

#### matlab.pyspark.sql.session.SparkSession.table

```text
table Read table from Spark context
```

#### matlab.pyspark.sql.session.SparkSession.toPy

```text
matlab.pyspark.sql.session.SparkSession/toPy is a function.
    pyObj = toPy(obj)
```

#### matlab.pyspark.sql.session.SparkSession.version

```text
V Return spark version
```

### matlab.sparkutils

### matlab.sparkutils.table2dataset

```text
TABLE2DATASET Function to create Spark dataset from MATLAB table
 
  It takes as arguments a MATLAB table, the spark session reference, and
  an optional schema object, and converts the table into a Dataset object.
 
  This function should be used for tests, not for large tables.
 
  To use it, at least a table and a spark session are needed:
 
    dataset = matlab.sparkutils.table2dataset(matlabTable, sparkSession);
 
  When the optional third input argument (schema) is not provided, the
  Column data types are automatically mapped as follows (also see the 
  createSparkSchemaFromMatlabType in the functions folder):
 
    MATLAB            Spark     Notes
    ======            ======    =====
    char              String    converting back to MATLAB results in string, not char
    string            String    <missing> value interpreted as the String \0
    double            Double
    single            Float
    int8              Byte
    int16             Short
    int32             Integer
    int64             Long
    logical           Boolean
    struct            Struct
    table             Struct    converting back to MATLAB results in struct, not table
    containers.Map    Map
    cell              WrappedArray
    datetime          Timestamp
    duration          CalendarInterval
    (any other type)  *** NOT SUPPORTED ***
 
  An optional third argument (schema) can also be specified. This is useful
  when a schema object is already available, for example the schema of a
  pre-existing Spark dataset.
 
    dataset = spark.read.format("parquet").load("/my/files")
    T = table(dataset);
    T = runAlgorithm(T);
    schema = dataset.schema;
    dataset = matlab.sparkutils.table2dataset(matlabTable, sparkSession, schema);
 
  The optional schema argument can also be specified as a cell-array of
  chars or a string array, representing case-insensitive column data types.
  Only the following basic data types are supported:
 
    string or char, double, single or float, int8 or byte, int16 or short,
    int32 or int or integer, int64 or long, logical or boolean, duration,
    datetime or timestamp.
 
  This list does not include complex data types such as struct, map,
  or table. If your data contains such data types, either use the 2-inputs
  variant of this function in order to auto-generate the schema, or use a
  schema-object from a pre-existing dataset object.
```

----
Copyright 2026 The MathWorks, Inc.
