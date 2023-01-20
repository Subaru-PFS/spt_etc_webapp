#!/usr/bin/env python3

# Standard Library
from io import BytesIO

# Third Party Library
import pandas as pd
import panel as pn
from logzero import logger
from pfs_etc_params import EnvironmentConf
from pfs_etc_params import InstrumentConf
from pfs_etc_params import PfsSpecParameter
from pfs_etc_params import TargetConf
from pfs_etc_params import TelescopeConf
from pfs_etc_plots import create_dummy_plot
from pfs_etc_specsim import PfsSpecSim
from pfs_etc_widgets import BokehWidgets
from pfs_etc_widgets import EnvironmentWidgets
from pfs_etc_widgets import ExecButtonWidgets
from pfs_etc_widgets import InstrumentWidgets
from pfs_etc_widgets import TargetWidgets
from pfs_etc_widgets import TelescopeWidgets

pn.extension(
    template="bootstrap",
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
)


def main_app():

    # set parameter objects with default parameters
    conf_target = TargetConf()
    conf_environment = EnvironmentConf()
    conf_instrument = InstrumentConf()
    conf_telescope = TelescopeConf()

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

    def on_click_exec(event):

        logger.info(f"callback function is called")

        panel_buttons.exec.disabled = True
        panel_buttons.exec.name = "Running"

        panel_plots.plot.object = None

        print(conf_instrument.mr_mode)

        specsim = PfsSpecSim(
            target=conf_target,
            environment=conf_environment,
            instrument=conf_instrument,
            telescope=conf_telescope,
        )

        with pn.param.set_values(panel_plots.pane, loading=True):
            logger.info(f"Running PFS Spectrum Simulator")
            specsim.exec(skip=True)
            # time.sleep(1)

        logger.info(f"Plotting simulated spectrum")
        panel_plots.plot.object = specsim.show()
        panel_buttons.exec.name = "Run"

        logger.info(f"Enable the run button")
        panel_buttons.exec.disabled = False

        print(conf_telescope.zenith_angle)
        print(conf_instrument.mr_mode)
        print(conf_target.mag)
        print(conf_target.template)
        print(conf_target.mag_file)

        if conf_target.mag_file is not None:
            df_content = pd.read_csv(BytesIO(conf_target.mag_file), encoding="utf8")
            print(df_content)

    def on_click_reset(event):
        logger.info(f"Reset parameters")
        conf_target.reset()
        conf_environment.reset()
        conf_instrument.reset()
        conf_telescope.reset()
        panel_plots.plot.object = None

    # Create a panel to show plots
    panel_plots = BokehWidgets(create_dummy_plot())

    # Define an action on click
    panel_buttons.exec.on_click(on_click_exec)
    panel_buttons.reset.on_click(on_click_reset)

    return pn.Row(
        pn.Column(
            panel_buttons.pane,
            tab_inputs,
            width=350,
        ),
        panel_plots.pane,
    ).servable(title="PFS Exposure Simulator")


if __name__.startswith("bokeh"):

    main_app()
