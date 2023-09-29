#!/usr/bin/env python3

import datetime
import os
import secrets
import threading
import time

import panel as pn
import param
from logzero import logger
from panel.io.state import set_curdoc

from .pfs_etc_params import (
    EnvironmentConf,
    InstrumentConf,
    OutputConf,
    TargetConf,
    TelescopeConf,
)
from .pfs_etc_specsim import PfsSpecSim
from .pfs_etc_utils import create_dummy_plot
from .pfs_etc_widgets import (
    BokehWidgets,
    DownloadWidgets,
    EnvironmentWidgets,
    ExecButtonWidgets,
    InitNoteWidgets,
    InstrumentWidgets,
    TargetWidgets,
    TelescopeWidgets,
)

# pn.param.ParamMethod.loading_indicator = True

# pn.extension(
#     "floatpanel",
#     "mathjax",
#     loading_spinner="dots",
#     loading_color="#6A589D",
#     sizing_mode="stretch_width",
#     css_files=[
#         "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
#     ],
#     js_files={
#         "font-awesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"
#     },
# )


def pfs_etc_app():
    template = pn.template.VanillaTemplate(
        title="PFS Spectral Simulator",
        sidebar_width=400,
        header_background="#6A589D",
        busy_indicator=None,
        favicon="docs/site/assets/images/favicon.png",
        # logo="docs/site/assets/images/favicon.png",
        # logo="src/pfs_etc_web/assets/logo-pfs.png",
    )

    # set parameter objects with default parameters
    conf_target = TargetConf()
    conf_environment = EnvironmentConf()
    conf_instrument = InstrumentConf()
    conf_telescope = TelescopeConf()

    conf_output = OutputConf()

    if not os.path.exists(conf_output.basedir):
        os.mkdir(conf_output.basedir)

    # Create panels in the side panel
    panel_target = TargetWidgets(conf_target)
    panel_environment = EnvironmentWidgets(conf_environment)
    panel_instrument = InstrumentWidgets(conf_instrument)
    panel_telescope = TelescopeWidgets(conf_telescope)

    # Use a tab layout for input parameters
    tab_inputs = pn.Tabs(
        ("Target    ", panel_target.panel),
        ("Condition ", panel_environment.panel),
        ("Instrument", panel_instrument.panel),
        ("Telescope ", panel_telescope.panel),
        # sizing_mode="stretch_width",
    )

    # Create button to start computation
    panel_buttons = ExecButtonWidgets()

    # Create a panel to show plots
    panel_plots = BokehWidgets(create_dummy_plot())
    # panel_plots.pane.visible = False

    # Create download buttons
    panel_downloads = DownloadWidgets(visible=False)

    # Float panel to display some messages
    panel_initnote = InitNoteWidgets()

    # put panels into a template
    sidebar_column = pn.Column(panel_buttons.pane, tab_inputs)
    template.sidebar.append(sidebar_column)

    main_column = pn.Column(
        panel_initnote.flatpanel,
        panel_downloads.pane,
        panel_plots.pane,
    )
    template.main.append(main_column)

    # setup threading
    c_exec = threading.Condition()
    c_reset = threading.Condition()

    queue_exec = []
    queue_reset = []

    # https://github.com/holoviz/panel/issues/5488
    curdoc = pn.state.curdoc

    def callback_exec():
        # panel_plots.visible = False
        while True:
            c_exec.acquire()
            for _ in queue_exec:
                with set_curdoc(curdoc):
                    # print("callback_exec")
                    # template.main.append(main_column)
                    logger.info("callback function is called")

                    session_id = (
                        datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                        + "_"
                        + secrets.token_hex(8)
                    )

                    logger.info(f"Session ID: {session_id}")

                    conf_output.sessiondir = session_id

                    panel_buttons.exec.disabled = True
                    panel_buttons.exec.name = "Running"

                    panel_buttons.reset.disabled = True

                    panel_plots.plot.object = create_dummy_plot()

                    panel_downloads.download_pfsobject_fits.visible = False
                    panel_downloads.download_simspec_fits.visible = False
                    panel_downloads.download_simspec_csv.visible = False
                    panel_downloads.download_snline_fits.visible = False
                    panel_downloads.download_snline_csv.visible = False

                    # print(conf_instrument.mr_mode)

                    specsim = PfsSpecSim(
                        target=conf_target,
                        environment=conf_environment,
                        instrument=conf_instrument,
                        telescope=conf_telescope,
                        output=conf_output,
                    )

                    try:
                        with pn.param.set_values(panel_plots.pane, loading=True):
                            logger.info("Running PFS Spectrum Simulator")
                            specsim.exec(skip=False)

                        logger.info("Plotting simulated spectrum")
                        panel_plots.pane.visible = False
                        panel_plots.plot.object = specsim.show()

                        logger.info("Set download buttons")
                        panel_downloads.download_pfsobject_fits.file = (
                            f"{specsim.outfile_pfsobject}"
                        )
                        panel_downloads.download_simspec_fits.file = (
                            f"{specsim.outfile_simspec_prefix}.fits"
                        )
                        panel_downloads.download_simspec_csv.file = (
                            f"{specsim.outfile_simspec_prefix}.ecsv"
                        )
                        panel_downloads.download_snline_fits.file = (
                            f"{specsim.outfile_snline_prefix}.fits"
                        )
                        panel_downloads.download_snline_csv.file = (
                            f"{specsim.outfile_snline_prefix}.ecsv"
                        )

                        panel_downloads.download_pfsobject_fits.visible = True
                        panel_downloads.download_simspec_fits.visible = True
                        panel_downloads.download_simspec_csv.visible = True
                        panel_downloads.download_snline_fits.visible = True
                        panel_downloads.download_snline_csv.visible = True
                        panel_plots.pane.visible = True

                        logger.info("Enable the run button")
                        panel_buttons.exec.name = "Run"
                        panel_buttons.exec.disabled = False

                    except ValueError as e:
                        # pass
                        # this does not work for panel 1.2.2
                        # https://github.com/holoviz/panel/issues/5090
                        pn.state.notifications.error(f"{str(e)}", duration=0)

                        logger.info("Enable the run button")
                        panel_buttons.exec.name = "Run"
                        panel_buttons.exec.disabled = False
                        panel_buttons.reset.disabled = False

            queue_exec.clear()
            c_exec.release()
            time.sleep(1)

    def callback_reset():
        while True:
            c_reset.acquire()
            for _ in queue_reset:
                logger.info("Reset parameters")
                conf_target.reset()
                conf_environment.reset()
                conf_instrument.reset()
                conf_telescope.reset()
                panel_plots.plot.object = None
                panel_downloads.download_pfsobject_fits.file = None
                panel_downloads.download_pfsobject_fits.visible = False
                panel_downloads.download_simspec_fits.file = None
                panel_downloads.download_simspec_fits.visible = False
                panel_downloads.download_simspec_csv.file = None
                panel_downloads.download_simspec_csv.visible = False
                panel_downloads.download_snline_fits.file = None
                panel_downloads.download_snline_fits.visible = False
                panel_downloads.download_snline_csv.file = None
                panel_downloads.download_snline_csv.visible = False
            queue_reset.clear()
            c_reset.release()
            time.sleep(1)

    thread_exec = threading.Thread(target=callback_exec, daemon=True)
    thread_exec.start()

    thread_reset = threading.Thread(target=callback_reset, daemon=True)
    thread_reset.start()

    def on_click_exec(event):
        queue_exec.append(event)

    def on_click_reset(event):
        queue_reset.append(event)

    # Define an action on click
    panel_buttons.exec.on_click(on_click_exec)
    panel_buttons.reset.on_click(on_click_reset)

    # print("info note")
    # pn.state.notifications.info("This is a info notification.", duration=0)

    # line_sn = conf_target.line_sn
    # print(line_sn)

    # @param.depends("line_sn", watch=True)
    # def toggle_line_box():
    #     print("Pressed")

    return template.servable()

    # return pn.Row(
    #     pn.Column(
    #         panel_buttons.pane,
    #         tab_inputs,
    #         width=350,
    #     ),
    #     pn.Column(
    #         panel_downloads.pane,
    #         panel_plots.pane,
    #     ),
    # ).servable()


# app = pfs_etc_app
