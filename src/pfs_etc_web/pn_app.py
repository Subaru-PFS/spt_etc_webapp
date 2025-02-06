#!/usr/bin/env python3

import datetime
import os
import secrets
import threading
import time

import panel as pn
import param
from bokeh.resources import INLINE
from dotenv import dotenv_values
from loguru import logger
from panel.io.state import set_curdoc

from .pfs_etc_params import (
    EnvironmentConf,
    InstrumentConf,
    OutputConf,
    TargetConf,
    TelescopeConf,
)
from .pfs_etc_specsim import PfsSpecSim
from .pfs_etc_utils import create_dummy_plot, recover_simulation
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


class SimulationId(param.Parameterized):
    simulation_id = param.String(default=None)


def show_main_panel(panel_plots, panel_downloads, specsim, write=True):
    panel_plots.pane.visible = False
    panel_plots.plot.object = specsim.show(write=write)

    logger.info("Set download buttons")

    panel_downloads.download_pfsobject_fits.file = f"{specsim.outfile_pfsobject}"
    panel_downloads.download_simspec_fits.file = (
        f"{specsim.outfile_simspec_prefix}.fits"
    )
    panel_downloads.download_simspec_csv.file = f"{specsim.outfile_simspec_prefix}.ecsv"
    panel_downloads.download_snline_fits.file = f"{specsim.outfile_snline_prefix}.fits"
    panel_downloads.download_snline_csv.file = f"{specsim.outfile_snline_prefix}.ecsv"
    panel_downloads.download_tjtext.file = f"{specsim.outfile_tjtext}"

    panel_downloads.download_heading.visible = True
    panel_downloads.download_pfsobject_fits.visible = True
    panel_downloads.download_simspec_fits.visible = True
    panel_downloads.download_simspec_csv.visible = True
    panel_downloads.download_snline_fits.visible = True
    panel_downloads.download_snline_csv.visible = True
    panel_downloads.download_tjtext.visible = True
    panel_plots.plot_heading.visible = True
    panel_plots.pane.visible = True


def pfs_etc_app():
    # pn.config.notifications = True
    pn.state.notifications.position = "bottom-left"

    template = pn.template.MaterialTemplate(
        # template = pn.template.BootstrapTemplate(
        title="PFS Spectral Simulator",
        # sidebar_width=400,
        sidebar_width=420,
        header_background="#6A589D",
        # header_background="#3A7D7E",
        busy_indicator=None,
        # site_url="/",
        favicon="doc/assets/images/favicon.png",
    )

    if os.path.exists(".env"):
        config = dotenv_values(".env")
    else:
        config = {}

    logger.info(f"Configuration: {config}")

    if "OUTPUT_DIR" in config.keys():
        basedir = config["OUTPUT_DIR"]
    else:
        basedir = "tmp"

    logger.info(f"Output directory: {basedir}")

    # set simulation_id class
    simulation_id = SimulationId()

    pn.state.location.sync(simulation_id, {"simulation_id": "id"})

    # set parameter objects with default parameters
    conf_target = TargetConf()
    conf_environment = EnvironmentConf()
    conf_instrument = InstrumentConf()
    conf_telescope = TelescopeConf()

    conf_output = OutputConf(basedir=basedir)

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
    )

    # Create button to start computation
    panel_buttons = ExecButtonWidgets()

    # Create a panel to show plots
    panel_plots = BokehWidgets(create_dummy_plot())
    panel_plots.plot_heading.visible = False

    # Create download buttons
    panel_downloads = DownloadWidgets(visible=False)

    is_recovered = False

    if simulation_id.simulation_id not in [None, "null", ""]:
        recovered_simulation_id, is_recovered, custom_input_file = recover_simulation(
            simulation_id.simulation_id,
            conf_target,
            conf_environment,
            conf_instrument,
            conf_telescope,
            conf_output,
            logger,
        )
        if is_recovered:
            conf_output.sessiondir = recovered_simulation_id
            specsim = PfsSpecSim(
                target=conf_target,
                environment=conf_environment,
                instrument=conf_instrument,
                telescope=conf_telescope,
                output=conf_output,
            )
            show_main_panel(panel_plots, panel_downloads, specsim, write=False)

    # Float panel to display some messages
    # panel_initnote = InitNoteWidgets()

    # put panels into a template
    sidebar_column = pn.Column(panel_buttons.pane, tab_inputs)
    template.sidebar.append(sidebar_column)

    main_column = pn.Column(
        # panel_initnote.flatpanel,
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

    # with set_curdoc(curdoc):
    #     if is_recovered:
    #         pn.state.notifications.info(
    #             f"Recovering Simulation ID {simulation_id}",
    #             duration=0,
    #         )
    #     else:
    #         pn.state.notifications.warning(
    #             f"Simulation ID {simulation_id} not found, use initial parameters",
    #             duration=0,
    #         )

    def callback_exec():
        while True:
            c_exec.acquire()
            for _ in queue_exec:
                with set_curdoc(curdoc):
                    logger.info("callback function is called")

                    session_id = (
                        datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                        + "-"
                        # + "_"
                        + secrets.token_hex(8)
                    )

                    simulation_id.simulation_id = session_id

                    logger.info(f"Session ID: {session_id}")

                    conf_output.sessiondir = session_id

                    panel_buttons.exec.disabled = True
                    panel_buttons.exec.name = "Running"

                    panel_buttons.reset.disabled = True

                    panel_target.disabled(disabled=True)
                    panel_environment.disabled(disabled=True)
                    panel_instrument.disabled(disabled=True)
                    panel_telescope.disabled(disabled=True)

                    panel_plots.plot.object = create_dummy_plot()
                    panel_plots.plot_heading.visible = False

                    panel_downloads.download_heading.visible = False
                    panel_downloads.download_pfsobject_fits.visible = False
                    panel_downloads.download_simspec_fits.visible = False
                    panel_downloads.download_simspec_csv.visible = False
                    panel_downloads.download_snline_fits.visible = False
                    panel_downloads.download_snline_csv.visible = False
                    panel_downloads.download_tjtext.visible = False

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
                        show_main_panel(
                            panel_plots, panel_downloads, specsim, write=True
                        )

                        # panel_plots.pane.visible = False
                        # panel_plots.plot.object = specsim.show()

                        # logger.info("Set download buttons")
                        # panel_downloads.download_pfsobject_fits.file = (
                        #     f"{specsim.outfile_pfsobject}"
                        # )
                        # panel_downloads.download_simspec_fits.file = (
                        #     f"{specsim.outfile_simspec_prefix}.fits"
                        # )
                        # panel_downloads.download_simspec_csv.file = (
                        #     f"{specsim.outfile_simspec_prefix}.ecsv"
                        # )
                        # panel_downloads.download_snline_fits.file = (
                        #     f"{specsim.outfile_snline_prefix}.fits"
                        # )
                        # panel_downloads.download_snline_csv.file = (
                        #     f"{specsim.outfile_snline_prefix}.ecsv"
                        # )
                        # panel_downloads.download_tjtext.file = (
                        #     f"{specsim.outfile_tjtext}"
                        # )

                        # panel_downloads.download_heading.visible = True
                        # panel_downloads.download_pfsobject_fits.visible = True
                        # panel_downloads.download_simspec_fits.visible = True
                        # panel_downloads.download_simspec_csv.visible = True
                        # panel_downloads.download_snline_fits.visible = True
                        # panel_downloads.download_snline_csv.visible = True
                        # panel_downloads.download_tjtext.visible = True

                        # panel_plots.plot_heading.visible = True
                        # panel_plots.pane.visible = True

                        logger.info("Enable the run button")
                        panel_buttons.exec.name = "Run"
                        panel_buttons.exec.disabled = False
                        panel_buttons.reset.disabled = False
                        panel_target.disabled(disabled=False)
                        panel_environment.disabled(disabled=False)
                        panel_instrument.disabled(disabled=False)
                        panel_telescope.disabled(disabled=False)

                        # panel_plots.pane.save(
                        #     specsim.outfile_plot,
                        #     resources=INLINE,
                        #     title="Simulated PFS Spectrum",
                        # )

                    except ValueError as e:
                        # pass
                        # this does not work for panel 1.2.2
                        # https://github.com/holoviz/panel/issues/5090
                        pn.state.notifications.error(f"{str(e)}", duration=0)

                        logger.info("Enable the run button")
                        panel_buttons.exec.name = "Run"
                        panel_buttons.exec.disabled = False
                        panel_buttons.reset.disabled = False
                        panel_target.disabled(disabled=False)
                        panel_environment.disabled(disabled=False)
                        panel_instrument.disabled(disabled=False)
                        panel_telescope.disabled(disabled=False)

                        simulation_id.simulation_id = None

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

                simulation_id.simulation_id = None

                panel_plots.plot.object = None
                panel_plots.plot_heading.visible = False

                panel_downloads.download_heading.visible = False
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
                panel_downloads.download_tjtext.file = None
                panel_downloads.download_tjtext.visible = False
            queue_reset.clear()
            c_reset.release()
            time.sleep(1)

    thread_exec = threading.Thread(target=callback_exec, daemon=True)
    thread_exec.start()

    thread_reset = threading.Thread(target=callback_reset, daemon=True)
    thread_reset.start()

    def on_click_exec(event):
        pn.state.location.unsync(simulation_id, {"simulation_id": "id"})
        queue_exec.append(event)

    def on_click_reset(event):
        pn.state.location.unsync(simulation_id, {"simulation_id": "id"})
        queue_reset.append(event)

    # Define an action on click
    panel_buttons.exec.on_click(on_click_exec)
    panel_buttons.reset.on_click(on_click_reset)

    return template.servable()
