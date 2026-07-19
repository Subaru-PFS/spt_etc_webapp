#!/usr/bin/env python3

import asyncio
import datetime
import os
import secrets

import panel as pn
import param
from dotenv import dotenv_values
from loguru import logger

from . import PfsArm
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
    VersionInfoWidgets,
)


class SimulationId(param.Parameterized):
    simulation_id = param.String(default=None)


def show_main_panel(panel_plots, panel_downloads, specsim, simulation_id, write=True):
    panel_plots.pane.visible = False
    panel_plots.plot.object = specsim.show(write=write)

    # notify saturation
    for arm in PfsArm:
        if specsim.flag_saturation[arm]:
            pn.state.notifications.error(
                f"Saturation detected in the {arm.label} arm.",
                duration=0,
            )
            logger.warning(f"Saturation detected in {arm.name} arm")

    logger.info("Set download buttons")

    panel_downloads.download_pfsobject_fits.file = f"{specsim.outfile_pfsobject}"
    panel_downloads.download_simspec_fits.file = (
        f"{specsim.outfile_simspec_prefix}.fits"
    )
    panel_downloads.download_simspec_csv.file = f"{specsim.outfile_simspec_prefix}.ecsv"
    panel_downloads.download_snline_fits.file = f"{specsim.outfile_snline_prefix}.fits"
    panel_downloads.download_snline_csv.file = f"{specsim.outfile_snline_prefix}.ecsv"
    panel_downloads.download_tjtext.file = f"{specsim.outfile_tjtext}"

    panel_downloads.update_simulation_id(simulation_id)

    panel_downloads.download_heading.visible = True
    panel_downloads.simulation_id_text.visible = True
    # panel_downloads.simulation_id_button.visible = True
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
        ("Condition ", pn.Column(panel_environment.panel, panel_environment.note)),
        ("Instrument", panel_instrument.panel),
        ("Telescope ", panel_telescope.panel),
    )

    # Create button to start computation
    panel_buttons = ExecButtonWidgets()

    # Create version info panel
    panel_version = VersionInfoWidgets()

    # Create a panel to show plots
    panel_plots = BokehWidgets(create_dummy_plot())
    panel_plots.plot_heading.visible = False

    # Create download buttons
    panel_downloads = DownloadWidgets(visible=False)

    is_recovered = False

    # Attempt to recover simulation if simulation_id is provided
    if simulation_id.simulation_id not in [None, "null", ""]:
        # Validate simulation_id format (must be YYYYMMDD-HHMMSS-...)
        if (
            len(simulation_id.simulation_id) < 8
            or not simulation_id.simulation_id[:8].isdigit()
        ):
            logger.error(
                f"Invalid simulation_id format: {simulation_id.simulation_id}. "
                "Expected YYYYMMDD-HHMMSS-... format."
            )
        else:
            # Try to recover the simulation
            recovered_simulation_id, is_recovered, custom_input_file = (
                recover_simulation(
                    simulation_id.simulation_id,
                    conf_target,
                    conf_environment,
                    conf_instrument,
                    conf_telescope,
                    conf_output,
                    logger,
                )
            )

            if is_recovered:
                # Extract year and month from recovered session_id
                year = recovered_simulation_id[:4]
                month = recovered_simulation_id[4:6]
                conf_output.sessiondir = f"{year}/{month}/{recovered_simulation_id}"

                specsim = PfsSpecSim(
                    target=conf_target,
                    environment=conf_environment,
                    instrument=conf_instrument,
                    telescope=conf_telescope,
                    output=conf_output,
                )
                show_main_panel(
                    panel_plots,
                    panel_downloads,
                    specsim,
                    recovered_simulation_id,
                    write=False,
                )

    # Float panel to display some messages
    # panel_initnote = InitNoteWidgets()

    # put panels into a template
    sidebar_column = pn.Column(
        panel_buttons.pane,
        tab_inputs,
        pn.Spacer(),
        panel_version.pane,
    )
    template.sidebar.append(sidebar_column)

    main_column = pn.Column(
        # panel_initnote.flatpanel,
        panel_downloads.pane,
        panel_plots.pane,
    )
    template.main.append(main_column)

    def _enable_inputs():
        """Re-enable the run/reset buttons and the four input panels."""
        panel_buttons.exec.name = "Run"
        panel_buttons.exec.disabled = False
        panel_buttons.reset.disabled = False
        panel_target.disabled(disabled=False)
        panel_environment.disabled(disabled=False)
        panel_instrument.disabled(disabled=False)
        panel_telescope.disabled(disabled=False)

    async def on_click_exec(event):
        # Re-entrancy guard: ignore clicks while a run is in flight. The
        # disable below happens on the session's event loop before the first
        # await, so there is no intra-session race.
        if panel_buttons.exec.disabled:
            return

        pn.state.location.unsync(simulation_id, {"simulation_id": "id"})

        # clear notifications
        pn.state.notifications.clear()

        logger.info("callback function is called")

        # Use UTC for session_id timestamp
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        session_id = (
            now_utc.strftime("%Y%m%d-%H%M%S")
            + "-"
            # + "_"
            + secrets.token_hex(8)
        )

        simulation_id.simulation_id = session_id

        logger.info(f"Session ID: {session_id}")

        # Create nested directory path: YYYY/MM/session_id (UTC)
        year_month_path = now_utc.strftime("%Y/%m")
        conf_output.sessiondir = f"{year_month_path}/{session_id}"

        panel_buttons.exec.disabled = True
        panel_buttons.exec.name = "Running"

        panel_buttons.reset.disabled = True

        panel_target.disabled(disabled=True)
        panel_environment.disabled(disabled=True)
        panel_instrument.disabled(disabled=True)
        panel_telescope.disabled(disabled=True)

        panel_plots.plot_heading.visible = False
        panel_plots.plot.object = create_dummy_plot()

        panel_downloads.simulation_id_text.visible = False

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

        # The loading spinner must stay on across the await, which the
        # `pn.param.set_values` context manager cannot span cleanly, so
        # toggle it explicitly and clear it in `finally`.
        panel_plots.pane.loading = True
        try:
            logger.info("Running PFS Spectrum Simulator")
            # Run the blocking computation off the event loop.
            await asyncio.to_thread(specsim.exec, skip=False)

            logger.info("Plotting simulated spectrum")
            show_main_panel(
                panel_plots,
                panel_downloads,
                specsim,
                session_id,
                write=True,
            )

        except ValueError as e:
            # this does not work for panel 1.2.2
            # https://github.com/holoviz/panel/issues/5090
            pn.state.notifications.error(f"{str(e)}", duration=0)
            simulation_id.simulation_id = None

        except Exception as e:
            logger.exception(f"Unexpected error during simulation: {e}")
            pn.state.notifications.error(
                "An unexpected error occurred during the simulation.",
                duration=0,
            )
            simulation_id.simulation_id = None

        finally:
            logger.info("Enable the run button")
            _enable_inputs()
            panel_plots.pane.loading = False

    def on_click_reset(event):
        pn.state.location.unsync(simulation_id, {"simulation_id": "id"})

        # clear notifications
        pn.state.notifications.clear()

        logger.info("Reset parameters")
        conf_target.reset()
        conf_environment.reset()
        conf_instrument.reset()
        conf_telescope.reset()
        panel_target.clear_custom_input()

        simulation_id.simulation_id = None

        panel_plots.plot.object = None
        panel_plots.plot_heading.visible = False

        panel_downloads.simulation_id_text.visible = False

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

    # Define an action on click
    panel_buttons.exec.on_click(on_click_exec)
    panel_buttons.reset.on_click(on_click_reset)

    return template.servable()
