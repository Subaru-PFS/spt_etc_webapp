#!/usr/bin/env python3

import datetime
import os

# import queue
import secrets
import threading
import time
from io import BytesIO

import pandas as pd
import panel as pn
from logzero import logger

from .pfs_etc_params import (
    EnvironmentConf,
    InstrumentConf,
    OutputConf,
    TargetConf,
    TelescopeConf,
)
from .pfs_etc_plots import create_dummy_plot
from .pfs_etc_specsim import PfsSpecSim
from .pfs_etc_widgets import (
    BokehWidgets,
    DownloadWidgets,
    EnvironmentWidgets,
    ExecButtonWidgets,
    InstrumentWidgets,
    TargetWidgets,
    TelescopeWidgets,
)

pn.extension(
    template="bootstrap",
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
)


def pfs_etc_app():
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
        ("Target", panel_target.panel),
        ("Condition", panel_environment.panel),
        ("Instrument", panel_instrument.panel),
        ("Telescope", panel_telescope.panel),
    )

    # Create button to start computation
    panel_buttons = ExecButtonWidgets()

    # Create download buttons
    panel_downloads = DownloadWidgets(visible=False)

    # setup threading
    c_exec = threading.Condition()
    c_reset = threading.Condition()

    queue_exec = []
    queue_reset = []

    def callback_exec():
        while True:
            c_exec.acquire()
            for _ in queue_exec:
                logger.info("callback function is called")

                session_id = (
                    datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    + "_"
                    + secrets.token_hex(8)
                )

                print(f"Session ID: {session_id}")

                conf_output.sessiondir = session_id

                panel_buttons.exec.disabled = True
                panel_buttons.exec.name = "Running"

                panel_plots.plot.object = create_dummy_plot()
                panel_downloads.download_simspec_fits.visible = False
                panel_downloads.download_simspec_csv.visible = False
                panel_downloads.download_snline_fits.visible = False
                panel_downloads.download_snline_csv.visible = False

                print(conf_instrument.mr_mode)

                specsim = PfsSpecSim(
                    target=conf_target,
                    environment=conf_environment,
                    instrument=conf_instrument,
                    telescope=conf_telescope,
                    output=conf_output,
                )

                with pn.param.set_values(panel_plots.pane, loading=True):
                    logger.info("Running PFS Spectrum Simulator")
                    specsim.exec(skip=False)

                logger.info("Plotting simulated spectrum")
                panel_plots.plot.object = specsim.show()
                panel_buttons.exec.name = "Run"

                logger.info("Set download buttons")
                panel_downloads.download_simspec_fits.visible = True
                panel_downloads.download_simspec_csv.visible = True
                panel_downloads.download_snline_fits.visible = True
                panel_downloads.download_snline_csv.visible = True

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

                logger.info("Enable the run button")
                panel_buttons.exec.disabled = False

                print(conf_telescope.zenith_angle)
                print(conf_instrument.mr_mode)
                print(conf_target.mag)
                print(conf_target.template)
                print(conf_target.mag_file)

                # if conf_target.custom_input is not None:
                #     df_content = pd.read_csv(
                #         BytesIO(conf_target.custom_input), encoding="utf8"
                #     )
                #     print(df_content)

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

    # Create a panel to show plots
    panel_plots = BokehWidgets(create_dummy_plot())

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

    return pn.Row(
        pn.Column(
            panel_buttons.pane,
            tab_inputs,
            width=350,
        ),
        pn.Column(
            panel_downloads.pane,
            panel_plots.pane,
        ),
    ).servable(title="PFS Spectral Simulator")

    # return pn.Row(
    #     pn.Column(
    #         panel_buttons.pane,
    #         tab_inputs,
    #         width=350,
    #     ),
    #     panel_plots.pane,
    # ).servable(title="PFS Spectral Simulator")


if __name__.startswith("bokeh"):
    pass
    # main_app()
