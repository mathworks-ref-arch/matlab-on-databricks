from pathlib import Path

import ipywidgets as widgets
from IPython.display import display

from . import dbx, diagnostics, dsp, matlab, matlab_proxy, mpm, version, web


def get():
    parent_widget = widgets.VBox()

    def display_widget(widget):
        parent_widget.children = parent_widget.children + (widget,)

    ## Set CSS
    style = widgets.HTML("""
    <style>
    .widget-button {
        font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Noto Sans", Arial, "Helvetica Neue", Helvetica, lucida, sans-serif; !important
        font_size: 12px !important;
        font-weight: normal !important;
        border-radius: 4px !important;
        justify-content: center !important;
    }
    .widget-text {
        font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Noto Sans", Arial, "Helvetica Neue", Helvetica, lucida, sans-serif; !important
        font_size: 12px !important;
        font-weight: normal;
        color: #212121;
    }
    .widget-label {
        font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Noto Sans", Arial, "Helvetica Neue", Helvetica, lucida, sans-serif; !important
        font_size: 12px !important;
        line-height: 17px !important;
        font-weight: normal;
        color: #212121;
        white-space: normal !important;
        height: auto !important;
    }

    .widget-select select {
        border: 1px solid lightgrey !important;
    }

    .widget-text input {
        border: 1px solid lightgrey !important;
        color: #212121 !important;
    }

    .paragraph {
        line-height: 17px !important;
    }

    /* Style accordion headers */
    .widget-accordion .widget-accordion-header {
        font-weight: bold !important;
        font-size: 14px !important;
    }

    /* Widget button color white */
    .dbx-button-text-white {
        color: white;
    }

    /* Widget button color light blue */
    .dbx-button-text-light-blue {
        color: #0076a8;
    }

    /* Button styled as hyperlink - matches link color in both light and dark themes */
    .dbx-button-as-link {
        color: -webkit-link !important;
        cursor: pointer !important;
        text-decoration: underline !important;
    }

    /* Margin top - Medium */
    .margin-top-md {
        margin-top: 34px;
    }

    /* Resize the box horizontally and vertically, vertical resize is limited to 100% to avoid double scrollbar condition */
    .resize-box-both {
        resize: both;
        max-width: 100%;
    }

    /* Wrapping text in logs */
    .resize-box-both pre {
        white-space: pre-wrap;   /* wraps text but preserves intentional whitespace/newlines */
        word-break: break-word;  /* breaks long unbreakable strings (e.g. long paths, URLs) */
    }
    </style>
    """)
    ### Load the style
    display_widget(style)

    ## Section Header : Title
    title_html = widgets.HBox(
        [
            widgets.HTML("""
            <style>
                h1 {
                    font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Noto Sans", Arial, "Helvetica Neue", Helvetica, lucida, sans-serif;
                    font-size: 24px;
                    font-weight: normal;
                    color: #C04C0B;
                }
            </style>
            <div style="display: flex; align-items: center; justify-content: center; padding: 0px;">
                <h1>Connect to MATLAB</h1>
            </div>
            """)
        ],
        layout=widgets.Layout(
            width="100%",
            align_items="flex-start",
        ),
    )

    ## Username  | Cluster Name | Cluster ID
    username_text = widgets.Text(
        description="User Name",
        value=dbx.current_user_name(),
        style={"description_width": "initial"},
        required=True,
        layout={"width": "100%"},
    )

    username_hbox = widgets.HBox(
        [username_text],
        layout=widgets.Layout(
            flex="1 1 0",
            min_width="480px",
            box_sizing="border-box",
            margin="0 48px 24px 0",
        ),
    )

    def _get_window_open_command(url: str) -> str:
        return f"window.open('{url}', '_blank');"

    def get_username():
        return username_text.value

    clustername_label = widgets.Label("Cluster:")

    clustername_html = widgets.HTML(
        value="Unavailable",
        style={"description_width": "initial", "text_color": "#616161"},
    )
    clustername_valid_button = widgets.Valid(
        value=False, layout=widgets.Layout(flex="0 0 auto", width="24px")
    )

    clustername_hbox = widgets.HBox(
        [clustername_label, clustername_html, clustername_valid_button],
        layout=widgets.Layout(
            flex="1 1 0",
            min_width="480px",
            box_sizing="border-box",
            margin="0 48px 24px 0",
            align_items="baseline",
        ),
    )

    clusterid_label = widgets.Label("Cluster ID:")

    clusterid_html = widgets.HTML(
        value=dbx.get_cluster_id(),
        style={"description_width": "initial", "text_color": "#616161"},
    )

    psp_version_label = widgets.Label("MATLAB Interface for Databricks:")
    psp_installed_version = dsp.read_installed_version(username=get_username())

    if psp_installed_version:
        # If the DSP is already installed, show the installed version.
        psp_version_html = widgets.HTML(
            value=psp_installed_version,
            style={"description_width": "initial", "text_color": "#616161"},
        )
        psp_version_hbox = widgets.HBox(
            [psp_version_label, psp_version_html],
            layout=widgets.Layout(
                flex="1 1 0",
                min_width="480px",
                box_sizing="border-box",
                margin="0 48px 24px 0",
                align_items="baseline",
            ),
        )
    else:
        # Show a message with a button to direct users to the installation instructions.
        psp_version_html = widgets.HTML(
            value="Not installed, click ",
            style={"description_width": "initial", "text_color": "#616161"},
        )

        click_to_install_button = widgets.Button(
            description="here",
            style={"button_color": "white"},
            layout=widgets.Layout(width="auto", height="24px", padding="0px 0px"),
        )
        click_to_install_button.add_class("dbx-button-as-link")

        psp_version_html_suffix = widgets.HTML(
            value=" for installation instructions.",
            style={"description_width": "initial", "text_color": "#616161"},
        )

        psp_version_hbox = widgets.HBox(
            [
                psp_version_label,
                psp_version_html,
                click_to_install_button,
                psp_version_html_suffix,
            ],
            layout=widgets.Layout(
                flex="1 1 0",
                min_width="480px",
                box_sizing="border-box",
                margin="0 48px 24px 0",
                align_items="baseline",
            ),
        )

        def open_matlab_interface_accordion(b):
            configuration_accordion.selected_index = 1

        click_to_install_button.on_click(open_matlab_interface_accordion)

    clusterid_hbox = widgets.HBox(
        [clusterid_label, clusterid_html],
        layout=widgets.Layout(
            flex="1 1 0",
            min_width="480px",
            box_sizing="border-box",
            margin="0 48px 24px 0",
            align_items="baseline",
        ),
    )

    connect_matlab_button = widgets.Button(
        description="Connect",
        style={"button_color": "#008013"},
        icon="play",
    )

    connect_matlab_button.add_class("dbx-button-text-white")

    stop_matlab_button = widgets.Button(
        description="Stop",
        style={"button_color": "#B7312C"},
        icon="stop",
    )

    stop_matlab_button.add_class("dbx-button-text-white")

    start_matlab_button = widgets.Button(
        description="Add",
        style={"button_color": "#0076a8"},
        icon="plus",
    )

    start_matlab_button.add_class("dbx-button-text-white")
    start_matlab_button.add_class("margin-top-md")

    sessions_buttons_vbox = widgets.VBox(
        [
            start_matlab_button,
            connect_matlab_button,
            stop_matlab_button,
        ],
        layout=widgets.Layout(align_items="center", min_width="160px"),
    )

    context = dbx.get_context()
    cluster_name = dbx.get_cluster_name()
    if not cluster_name:
        clustername_html.value = "Serverless"
        box_upper_row1 = widgets.HBox(
            [username_hbox, clustername_hbox, clusterid_hbox],
            layout=widgets.Layout(
                display="flex",
                flex_flow="row wrap",  # side-by-side when wide, stacked when narrow
                width="100%",
                align_items="flex-start",
            ),
        )

        box_upper = widgets.Box(
            [title_html, box_upper_row1],
            layout=widgets.Layout(
                display="flex",
                flex_flow="row wrap",
                width="100%",
                align_items="flex-start",
            ),
        )
        display_widget(box_upper)
    else:
        # Proceed with building the rest of the app only if we are in a valid cluster.
        clustername_html.value = cluster_name
        clustername_valid_button.value = True

        ## Create data for Access Tab
        app_outputs = widgets.Output()
        app_outputs.append_stdout("...")
        logs_label = widgets.HTML(value="<b>Log</b>")

        available_matlab_sessions_selectmultiple = widgets.SelectMultiple(
            options=matlab_proxy.list_servers_ports(username=get_username()),
            rows=10,
            disabled=False,
            layout={"width": "auto", "height": "160px", "border": ""},
        )
        available_matlab_sessions_label = widgets.HTML(
            value="<b>Available MATLAB Sessions</b>"
        )
        refresh_matlab_button = widgets.Button(
            description="Refresh",
            style={"button_color": "white"},
            icon="refresh",
            layout=widgets.Layout(width="auto", border="", justify_content="flex-end"),
        )
        refresh_matlab_button.add_class("dbx-button-text-light-blue")

        clear_outputs_button = widgets.Button(
            description="Clear",
            style={"button_color": "white"},
            icon="times",
            layout=widgets.Layout(width="auto", border="", justify_content="flex-end"),
        )
        clear_outputs_button.add_class("dbx-button-text-light-blue")

        available_matlab_sessions_vbox = widgets.VBox(
            [
                widgets.HBox(
                    [available_matlab_sessions_label, refresh_matlab_button],
                    layout=widgets.Layout(justify_content="space-between"),
                ),
                available_matlab_sessions_selectmultiple,
            ],
            layout=widgets.Layout(flex="1 1 auto", width="100%"),
        )

        available_matlab_sessions_hbox = widgets.HBox(
            [available_matlab_sessions_vbox, sessions_buttons_vbox],
            layout=widgets.Layout(
                flex="1 1 0",
                min_width="480px",
                box_sizing="border-box",
                margin="0 48px 24px 0",
            ),
        )

        logs_hbox = widgets.HBox(
            [logs_label, clear_outputs_button],
            layout={"justify_content": "space-between"},
        )
        app_outputs_box = widgets.Box(
            [app_outputs],
            layout=widgets.Layout(
                width="100%",
                height="160px",
                box_sizing="border-box",
                overflow="auto",
                border="1px solid lightgrey",
            ),
        )
        app_outputs_box.add_class("resize-box-both")

        logs_vbox = widgets.VBox(
            [logs_hbox, app_outputs_box],
            layout=widgets.Layout(
                flex="1 1 0",
                min_width="480px",
                box_sizing="border-box",
                margin="0 48px 24px 0",
            ),
        )

        box_upper_row1 = widgets.HBox(
            [username_hbox, clustername_hbox, clusterid_hbox, psp_version_hbox],
            layout=widgets.Layout(
                display="flex",
                flex_flow="row wrap",  # side-by-side when wide, stacked when narrow
                width="100%",
                align_items="flex-start",
            ),
        )

        box_upper_row2 = widgets.HBox(
            [
                available_matlab_sessions_hbox,
                logs_vbox,
            ],
            layout=widgets.Layout(
                display="flex",
                flex_flow="row wrap",  # side-by-side when wide, stacked when narrow
                width="100%",
                align_items="flex-start",
            ),
        )

        box_upper = widgets.Box(
            [title_html, box_upper_row1, box_upper_row2],
            layout=widgets.Layout(
                display="flex",
                flex_flow="row wrap",
                width="100%",
                align_items="flex-start",
            ),
        )

        ## Begin footer

        configuration_label = widgets.HTML(
            "<b>Configuration</b>", layout=widgets.Layout(justify_content="flex-start")
        )

        matlabroot_query_result = matlab.root()
        if not matlabroot_query_result:
            matlabroot_query_result = "MATLAB not on PATH"
        matlabroot_text = widgets.HBox(
            [
                widgets.HTML(value="Root Directory:"),
                widgets.HTML(
                    value=f"<span style='color: #616161;'>{matlabroot_query_result}</span>",
                ),
            ],
        )
        matlab_version_text = widgets.HBox(
            [
                widgets.HTML(value="Version:"),
                widgets.HTML(
                    value=f"<span style='color: #616161;'>{matlab.version()}</span>",
                ),
            ],
        )

        DATABRICKS_CLUSTER_AUTO_TERMINATION_MINUTES = (
            dbx.cluster_autotermination_minutes()
        )
        # Settings related to idle timeout for MATLAB session
        idle_timeout_checkbox = widgets.Checkbox(
            value=True if DATABRICKS_CLUSTER_AUTO_TERMINATION_MINUTES else False,
            indent=False,
            layout=widgets.Layout(width="auto", margin="10px 0 0 0"),
        )
        idle_timeout_textbox = widgets.BoundedIntText(
            value=DATABRICKS_CLUSTER_AUTO_TERMINATION_MINUTES,
            min=1,
            max=14400,  # 10 days in minutes
            step=1,
            disabled=False if DATABRICKS_CLUSTER_AUTO_TERMINATION_MINUTES else True,
            layout=widgets.Layout(width="50px", margin="0 10px 0 10px"),
        )

        # Add event handler to enable/disable textbox based on checkbox state
        def on_checkbox_change(change):
            idle_timeout_textbox.disabled = not change["new"]

        idle_timeout_checkbox.observe(on_checkbox_change, names="value")
        # TODO: update doc link to section in notebook README that describes this feature\n",

        info_icon = widgets.HTML(
            value="""
        <a href="https://github.com/mathworks/matlab-proxy/blob/main/Advanced-Usage.md#shutdown-on-idle" target="_blank" style="text-decoration: none;">
            <i class="fa fa-question-circle" style="font-size: 20px; color: #1f77b4; cursor: pointer;"></i>
        </a>
        """,
            description="",
            layout=widgets.Layout(margin="5px 0 0 5px"),
        )

        idle_timeout_hbox = widgets.HBox(
            [
                idle_timeout_checkbox,
                widgets.HTML(value="Terminate MATLAB after"),
                idle_timeout_textbox,
                widgets.HTML(value="minutes of inactivity"),
                info_icon,
            ],
            layout=widgets.Layout(align_items="flex-start"),
        )

        configuration_vbox = widgets.VBox(
            [
                configuration_label,
                matlab_version_text,
                matlabroot_text,
                idle_timeout_hbox,
            ],
            layout=widgets.Layout(
                margin="0 48px 24px 0",
                height="auto",
                flex="1 1 320px",  # base width
                min_width="320px",
            ),
        )
        installed_toolboxes_label = widgets.HTML(
            value="<b>Installed Toolboxes</b>",
            layout=widgets.Layout(justify_content="flex-start"),
        )

        installed_toolboxes = matlab.installed_toolboxes(username=get_username())

        installed_toolboxes_list = [
            widgets.Label(
                value=toolbox_name,
                layout=widgets.Layout(height="auto", flex="0 0 auto"),
            )
            for toolbox_name in installed_toolboxes
        ]

        installed_toolboxes_inner_vbox = widgets.VBox(
            children=installed_toolboxes_list,
            layout=widgets.Layout(
                width="100%",
                height="160px",
                border="1px solid lightgrey",
                margin="0 0 0 0",
            ),
        )
        installed_toolboxes_vbox = widgets.VBox(
            [
                installed_toolboxes_label,
                widgets.HTML(
                    value="<span style='color: #616161;'>Add a new MATLAB session to access recently installed toolboxes.</span>",
                    layout=widgets.Layout(margin="0 0 8px 0"),
                ),
                installed_toolboxes_inner_vbox,
            ],
            layout=widgets.Layout(
                margin="0 48px 24px 0",
                # width = "100%",
                flex="1 1 320px",  # base width
                min_width="320px",
            ),
        )

        matlab_interface_for_databricks_description_html_content = """
        <div class="paragraph">Install the MATLAB Interface for Databricks to use these workflows:
        <ul>
            <li>Use SQL to work with data in Databricks</li>
            <li>Work with Spark&trade; interactively in MATLAB</li>
            <li>Scale compiled MATLAB algorithms on Databricks</li>
            <li>Share MATLAB algorithms with other Databricks users working with Python&reg;</li>
        </ul>
        To install the Interface for Databricks, you can either download the latest version, or provide the full path to the zip file, if it already in your volume.
        </div>
        <br>
        """

        matlab_interface_for_databricks_description_html = widgets.HTML(
            value=matlab_interface_for_databricks_description_html_content
        )

        __DATABRICKS_SUPPORT_PACKAGE_DOWNLOAD_URL = "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/products/reference-architectures/matlab-databricks-latest.zip"
        __MATLAB_INTERFACE_LEARN_MORE_BUTTON_URL = (
            "https://www.mathworks.com/solutions/partners/databricks.html"
        )
        install_databricks_support_package_button = widgets.Button(
            description="Install",
            style={"button_color": "#015418"},
            icon="plus",
            disabled=True,
        )
        install_databricks_support_package_button.add_class("dbx-button-text-white")

        installed_version = dsp.read_installed_version(get_username())
        if installed_version:
            _initial_status = f"<span style='color: #616161;'>Version {installed_version} installed.</span>"
        else:
            _initial_status = ""
        support_package_status_html = widgets.HTML(value=_initial_status)

        @app_outputs.capture(clear_output=True)
        def enable_support_package_install_button(change):
            _databricks_support_package_location = change.new
            if (_databricks_support_package_location).endswith(".zip"):
                # verify that this path is valid
                file_path = Path(_databricks_support_package_location)
                if file_path.is_file():
                    try:
                        # get version of the support package
                        version_number = dsp.read_version_from_zip(
                            zip_file_path=file_path
                        )
                        if installed_version and installed_version == version_number:
                            support_package_status_html.value = f"<span style='color: #616161;'>Version {installed_version} is already installed. Click Install to reinstall.</span>"
                        elif installed_version:
                            support_package_status_html.value = f"<span style='color: #616161;'>Version {installed_version} installed. Click Install to update to version {version_number}.</span>"
                        else:
                            support_package_status_html.value = f"<span style='color: #616161;'>Version {version_number} ready to install.</span>"

                        install_databricks_support_package_button.disabled = False
                    except Exception as e:
                        support_package_status_html.value = f"<span style='color: #616161;'> &#10060; Error reading zip file: {str(e)}</span>"
                        install_databricks_support_package_button.disabled = True
                else:
                    print(f"{_databricks_support_package_location} : File not found.")
                    install_databricks_support_package_button.disabled = True

        resolved_dsp_path, resolved_dsp_error = (
            dsp.resolve_latest_dsp_from_interface_directory()
        )
        if resolved_dsp_error:
            app_outputs.append_stdout(f"\n{resolved_dsp_error}")

        databricks_support_package_location = widgets.Text(
            value=resolved_dsp_path,
            placeholder="Full path to zip file",
            disabled=False,
            layout=widgets.Layout(flex="6 1 auto", width="auto", margin="0 0 0 10px"),
        )

        databricks_support_package_location.observe(
            enable_support_package_install_button, names="value"
        )
        if resolved_dsp_path:
            enable_support_package_install_button(
                type("Change", (), {"new": resolved_dsp_path})()
            )

        databricks_support_package_location_hbox = widgets.HBox(
            [
                widgets.HTML(
                    value="Install Location:",
                    layout=widgets.Layout(flex="1 1 auto", width="auto"),
                ),
                databricks_support_package_location,
            ],
            layout=widgets.Layout(
                display="flex", flex_flow="row", align_items="stretch", width="100%"
            ),
        )
        download_status_html = widgets.HTML(
            value="<span style='color: #616161;'>Click to download from MathWorks</span>"
        )

        def _is_download_location_unreachable():
            if diagnostics.check_internet_connection(
                __DATABRICKS_SUPPORT_PACKAGE_DOWNLOAD_URL, timeout=0.5
            ):
                # has access to internet, set disabled to False
                return False
            else:
                download_status_html.value = "<span style='color: #616161;'>❌ Need internet access to download.</span>"
                return True

        databricks_support_package_download_button = widgets.Button(
            description="Download",
            style={"button_color": "#0076a8"},
            icon="download",
            disabled=_is_download_location_unreachable(),
        )
        databricks_support_package_download_button.add_class("dbx-button-text-white")

        matlab_interface_learn_more_button_html = f"""<button style="background: none; border: none; outline: none; cursor: pointer;"  onclick="{_get_window_open_command(__MATLAB_INTERFACE_LEARN_MORE_BUTTON_URL)};"><i style="font-size:18px;color:#0076a8;" class="fa">&#xf059;</i></button>"""
        matlab_interface_learn_more_button = widgets.HTML(
            matlab_interface_learn_more_button_html
        )

        @app_outputs.capture(clear_output=True)
        def install_databricks_support_package(b):
            # Disable UI while installation is in progress.
            install_databricks_support_package_button.disabled = True
            databricks_support_package_download_button.disabled = True
            databricks_support_package_location.disabled = True
            support_package_status_html.value = (
                "<span style='color: #616161;'>&#9203; Installing...</span>"
            )

            zip_file_path = databricks_support_package_location.value

            print("Installing Databricks Support Package\n")
            print(f"Unzipping from: {zip_file_path}")
            dsp.unzip(username=get_username(), zip_file_path=zip_file_path)
            print("Installation complete.")
            print(
                "The Databricks support package will be available from your next MATLAB session."
            )
            refresh_installed_toolboxes()

            nonlocal installed_version
            installed_version = dsp.read_installed_version(get_username())
            new_session_message = "<br><span style='color: #F57C00; font-size: 12px;'>Add a new session to open MATLAB with the newly installed version.</span>"
            if installed_version:
                support_package_status_html.value = f"<span style='color: #616161;'>&#9989; Version {installed_version} installed successfully.</span>{new_session_message}"
            else:
                support_package_status_html.value = f"<span style='color: #616161;'>&#9989; Installed successfully.</span>{new_session_message}"

            # Restore UI state after installation is complete.
            install_databricks_support_package_button.disabled = False
            databricks_support_package_download_button.disabled = False
            databricks_support_package_location.disabled = False

            # Update the installed version in the UI
            if installed_version:
                psp_version_html.value = installed_version
                # Remove the button and suffix
                psp_version_hbox.children = [psp_version_label, psp_version_html]

        matlab_interface_for_databricks_vbox = widgets.VBox(
            [
                widgets.HBox(
                    [
                        matlab_interface_for_databricks_description_html,
                        matlab_interface_learn_more_button,
                    ]
                ),
                widgets.VBox(
                    [
                        databricks_support_package_download_button,
                        download_status_html,
                    ],
                    layout=widgets.Layout(margin="0 0 8px 0"),
                ),
                databricks_support_package_location_hbox,
                install_databricks_support_package_button,
                support_package_status_html,
            ]
        )

        mpm_input_file_help_html = widgets.HTML(
            value="<span style='color: #616161;'>Upload an <a href='https://www.mathworks.com/help/install/ug/mpminstall.html#mw_62b735b4-6bfe-4369-a649-d8faebb0f0d7'>mpm_input.txt</a> file with toolboxes to install.</span>",
            layout=widgets.Layout(white_space="normal", margin="0 0 8px 0"),
        )

        input_file_uploader = widgets.FileUpload(
            accept=".txt",
            multiple=False,
            description="Upload",
            style={"button_color": "#0076a8"},
            layout=widgets.Layout(),
        )
        input_file_uploader.add_class("dbx-button-text-white")

        # Disable button if MPM is not on path.
        if not mpm.exists():
            input_file_uploader.disabled = True
            mpm_input_file_help_html.value += "</br><span style='color: #616161;'>❌ MATLAB Package Manager is not available.</br><a href='https://www.mathworks.com/help/install/ug/get-mpm-os-command-line.html'>See here for installation steps</a> and reload widget.</span>"

        toolboxes_install_button = widgets.Button(
            description="Install",
            disabled=True,
            style={"button_color": "#015418"},
            icon="plus",
            layout=widgets.Layout(border="1px solid #0076a8"),
        )
        toolboxes_install_button.add_class("dbx-button-text-white")

        def _reset_file_uploader_state():
            toolboxes_install_button.disabled = True
            try:
                # Un-observe the file uploader to prevent triggering on_file_upload when we reset its value.
                input_file_uploader.unobserve(on_file_upload, names="value")
                input_file_uploader.value.clear()  # clear saved value in memory
                input_file_uploader._counter = 0  # resets the UI counter
            finally:
                input_file_uploader.observe(on_file_upload, names="value")

        mpm_context = {"input_file_path": ""}

        @app_outputs.capture(clear_output=True)
        def on_file_upload(change):
            uploaded_files = change["new"]
            if not uploaded_files:
                print("No file selected")
                _reset_file_uploader_state()
                return

            try:
                # Get the first uploaded file
                uploaded_file = list(uploaded_files.values())[0]

                saved_file_path = mpm.save_file(uploaded_file)
                mpm_context["input_file_path"] = saved_file_path
                toolboxes_install_button.disabled = False
                print("File upload successful. Click Install to proceed.")

            except Exception as e:
                print(f"Exception: {str(e)}")
                _reset_file_uploader_state()

        @app_outputs.capture(clear_output=True)
        def install_toolboxes_using_mpm(button):
            toolboxes_install_button.disabled = True
            input_file_uploader.disabled = True
            input_file_uploader._counter = 0  # resets the UI counter

            try:
                input_file_path = mpm_context.get("input_file_path", "")
                print("Toolbox installation started")
                print(
                    f"Installing toolboxes using mpm with input file as :{input_file_path}"
                )
                for line in mpm.install(input_file_path):
                    print(line)
                print("-" * 45)
                print("Toolbox installation completed successfully.")
                refresh_installed_toolboxes()
            except Exception as e:
                print(f"Toolbox installation failed: {str(e)}")
                _reset_file_uploader_state()
            finally:
                input_file_uploader.disabled = False

        input_file_uploader.observe(on_file_upload, names="value")

        toolboxes_install_button.on_click(install_toolboxes_using_mpm)

        additional_toolboxes_vbox = widgets.VBox(
            [
                widgets.HTML(
                    value="<b>Install Additional MathWorks Toolboxes</b>",
                    layout=widgets.Layout(justify_content="flex-start"),
                ),
                mpm_input_file_help_html,
                widgets.HBox(
                    [
                        input_file_uploader,
                        toolboxes_install_button,
                    ]
                ),
            ],
            layout=widgets.Layout(
                margin="0 48px 24px 0",
                flex="1 1 320px",
            ),
        )

        configuration_and_toolboxes_box = widgets.Box(
            [configuration_vbox, installed_toolboxes_vbox, additional_toolboxes_vbox],
            layout=widgets.Layout(
                display="flex",
                flex_flow="row wrap",
                width="100%",
                align_items="flex-start",
            ),
        )

        configuration_accordion = widgets.Accordion(
            children=[
                configuration_and_toolboxes_box,
                matlab_interface_for_databricks_vbox,
            ],
        )

        # Using set_title to configure accordion titles
        configuration_accordion.set_title(0, "Configuration and Toolboxes")
        configuration_accordion.set_title(1, "MATLAB Interface for Databricks")

        display_widget(box_upper)
        display_widget(configuration_accordion)

        # Start cluster keep-alive if auto-termination is enabled,
        # to prevent cluster from shutting down while user is interacting with the app.
        if DATABRICKS_CLUSTER_AUTO_TERMINATION_MINUTES:
            dbx.start_cluster_keep_alive(
                username=get_username(),
                check_interval_minutes=DATABRICKS_CLUSTER_AUTO_TERMINATION_MINUTES // 3,
            )

        ## App Functionality begins here:

        def clear_outputs(b):
            app_outputs.clear_output(wait=True)
            with app_outputs:
                print("...")

        clear_outputs_button.on_click(clear_outputs)

        def refresh_matlab_sessions(b):
            available_matlab_sessions_selectmultiple.options = (
                matlab_proxy.list_servers_ports(username=get_username())
            )

        def download_databricks_support_package(b):
            databricks_support_package_download_button.disabled = True
            install_databricks_support_package_button.disabled = True
            databricks_support_package_location.disabled = True
            downloaded_location = web.download_file(
                __DATABRICKS_SUPPORT_PACKAGE_DOWNLOAD_URL,
                status_html=download_status_html,
            )
            if downloaded_location:
                databricks_support_package_location.disabled = False
                databricks_support_package_location.value = downloaded_location

            databricks_support_package_download_button.disabled = False
            install_databricks_support_package_button.disabled = False
            databricks_support_package_location.disabled = False

        @app_outputs.capture(clear_output=True)
        def stop_matlab_session(b):
            selected_sessions = available_matlab_sessions_selectmultiple.value
            if selected_sessions:
                for session in selected_sessions:
                    matlab_proxy.stop(
                        username=get_username(), port=session, context=context
                    )
                    print(f"Stopped MATLAB session: {session}")
            else:
                print("No sessions selected to stop.")
            available_matlab_sessions_selectmultiple.options = (
                matlab_proxy.list_servers_ports(username=get_username())
            )

        def connect_to_matlab_sessionid(session_id):
            URL = dbx.get_url_to_matlab(session_id, context)
            if URL:
                button_text = widgets.Label(
                    f"Generating link to MATLAB session: {session_id}"
                )
                button_html = f"""<button style="background-color: green; color: white;" onclick="{_get_window_open_command(URL)}">Open MATLAB Session {session_id}</button>"""
                display(
                    widgets.VBox(
                        [
                            button_text,
                            widgets.HTML(button_html),
                        ]
                    )
                )

        def refresh_installed_toolboxes():
            # Refreshing installed toolboxes in configuration tab
            latest_installed_toolboxes = matlab.installed_toolboxes(
                username=get_username()
            )
            installed_toolboxes_inner_vbox.children = [
                widgets.Label(
                    value=toolbox_name,
                    layout=widgets.Layout(height="auto", flex="0 0 auto"),
                )
                for toolbox_name in latest_installed_toolboxes
            ]

        def get_matlab_autotermination_setting() -> dict:
            # Fetch the idle timeout value from the widget, default to None if not set
            if not idle_timeout_textbox.disabled:
                return {"MWI_SHUTDOWN_ON_IDLE_TIMEOUT": str(idle_timeout_textbox.value)}
            return {}

        def get_additional_environment_variables_for_matlab_startup():
            env_vars = {}
            env_vars.update(get_matlab_autotermination_setting())
            return env_vars

        @app_outputs.capture(clear_output=True)
        def connect_to_matlab_session(b):
            display_header = widgets.Label("------------------")
            display(display_header)
            selected_sessions = available_matlab_sessions_selectmultiple.value
            if selected_sessions:
                for session_id in selected_sessions:
                    connect_to_matlab_sessionid(session_id)
            else:
                print("No sessions selected to connect.")
            display(display_header)

        @app_outputs.capture(clear_output=True)
        def start_matlab_session(b):
            start_matlab_button.disabled = True
            app_outputs.clear_output(wait=True)
            try:
                print("Starting MATLAB session...")
                session_id = matlab_proxy.start(
                    username=get_username(),
                    env=get_additional_environment_variables_for_matlab_startup(),
                    dbx_context=context,
                )
                list_of_running_servers = matlab_proxy.list_servers_ports(
                    username=get_username()
                )
                # New sessions might take a few seconds to appear.
                # Add the newly created session if it is not already present.
                if session_id not in list_of_running_servers:
                    list_of_running_servers.append(session_id)
                available_matlab_sessions_selectmultiple.options = (
                    list_of_running_servers
                )
                print("Started MATLAB session.")
                connect_to_matlab_sessionid(session_id)
                start_matlab_button.disabled = False
            except Exception as e:
                print(f"Exception while starting MATLAB: {str(e)}")
            finally:
                start_matlab_button.disabled = False

        start_matlab_button.on_click(start_matlab_session)
        connect_matlab_button.on_click(connect_to_matlab_session)
        stop_matlab_button.on_click(stop_matlab_session)
        refresh_matlab_button.on_click(refresh_matlab_sessions)
        databricks_support_package_download_button.on_click(
            download_databricks_support_package
        )
        install_databricks_support_package_button.on_click(
            install_databricks_support_package
        )

    diagnostics_overview_text = widgets.HTML(
        """
    <p>
        To view your environment details and investigate errors, run diagnostics.
        To request customer support, include the diagnostic results in a
        <a href='https://github.com/mathworks-ref-arch/matlab-on-databricks/issues'>GitHub issue</a>
        or in an email to <i>databricks@mathworks.com</i>.
    </p>
    """,
        layout=widgets.Layout(justify_content="flex-start"),
    )

    run_diagnostics_button = widgets.Button(
        description="Run Diagnostics",
        style={"button_color": "#008013"},
        icon="play",
    )
    run_diagnostics_button.add_class("dbx-button-text-white")

    diagnostics_inner_vbox_content = widgets.HTML(
        "", layout=widgets.Layout(justify_content="flex-start")
    )

    diagnostics_inner_vbox = widgets.Box(
        children=[diagnostics_inner_vbox_content],
        layout=widgets.Layout(
            width="100%",
            height="260px",
            border="1px solid lightgrey",
            margin="10px 0 0 0",
        ),
    )
    diagnostics_inner_vbox.add_class("resize-box-both")

    diagnostics_vbox = widgets.VBox(
        [diagnostics_overview_text, run_diagnostics_button, diagnostics_inner_vbox],
        layout=widgets.Layout(
            margin="0 48px 24px 0",
            height="auto",
            flex="1 1 320px",  # base width
            min_width="320px",
        ),
    )

    diagnostics_accordion = widgets.Accordion(
        children=[
            diagnostics_vbox,
        ],
        # Keep the accordion closed by default
        selected_index=None,
    )

    diagnostics_accordion.set_title(0, "Diagnostics")

    def run_diagnostics(b):
        lines = []
        for line in diagnostics.stream(username=get_username(), dbx_context=context):
            lines.append(line)
            diagnostics_inner_vbox_content.value = f"<pre>{'&#10;'.join(lines)}</pre>"

    run_diagnostics_button.on_click(run_diagnostics)

    display_widget(diagnostics_accordion)

    version_label = widgets.HTML(
        value=f"<span style='color: #9e9e9e; font-size: 11px;'>v{version()}</span>",
        layout=widgets.Layout(width="100%", justify_content="flex-end"),
    )
    display_widget(version_label)

    return parent_widget
