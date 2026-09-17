# Instance Pool Creation

This guide helps administrators to configure an Instance Pool to support starting MATLAB on Databricks more quickly.

An Instance Pool is a set of zero or more, idle, ready-to-use instances that reduces cluster startup time. When you create a cluster from an Instance Pool, the cluster uses the idle instances instead of provisioning new instances, which significantly reduces startup time.

The Databricks Instance Pool UI currently does not support the creation of Instance Pools based on custom Docker images. However, this is fully supported by the underlying REST API. The sample MATLAB code and curl command below show how such a pool can be created. This requires administrative privileges.

While large production clusters may require dozens of nodes in an instance pool, even a single idle node can drastically cut startup times for single-node interactive desktop workloads.

```matlab
% Create a MATLAB cluster from a pool using a docker image:
ip = databricks.InstancePools;
cr = databricks.datastructures.instancepools.CreateRequest();
cr.instancePoolName = "MATLAB R2026a Desktop Dbx 17.3 Pool";
settings = databricks.internal.settings.Settings.getSettingsStruct();
vendor = matlab.databricks.vendor.getVendorFromAPI();
cr.nodeTypeId = settings.(vendor).node_type_id;
cr.minIdleInstances = 2;
di = databricks.datastructures.instancepools.DockerImage(fileread(databricksRoot("config", "dockerAuth.json")));
cr.preloadedDockerImages = di;
% Make sure the Spark version coincides with the Databricks Runtime version in the docker image
cr.preloadedSparkVersions = "17.3.x-scala2.13";
[poolId, errorResponse] = ip.create(cr)
```

If using an alternative approach the following sample `curl` command show the
core required values:

```bash
curl --header "Content-Type: application/json" \
  --header "Authorization: Bearer _REDACTED_Token" \
  --header "User-Agent: MathWorks_MATLAB/26.1.0" \
  --request POST \
  --data '{"instance_pool_name":"MATLAB R2026a Desktop Dbx 17.3 Pool","min_idle_instances":2,"node_type_id":"Standard_D4ds_v5","preloaded_docker_images":[{"url":"myregistry.azurecr.io/matlab/databricks/desktop:r2026a-dbx17.3","basic_auth":{"username":"REDACTED","password":"REDACTED"}}],"preloaded_spark_versions":["17.3.x-scala2.13"]}' \
  "https://adb-123456789012345.1.azuredatabricks.net/api/2.0/instance-pools/create"
```

## Tips

* When using `cmd.exe` on Windows escape the JSON double quotes with backslashes when using `curl`, alternatively use PowerShell for simpler parsing.

* For desktop workloads, keeping a pool active only during business hours will reduce costs.

* As instance pool creation and deletion is typically infrequent, it may prove simpler to keep the initial creation API call relatively simple and then later adjust the resulting pool properties using the Workspace UI.
