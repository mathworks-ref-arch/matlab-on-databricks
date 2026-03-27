# Create a Cluster Policy for MATLAB Desktop on Databricks

This guide shows administrators how to configure a [Compute Policy (Databricks)](https://docs.databricks.com/aws/en/admin/clusters/policies#what-are-compute-policies) for running the MATLAB desktop on Databricks. The policy makes it simpler for your users to create a cluster with the required properties.

Use the policy in this guide as a template. Customize it as needed for your organization's standards, naming conventions, and security requirements. To edit a policy, you must have Databricks admin privileges.

Note: Your end users can see the details of a policy. Ensure that any Docker credentials you use in the policy allow read-only access to the image repository.

## Table of Contents

- [Build Policy](#build-policy)
- [Create Policy](#create-policy)
- [Example Policy](#example-policy)

## Build Policy

Build the policy JSON by combining:

- [Required Fields](#required-fields)
- [Docker Image Fields](#docker-image-fields)
- [Optional Fields](#optional-fields)

### Required Fields

These fields are required for every MATLAB Desktop cluster policy. They configure the cluster mode, Spark runtime, and Databricks Runtime version.

```json
{ 
  "docker_image.url": {
    "type": "fixed",
    "value": "<IMAGE_URL>"
  },
  "docker_image.basic_auth.username": {
    "type": "fixed",
    "value": "<USERNAME>"
  },
  "docker_image.basic_auth.password": {
    "type": "fixed",
    "value": "<PASSWORD_OR_TOKEN>"
  },
  "spark_env_vars.MW_INTERFACE_DIRECTORY_DEFAULT": {
    "type": "unlimited",
    "defaultValue": "/Volumes/main/default/myvolume/MathWorks"
  },
  "workload_type.clients.notebooks": {
    "type": "fixed",
    "value": true
  },
  "workload_type.clients.jobs": {
    "type": "fixed",
    "value": true
  },
  "data_security_mode": {
    "type": "unlimited",
    "defaultValue": "SINGLE_USER"
  },
  "autotermination_minutes": {
    "type": "unlimited",
    "defaultValue": 30
  },
  "spark_env_vars.MWI_SHUTDOWN_ON_IDLE_TIMEOUT": {
    "type": "unlimited",
    "defaultValue": "90"
  },
  "spark_conf.spark.databricks.cluster.profile": {
    "type": "unlimited",
    "defaultValue": "singleNode"
  },
  "spark_version": {
    "type": "allowlist",
    "values": [
      "17.3.x-scala2.13"
    ]
  },
  "num_workers": {
    "type": "unlimited",
    "defaultValue": 0
  },
  "runtime_engine": {
    "type": "unlimited",
    "defaultValue": "STANDARD"
  },
  "spark_conf.spark.databricks.unityCatalog.volumes.enabled": {
    "type": "fixed",
    "value": "true"
  },
  "spark_conf.spark.databricks.isv.product": {
    "type": "unlimited",
    "defaultValue": "MathWorks_MATLAB/25.2.0"
  },
  "custom_tags.ResourceClass": {
    "type": "unlimited",
    "defaultValue": "SingleNode"
  }
}
```

- Create a directory on a volume that your users can read but not write to. You use this directory to store some files later. In the field `spark_env_vars.MW_INTERFACE_DIRECTORY_DEFAULT`, replace `/Volumes/main/default/myvolume/MathWorks` with the actual path to the new directory you have created.

- For the field `spark_conf.spark.databricks.isv.product`, replace the value `MathWorks_MATLAB/25.2.0` with the MATLAB release and version of your choice. The format is `MathWorks_MATLAB/<Release_Year>.<Release_Number>.0`:
  - `<Release_Year>` is the 2-digit year of the MATLAB release.
  - `<Release_Number>` is the number of the MATLAB release.
  - The third number is always `0`.
  - For example, for MATLAB R2025b, the value is `MathWorks_MATLAB/25.2.0`.

### Docker Image Fields

The three Docker image keys are the same regardless of which container  registry you use. Only their values differ. Add the following block to your policy and fill in the values using the reference table that follows.

  ```json
  {
    "docker_image.url": {
      "type": "fixed",
      "value": "<IMAGE_URL>"
    },
    "docker_image.basic_auth.username": {
      "type": "fixed",
      "value": "<USERNAME>"
    },
    "docker_image.basic_auth.password": {
      "type": "fixed",
      "value": "<PASSWORD_OR_TOKEN>"
    }
  }
  ```

  **Values by Registry:**

  | Registry | `docker_image.url` | `docker_image.basic_auth.username` | `docker_image.basic_auth.password` |
  | --- | --- | --- | --- |
  | AWS ECR | `<aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>` | AWS | ECR authorization token from `aws ecr get-login-password`. Expires after 12 hours. Consider automating rotation. |
  | Azure ACR | `<registry>.azurecr.io/<repository>:<tag>` | ACR admin username or service principal client ID | ACR admin password or service principal secret. The principal should have the `acrpull` role. |
  | GitHub Container Registry (ghcr.io) | `ghcr.io/<owner>/<repository>:<tag>` | GitHub username | GitHub Personal Access Token (PAT) with `read:packages` scope. |
  | Docker Hub | `<username>/<repository>:<tag>` | Docker Hub username | Docker Hub password or access token. |

---

### Optional Fields

#### NLM Server Address

If your organization uses the Network License Manager, you can specify the address of the NLM server by adding the `spark_env_vars.MLM_LICENSE_FILE` field to your policy:

```json
"spark_env_vars.MLM_LICENSE_FILE": {
    "type": "unlimited",
    "defaultValue": "port@hostname"
  }
```

#### Auto-termination

MathWorks recommends you use this field to configure how long an idle MATLAB session keeps running on Databricks:

| Setting | Applies To | Description |
| --- | --- | --- |
| `MWI_SHUTDOWN_ON_IDLE_TIMEOUT` | MATLAB process | Shuts down MATLAB after the specified number of minutes elapse without user interaction or code execution. |
| `autotermination_minutes` | Spark cluster | Terminates the underlying cluster after the specified number of minutes elapse without a Spark command. |

MATLAB commands do not reset the cluster auto-termination timer, thus the auto-termination timer effectively starts counting from the moment MATLAB goes idle. The total time before all resources are released is:

```text
total idle time ≈ MWI_SHUTDOWN_ON_IDLE_TIMEOUT + autotermination_minutes
```

Databricks uses a default idle timeout of **120 minutes**. The defaults below split this budget so that MATLAB shuts down after 90 minutes of inactivity and the cluster is then terminated 30 minutes later:

```text
90 (MWI_SHUTDOWN_ON_IDLE_TIMEOUT) + 30 (autotermination_minutes) = 120 minutes
```

You can customize this budget to suit your users.

```json
{
  "autotermination_minutes": {
    "type": "unlimited",
    "defaultValue": 30
  },
  "spark_env_vars.MWI_SHUTDOWN_ON_IDLE_TIMEOUT": {
    "type": "unlimited",
    "defaultValue": "90"
  }
}
```

Note that:

- When a cluster times out, you lose any work that is not saved to persistent storage.

- Databricks sets auto-termination according to the last command you run on the cluster. This includes the commands you use to start and connect to MATLAB, any Spark API calls, and certain REST API commands issued from within MATLAB, but **not** general MATLAB commands.

- To avoid unnecessary charges, terminate or delete a cluster when no longer needed.

## Create Policy

1. In the left-hand sidebar of your Databricks workspace, click **Compute**.
2. Click the **Policies** tab.
3. Click **Create policy**.
4. Enter the suggested **Name** and **Description** for the policy in this example:

   - **Name**: `MATLAB Desktop R2025b, DBR 17.3`
   - **Description**: `MATLAB Desktop R2025b on a dedicated 17.3 Cluster supporting the optional installation of the MATLAB Interface for Databricks.`

5. Click the **JSON** tab, and paste your complete Policy JSON into the **Definition JSON** section.
6. Click **Create**.

## Example Policy

The following JSON combines all of the sections above using AWS ECR as the Docker registry. Use it as a reference when assembling your own policy.

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
    "value": "123456789.dkr.ecr.us-west-2.amazonaws.com/mathworks/matlab-on-databricks:R2025b"
  },
  "spark_env_vars.MW_INTERFACE_DIRECTORY_DEFAULT": {
    "type": "unlimited",
    "defaultValue": "/Volumes/main/default/myvolume/MathWorks"
  },
  "workload_type.clients.notebooks": {
    "type": "fixed",
    "value": true
  },
  "workload_type.clients.jobs": {
    "type": "fixed",
    "value": true
  },
  "data_security_mode": {
    "type": "unlimited",
    "defaultValue": "SINGLE_USER"
  },
  "autotermination_minutes": {
    "type": "unlimited",
    "defaultValue": 30
  },
  "spark_env_vars.MWI_SHUTDOWN_ON_IDLE_TIMEOUT": {
    "type": "unlimited",
    "defaultValue": "90"
  },
  "spark_conf.spark.databricks.cluster.profile": {
    "type": "unlimited",
    "defaultValue": "singleNode"
  },
  "num_workers": {
    "type": "unlimited",
    "defaultValue": 0
  },
  "runtime_engine": {
    "type": "unlimited",
    "defaultValue": "STANDARD"
  },
  "spark_conf.spark.databricks.unityCatalog.volumes.enabled": {
    "type": "fixed",
    "value": "true"
  },
  "spark_conf.spark.databricks.isv.product": {
    "type": "unlimited",
    "defaultValue": "MathWorks_MATLAB/25.2.0"
  },
  "custom_tags.ResourceClass": {
    "type": "unlimited",
    "defaultValue": "SingleNode"
  },
  "spark_version": {
    "type": "allowlist",
    "values": [
      "17.3.x-scala2.13"
    ]
  }
}
```

---

Copyright 2026 The MathWorks, Inc.
