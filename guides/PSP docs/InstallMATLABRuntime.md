# Install MATLAB Runtime on Databricks Cluster

This guide shows how to install MATLAB&reg; Runtime on a Databricks cluster. Your users require MATLAB Runtime to scale compiled MATLAB code for these workflows:

- [Use Spark with Compiled MATLAB Code](./PSP%20docs/SparkWithCompiledMATLAB.md).

- [Scale Compiled MATLAB Code for Production Workflows](./PSP%20docs/ScaleCompilerSDK.md).

## Table of Contents

- [Requirements](#requirements)
- [Build and Push Docker Image](#build-and-push-docker-image)
- [Create Cluster Policy for MATLAB Runtime](#create-cluster-policy-for-matlab-runtime-on-databricks)
  - [Build Policy](#build-policy)
  - [Create Policy](#create-policy)

## Requirements

- In your Databricks workspace, [Enable Container Services (Databricks)](https://docs.databricks.com/aws/en/compute/custom-containers#enable-container-services).

- Ensure you have access to a container registry such as ACR, ECR, or Docker Hub. To improve startup time and reduce network costs, ensure the registry is located in the same data center as your Databricks workspace.

## Build and Push Docker Image

Use the MATLAB Runtime [Dockerfile](/resources/dockerfiles/runtime/Dockerfile) in this repository to build a Docker image for MATLAB Runtime R2025b. To request help with creating a custom image, contact [databricks@mathworks.com](mailto:databricks@mathworks.com).

For example:

```bash
docker build -t myregistry.azurecr.io/mathworks/matlabruntimer2025b_17-3 -f ./output/Dockerfile.R2025b-17.3 .
```

Then push the built image to your organization's container registry.

## Create Cluster Policy for MATLAB Runtime on Databricks

Next, create a [Compute Policy (Databricks)](https://docs.databricks.com/aws/en/admin/clusters/policies#what-are-compute-policies) for running MATLAB Runtime on Databricks. The policy makes it simpler for your users to create a cluster with the required properties.

Use the policy in this guide as a template. Customize it as needed for your organization's standards, naming conventions, and security requirements. To edit a policy, you must have Databricks admin privileges.

Your end users can see the details of a policy. Ensure that any Docker credentials you use in the policy allow read-only access to the image repository.

When you use MATLAB Runtime, the release must match that of the MATLAB Desktop you use to build your compiled MATLAB or Simulink code. Thus, over time it is normal to have multiple Docker images, with different combinations of MATLAB Runtime versions and Databricks runtime versions. Each image requires its own policy that your users can easily access.

### Build Policy

This is an example policy for MATLAB Runtime R2025b and Databricks runtime 17. See the list that follows for details on which fields you must update so you can use the policy.

```json
{
  "docker_image.basic_auth.password": {
    "type": "fixed",
    "value": "ey[REDACTED]MxfQ=="
  },
  "docker_image.basic_auth.username": {
    "type": "fixed",
    "value": "AWS"
  },
  "docker_image.url": {
    "type": "fixed",
    "value": "123456789.dkr.ecr.us-west-2.amazonaws.com/matlab/databricks/runtime:r2025b-dbx17.3"
  },
  "spark_env_vars.MW_INTERFACE_DIRECTORY_DEFAULT": {
    "type": "unlimited",
    "defaultValue": "/Volumes/main/default/myvolume/MathWorks"
  },
  "spark_env_vars.LD_LIBRARY_PATH": {
    "type": "unlimited",
    "defaultValue": "/MATLAB_Runtime/runtime/glnxa64:/MATLAB_Runtime/bin/glnxa64:/MATLAB_Runtime/sys/os/glnxa64:/MATLAB_Runtime/sys/opengl/lib/glnxa64:/MATLAB_Runtime/extern/bin/glnxa64"
  },
  "spark_env_vars.MW_RUNTIME_RELEASE": {
    "type": "unlimited",
    "value": "R2025b"
  },
  "spark_conf.spark.databricks.isv.product": {
    "type": "unlimited",
    "defaultValue": "MathWorks_MATLAB/25.2.0"
  },
  "spark_version":{
    "type":"allowlist",
    "values":[
    "17.3.x-scala2.13"
    ]
  },
  "data_security_mode": {
    "type": "fixed",
    "value": "SINGLE_USER"
  },
  "spark_conf.spark.databricks.unityCatalog.volumes.enabled": {
    "type": "unlimited",
    "defaultValue": "true"
  },
  "autotermination_minutes": {
    "type": "unlimited",
    "defaultValue": 30
  }
}
```

- Set the value of `spark_env_vars.MW_INTERFACE_DIRECTORY_DEFAULT` to the path of the interface directory you created when you previously followed the instructions to [Create a Cluster Policy for MATLAB Desktop on Databricks](/guides/admin/create-cluster-policy-for-matlab-on-databricks.md#).

- Set the value of `spark_env_vars.MW_RUNTIME_RELEASE` to your MATLAB Release.

- For the field `spark_conf.spark.databricks.isv.product`, replace the value `MathWorks_MATLAB/25.2.0` with the MATLAB release and version of your choice. The format is `MathWorks_MATLAB_Runtime/<Release_Year>.<Release_Number>.0`:
  - `<Release_Year>` is the 2-digit year of the MATLAB release.
  - `<Release_Number>` is the number of the MATLAB release.
  - The third number is always `0`.
  - For example, for MATLAB R2025b, the value is `MathWorks_MATLAB_Runtime/25.2.0`.

- In the `spark_version` field, specify your Spark version. To find this value, navigate in Databricks to **Compute > Create compute**. Click the **Databricks runtime** dropdown to see the Spark version for your Databricks runtime.

- The three Docker image keys are the same regardless of which container registry you use. Only their values differ. Specify the values using the reference table that follows.

**Values by Registry:**

| Registry | `docker_image.url` | `docker_image.basic_auth.username` | `docker_image.basic_auth.password` |
| --- | --- | --- | --- |
| AWS ECR | `<aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>` | AWS | ECR authorization token from `aws ecr get-login-password`. Expires after 12 hours. Consider automating rotation. |
| Azure ACR | `<registry>.azurecr.io/<repository>:<tag>` | ACR admin username or service principal client ID | ACR admin password or service principal secret. The principal should have the `acrpull` role. |
| GitHub Container Registry (ghcr.io) | `ghcr.io/<owner>/<repository>:<tag>` | GitHub username | GitHub Personal Access Token (PAT) with `read:packages` scope. |
| Docker Hub | `<username>/<repository>:<tag>` | Docker Hub username | Docker Hub password or access token. |

### Create Policy

1. In the left-hand sidebar of your Databricks workspace, click **Compute**.
2. Click the **Policies** tab.
3. Click **Create policy**.
4. Enter the suggested **Name** and **Description** for the policy in this example:

   - **Name**: `MATLAB Runtime R2025b, DBR 17.3`
   - **Description**: `MATLAB Runtime R2025b on a dedicated 17.3 Cluster.`

5. Click the **JSON** tab, and paste the Policy JSON you created earlier into the **Definition JSON** section.
6. Click **Create**.

Provide your users with the name of the policy you create, so they can select the policy when creating a cluster.

---
Copyright 2026 The MathWorks, Inc.
