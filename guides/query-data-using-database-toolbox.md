
# Query Data in Databricks from MATLAB Using Database Toolbox

This guide shows how to execute SQL queries on tabular data you have stored in Databricks, using the Database Toolbox&trade; in MATLAB.

You need:

- Database Toolbox for MATLAB. To check if the toolbox is installed, use the `ver` command.

- The MATLAB Interface for Databricks package. To install the package, follow the set up instructions in [Run MATLAB Interactively on Databricks](./run-matlab-interactively-on-databricks.md). (In particular, you must complete [Step 3: Install the MATLAB Interface for Databricks package](./run-matlab-interactively-on-databricks.md#step-3-install-matlab-interface-for-databricks-package)).

You can connect either to a specific cluster or to a SQL warehouse. To find out which method your organization recommends, contact your administrator:

- [Connect to a Specific Cluster](#connect-to-a-specific-cluster)
- [Connect to SQL Warehouse](#connect-to-sql-warehouse)

## Connect to a Specific Cluster

You can choose a cluster for running your queries. For simple queries, you might want to use the same cluster running MATLAB. This is selected by default. For more complex queries, you might want to select a different cluster by specifying the `cluster` argument in the code below. Check that your cluster is running before you try to connect to it, otherwise MATLAB will wait for the cluster to start.

```matlab
j = databricks.JDBCConnection(cluster=id, authMethod="OauthU2M", useDriverAuth=false)

myData = fetch(j.Connection, "SELECT * FROM mycatalog.mydatabasename.myDatabaseTable LIMIT 10");
```

The databricks.JDBCConnection function supports a number of optional arguments you can pass to the [Databricks JDBC Driver](https://docs.databricks.com/aws/en/integrations/jdbc/). To see the complete list of arguments, enter `doc databricks.JDBCConnection` in the MATLAB command window.

Some naming restrictions apply when you use SQL. For details, see [SQL Names Reference (Databricks)](https://docs.databricks.com/en/sql/language-manual/sql-ref-names.html).

A connection usually takes a few seconds to return. If the connection is unsuccessful, an empty `database.JDBCConnection.Connection` is returned in the connection property. If a JDBC Driver Error is returned in the connection's
`Message` property, it is displayed but an error is not raised directly.

To verify that a connection has been established successfully, run:

```matlab
[tf, message] = j.testConnection()
```

The results of your query are stored in the table `myData`.

When you do not need the connection any longer, call the connection property's close method. You can also use the the object's close method, which calls the connection's close method.

### Example

```matlabsession

% Read the entire table
data = sqlread(j.Connection, 'mycatalog.mydatabasename.outages');

Display the first few lines of the table
head(data,3)

>> head(data,3)
       Region               OutageTime             Loss     Customers          RestorationTime              Cause      
    _____________    _________________________    ______    __________    _________________________    ________________
    {'SouthWest'}    {'2002-02-01 12:18:00.0'}    458.98    1.8202e+06    {'2002-02-07 16:50:00.0'}    {'winter storm'}
    {'SouthEast'}    {'2003-01-23 00:49:00.0'}    530.14    2.1204e+05    {0×0 char               }    {'winter storm'}
    {'SouthEast'}    {'2003-02-07 21:15:00.0'}     289.4    1.4294e+05    {'2003-02-17 08:14:00.0'}    {'winter storm'}

% Delete the table if no longer needed
execute(Connection, 'DROP TABLE mycatalog.mydatabasename.outages')

% Close the connection when done
close(Connection);
```

## Connect to SQL Warehouse

This guide shows how to query your data stored in a [SQL Warehouse (Databricks)](https://docs.databricks.com/aws/en/compute/sql-warehouse) on Databricks using Database Toolbox.

- [Get Started](#get-started)
- [REST API](#using-matlab-to-connect-to-the-databricks-rest-api-for-sql-warehouses)

### Get Started

To interact with the Databricks REST API for SQL Warehouses from MATLAB, you use the `databricks.SQLWarehouse`
class in MATLAB. This class has the same properties as a warehouse in the Databricks REST
API. For the complete list of properties, see
[Databricks REST API for SQL Warehouses](https://docs.databricks.com/api/workspace/warehouses/get).

To connect to a SQL warehouse, you can either list the warehouses and then "select" one:

```matlab
% List all warehouses
warehouses = databricks.SQLWarehouse.list();
% As an example select the second one
warehouse = warehouses(2);
```

or if you know a specific warehouse ID, you can create a `SQLWarehouse` instance and specify the ID.
that id:

```matlab
% Create a SQLWarehouse instance 
warehouse = databricks.SQLWarehouse;
% And specify a specific id
warehouse.id = "qfufxboufejuuibuxbz";
```

To connect to the warehouse using Database Toolbox, run:

```matlab
conn = warehouse.connect(authMethod="OauthU2M", useDriverAuth=false);
myData = fetch(conn, "SELECT * FROM mycatalog.mydatabasename.myDatabaseTable LIMIT 10");
```

The results of your query are stored in the table `myData`.

The `connect` function uses the Database Toolbox `database` function and the connection object is the same kind of object returned by `database`. Check the `Message` field of the object to ensure the
connection was successful, in which case `Message` will be empty. If there is an error, `Message` will contain the error message.

### Using MATLAB to Connect to the Databricks REST API for SQL Warehouses

To connect to the Databricks API for SQL warehouses from MATLAB, use these functions in MATLAB.

#### List

To list all available SQL warehouses in your
Databricks workspace, call the static `list` method:

```matlab
warehouses = databricks.SQLWarehouse.list();
```

This will return an array of `databricks.SQLWarehouse` objects. If no warehouses have been
configured an empty `0x0` array of `databricks.SQLWarehouse` objects is returned.

#### Create

To create a SQL warehouse, you must set some required options and can set optional others. For details, see [Create Warehouse (Databricks)](https://docs.databricks.com/sql/api/sql-endpoints.html#create). You might not have privileges to create a warehouse. Contact your administrator for help.

```matlab
% Create an empty SQLWarehouse instance
warehouse = databricks.SQLWarehouse;
% Configure all required options - the actual values are just an example here
warehouse.name = "myNewInstance"
warehouse.cluster_size = "Small";
warehouse.min_num_clusters = 1;
warehouse.max_num_clusters = 2;
% Create the SQL warehouse on Databricks
warehouse.create();
```

If successful, the `warehouse`'s `id` property is updated, along with other properties like `state`.

#### Refresh

In the Databricks API, this method is called [Get (Databricks)](https://docs.databricks.com/api/workspace/warehouses/get). It is called `refresh` here to avoid confusion with MATLAB's built-in `get`/`set` methods.

Use `refresh` to update the properties of a SQLWarehouse you retrieved before, for example by using `list`:

```matlab
%% Initial inspection of the warehouses
% List all warehouses
>> warehouses = databricks.SQLWarehouse.list();
% As an example select the second one
>> warehouse = warehouses(2);
% Check the state
>> warehouse.state

ans = 

  WarehouseState enumeration

    STARTING

%% At some later point in time, check whether the state is still the same
% First refresh
>> warehouse.refresh()
% And display the current state
>> warehouse.state

ans = 

  WarehouseState enumeration

    RUNNING
```

You can also use `refresh` to query the information of an warehouse with some known ID,
for example:

```matlab
% Create a SQLWarehouse instance - all its properties will be empty
>> warehouse = databricks.SQLWarehouse;
% Specify a specific known ID - id is then set, but all other properties are still empty
>> warehouse.id = "qfufxboufejuuibuxbz";
% Call refresh - this queries the REST API and all other properties will be filled out
>> warehouse.refresh()
% Show the object
>> warehouse

    warehouse = 
      
        SQLWarehouse with properties:
      
                             id: "qfufxboufejuuibuxbz"
                           name: "myWarehouse"
                   cluster_size: "2X-Small"
                 auto_stop_mins: 10
           spot_instance_policy: COST_OPTIMIZED
                   num_clusters: 1
               min_num_clusters: 1
               max_num_clusters: 1
            num_active_sessions: 0
                          state: RUNNING
                   creator_name: "username@example.com"
                     creator_id: "3141592653589793"
                       jdbc_url: "jdbc:spark://adb-42424242424242.1.azuredatabricks.net:443/default;transportMode=http;ssl=1;AuthMech=3;httpPath=/sql/1.0/warehouses/qfufxboufejuuibuxbz;"
                    odbc_params: [1×1 databricks.datastructures.ODBCParams]
                           tags: [1×1 databricks.datastructures.WarehouseTags]
                         health: [1×1 databricks.datastructures.WarehouseHealth]
                  enable_photon: 1
      enable_serverless_compute: 0
                        channel: [1×1 databricks.datastructures.Channel]
```

Finally, you can use `refresh` to refresh multiple warehouses at once, for example:

```matlab
% Get the list of warehouses, if there are more than one this will be an array
warehouses = databricks.SQLWarehouses.list()
% Update all of those warehouses in one call
warehouses.refresh();
```

#### Edit

Use `edit` to change the settings of an existing cluster. For details about what you can chage, see [Edit (Datarbricks)](https://docs.databricks.com/api/workspace/warehouses/edit). To use the
`edit` method, you must set the `id` property, for example:

```matlab
% Create an SQLWarehouse Instance
warehouse = databricks.SQLWarehouse;
% Specify which instance is to be updated
warehouse.id = "qfufxboufejuuibuxbz";
% Set a modified value
warehouse.name = "My New Name";
% Apply the edit
warehouse.edit();
```

You can also obtain a warehouse using `list`,
then modify one or more properties and apply the edit:

```matlab
% Get the list
warehouses = databricks.SQLWarehouse.list();
% Select the first warehouse
warehouse = warehouses(1);
% Modify two of its settings
warehouse.name = "My New Name";
warehouses.max_num_clusters = 42;
% Apply the edit
warehouse.edit();
```

You can only use the `edit` method on `databricks.SQLWarehouse` scalars and not on on arrays.

#### Start

The `start` method starts SQL warehouses that exist but are stopped. For example

```matlab
% List all warehouses
warehouses = databricks.SQLWarehouse.list();
% As an example select the second one
warehouse = warehouses(2);
```

or if you know a specific ID, create a `SQLWarehouse` instance and set its ID:

```matlab
% Create a SQLWarehouse instance 
warehouse = databricks.SQLWarehouse;
% And specify a specific id
warehouse.id = "qfufxboufejuuibuxbz";
```

Then call the `start` method to actually start the warehouse:

```matlab
warehouse.start();
```

You can use this method on arrays of `databricks.SQLWarehouse` objects to start
multiple SQL warehouses in one call.

#### Stop

Use this method to stop warehouses:

```matlab
warehouse.stop();
```

You can use this method on arrays of `databricks.SQLWarehouse` objects to stop
multiple SQL warehouses with one call.

#### Delete

This method is called [Delete](https://docs.databricks.com/api/workspace/warehouses/delete) in the Databricks API. It is called `remove`
here to avoid confusion with the built-in MATLAB `delete` method. This works
similarly to `start` and `stop`.

```matlab
warehouse.remove();
```

You can use this method on arrays of `databricks.SQLWarehouse` objects to delete multiple SQL warehouses with one call.

----
Copyright 2026 The MathWorks, Inc.
