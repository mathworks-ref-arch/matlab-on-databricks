# Import Repository into Databricks

This guide explains how to import the `matlab-on-databricks` repository into your Databricks workspace. Choose the method that matches your environment.

With internet acccess (recommended):

- [Use Databricks Git Folders](#use-databricks-git-folders)

Without internet access:

- [Manually Upload Repository](#manually-upload-repository).

## Use Databricks Git Folders

If you have internet access, MathWorks recommends using this method to import the repository into your Databricks workspace (requires Databricks Runtime 14.3 or above).

### Requirements

- Databricks Runtime 14.3 or above.

- Ensure that Databricks Git folders are enabled in your workspace (enabled by default). For details, see [Enable or Disable Databricks Git Folders (Databricks)](https://docs.databricks.com/aws/en/repos/enable-disable-repos-with-api).
- Ensure you have internet access to GitHub.

### Import Repository

1. Log in to your Databricks Workspace.

2. Click **Workspace** in the sidebar.
3. Navigate to your user folder (`Workspace/Users/<your-email>`).
4. Click **Create** > **Git folder**.
5. In the **Git Repository URL** field, enter `https://github.com/mathworks-ref-arch/matlab-on-databricks`.
6. In the **Git Provider** field, select **GitHub**.
7. Click **Create Git folder**.

## Manually Upload Repository

If you do not have internet access, use this method to upload the repository as a `.zip` file into your Databricks workspace.

### Requirements

Using a machine with internet access, download the repository as a `.zip` file:

- Using your browser, go to the repository: [MATLAB on Databricks (GitHub)](https://github.com/mathworks-ref-arch/matlab-on-databricks).

- Click **Code** > **Download ZIP**.

### Import Repository

1. Log in to your Databricks workspace.

2. Navigate to your user folder (`Workspace/Users/<your-email>`).
3. Click the three vertical dots, then click **Import**.
4. Select **Import from** > **File**.
5. Upload the repository `.zip` file.
6. Click **Import**. Databricks will automatically unzip the archive into a folder named `matlab-on-databricks-main`.

---------------
Copyright 2026 The MathWorks, Inc.
