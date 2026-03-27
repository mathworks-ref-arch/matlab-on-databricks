# Set Up MATLAB in Databricks

This guide shows administrators how to set up MATLAB&reg; in Databricks&reg; so your users can run MATLAB interactively in Databricks clusters. To request technical support, contact [databricks@mathworks.com](mailto:databricks@mathworks.com).

As an overview, you set up MATLAB using this workflow:

1. First, you build a custom Docker image. This image includes MATLAB as well as [MATLAB Proxy](https://github.com/mathworks/matlab-proxy), a package that allows your users to open MATLAB in a browser window.

2. Then you push the image to a container registry that you can access from your Databricks workspace.

3. Create compute policies so your users can easily create clusters configured for your organization.

4. Download the MATLAB Interface for Databricks package. This is optional but required if you want to enable all workflows for your users, such as scaling compiled MATLAB code.

## Requirements

- In your Databricks workspace, [Enable Container Services (Databricks)](https://docs.databricks.com/aws/en/compute/custom-containers#enable-container-services).

- Ensure you have access to a container registry such as ACR, ECR, or Docker Hub. To improve startup time and reduce network costs, ensure the registry is located in the same region as your Databricks workspace.

- If your organization uses Network License Manager to manage MATLAB licenses, follow the instructions to [Configure Network License Manager for Databricks](./configure-network-license-for-databricks.md).

    You can specify the address of the license manager for your users either in the MATLAB Dockerfile or in the compute policy you create. Otherwise your users can enter the address themselves when they start MATLAB for the first time. For details, see [Specify License Manager Address for MATLAB](./configure-network-license-for-databricks.md#specify-license-manager-address-for-matlab).

## Build the Docker Image

First, use the MATLAB [Dockerfile](/resources/dockerfiles/matlab/Dockerfile) in this repository to build an image containing MATLAB and [MATLAB Proxy (GitHub)](https://github.com/mathworks/matlab-proxy). This workflow supports MATLAB R2023b or later (with the exception of R2024b Update 8, which supports compiled MATLAB workflows but does not support running MATLAB interactively. For details, see the GitHub issue [MATLAB R2024b_U8 on MATLAB Proxy](https://github.com/mathworks/matlab-proxy/issues/88)).

1. Clone this repository.

    ```bash
    git clone https://github.com/mathworks-ref-arch/matlab-on-databricks
    cd matlab-on-databricks
    ```

2. Build the image. To customize the image, for example to install certain MATLAB toolboxes, you can modify the Dockerfile or build-time variables. For instructions, see [Customize the MATLAB Image](/resources/dockerfiles/matlab/README.md#customize-the-image).

    - To enable your users to scale compiled MATLAB code using Spark, you need to install MATLAB Compiler SDK.

    - To enable your users to use GPUs or MATLAB's in-built parallel computing, on a single node, you need to install Parallel Computing Toolbox.

    - You can specify the address to your network license manager by setting the environment variable `LICENSE_SERVER` in the Dockerfile.

    ```bash
    docker build -t matlab-on-databricks:R2025b -f resources/dockerfiles/matlab/Dockerfile .
    ```

## Push Image to Container Registry

Push the built image to your organization's container registry.

### Example: Azure Container Registry

```bash
az acr login --name <myRegistry>
docker tag matlab-on-databricks:R2025b <myRegistry>.azurecr.io/matlab-on-databricks:R2025b
docker push <myRegistry>.azurecr.io/matlab-on-databricks:R2025b
```

### Example: AWS Elastic Container Registry

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
docker tag matlab-on-databricks:R2025b <aws_account_id>.dkr.ecr.<region>.amazonaws.com/matlab-on-databricks:R2025b
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/matlab-on-databricks:R2025b
```

## Create Policy

To help your users create clusters that meet the requirements of your organization, create a compute policy. For instructions, see [Create Policy for MATLAB on Databricks](./create-cluster-policy-for-matlab-on-databricks.md).

Provide your users with the name of the policy you create, so they can select the policy when creating a cluster.

## Download MATLAB Interface for Databricks Package

If your users want to use workflows such as using Database Toolbox, using Spark, and scaling compiled MATLAB code on Databricks, they require a package called the MATLAB Interface for Databricks. (They do not need the package if they only want to run MATLAB interactively.)

You can either download the package for your users and store it on a volume from where they can install it, or they can download and install it themselves (which requires Internet access).

- To provide the package to your users, download it from [MATLAB Interface for Databricks (MathWorks)](https://www.mathworks.com/solutions/partners/databricks.html). Store the package at `<interface directory>/Versions/<Semantic Version Number>/filename.zip`, where `<interface directory>` is the directory you created and then specified in your policy using the `spark_env_vars.MW_INTERFACE_DIRECTORY_DEFAULT` field.

    Provide your users with the path to the package. They can install the package by following the instructions in [Run MATLAB Interactively on Databricks: Install MATLAB Interface for Databricks](../run-matlab-interactively-on-databricks.md#step-3-install-matlab-interface-for-databricks-package).

- Alternatively, your users can both download and install the package themselves by following the instructions in [Run MATLAB Interactively on Databricks: Install MATLAB Interface for Databricks](../run-matlab-interactively-on-databricks.md#step-3-install-matlab-interface-for-databricks-package).

## Next Steps

Now your users can:

- [Run MATLAB Interactively on Databricks](../run-matlab-interactively-on-databricks.md)
  - Access the MATLAB desktop in your web browser, running on a Databricks cluster.
  
  - Develop and debug algorithms interactively before scaling out.

- [Query Data in Databricks from MATLAB](../query-data-using-database-toolbox.md)
  - Run SQL queries on a Databricks cluster or SQL warehouse using Database Toolbox&trade;.

- [Scale MATLAB Workflows on Databricks](../scale-matlab-workflows-on-databricks.md)
  - Scale MATLAB code interactively on a single node using Parallel Computing Toolbox&trade;.

  - Perform Spark operations in MATLAB on a single node, for quick development and testing.

  - Combine Spark operations with compiled MATLAB or Simulink code for quick development in MATLAB, across multiple nodes.

  - Scale production workflows with compiled MATLAB or Simulink code for frequent and complex computations, across multiple nodes.

----
Copyright 2026 The MathWorks, Inc.
