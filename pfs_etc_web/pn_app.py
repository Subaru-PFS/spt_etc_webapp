#!/usr/bin/env python3

# Standard Library
import threading
import time

# Third Party Library
import panel as pn
from logzero import logger
from panel.layout.gridstack import GridStack
from pfs_etc_calc import PfsSpecSim
from pfs_etc_params import PfsSpecParameter
from pfs_etc_plots import create_dummy_plot

# from pfs_etc_plots import create_test_plot
from pfs_etc_widgets import BokehWidgets
from pfs_etc_widgets import EnvironmentWidgets
from pfs_etc_widgets import ExecButtonWidgets
from pfs_etc_widgets import InstrumentWidgets
from pfs_etc_widgets import TargetWidgets
from pfs_etc_widgets import TelescopeWidgets

pn.extension(
    # "gridstack",
    template="bootstrap",
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
    # sizing_mode="scale_width",
)

queue = []


def main_app():

    # # Create main app object using the BootStrap template
    # app = pn.template.BootstrapTemplate(
    #     title="PFS spectral simulator",
    #     header_background="#6A589D",  # picked from the PFS logo
    # )

    # Load default parameters
    params_default = PfsSpecParameter()

    # Create panels in the side panel
    panel_target = TargetWidgets(params_default)
    panel_environment = EnvironmentWidgets(params_default)
    panel_instrument = InstrumentWidgets(params_default)
    panel_telescope = TelescopeWidgets(params_default)

    # Use a tab layout for input parameters
    tab_inputs = pn.Tabs(
        ("Target", panel_target.pane),
        ("Condition", panel_environment.pane),
        ("Instrument", panel_instrument.pane),
        ("Telescope", panel_telescope.pane),
    )

    # Create button to start computation
    panel_buttons = ExecButtonWidgets()

    # # Async thread setting
    # # https://panel.holoviz.org/user_guide/Async_and_Concurrency.html
    # c = threading.Condition()

    # def callback(skip=False):
    #     global queue
    #     while True:
    #         c.acquire()
    #         for i, q in enumerate(queue):
    #             logger.info(f"callback function is called")
    #             logger.info(f"Processing item {i+1} of {len(queue)} items in queue")
    #             panel_buttons.exec.disabled = True
    #             panel_buttons.exec.name = "Running"
    #             specsim = PfsSpecSim(params_default)
    #             logger.info(f"Running PFS ETC: {skip}")
    #             with pn.param.set_values(panel_plots.pane, loading=True):
    #                 specsim.exec(skip=skip)
    #             logger.info(f"Running PFS Spectrum Simulator")
    #             panel_plots.plot.object = specsim.show()
    #             panel_buttons.exec.name = "Run"
    #             logger.info(f"Enable the run button")
    #             panel_buttons.exec.disabled = False
    #         queue.clear()
    #         c.release()
    #     # print("Queue empty")

    # thread = threading.Thread(target=callback, kwargs={"skip": False})
    # thread.start()

    # def on_click_exec_thread(event):
    #     queue.append(event)

    def on_click_exec(event):

        logger.info(f"callback function is called")

        panel_buttons.exec.disabled = True
        panel_buttons.exec.name = "Running"

        specsim = PfsSpecSim(params_default)

        # logger.info(f"Running PFS ETC: {skip}")

        with pn.param.set_values(panel_plots.pane, loading=True):
            # specsim.exec(skip=False)
            time.sleep(10)

        logger.info(f"Running PFS Spectrum Simulator")
        panel_plots.plot.object = specsim.show()
        panel_buttons.exec.name = "Run"

        logger.info(f"Enable the run button")
        panel_buttons.exec.disabled = False

    # Create a panel to show plots
    panel_plots = BokehWidgets(create_dummy_plot())

    # Define an action on click
    # panel_buttons.exec.on_click(on_click_exec_thread)
    panel_buttons.exec.on_click(on_click_exec)

    # gstack = GridStack(
    #     sizing_mode="stretch_both",
    #     nrows=1,
    #     ncols=4,
    #     mode="warn",
    # )
    # gstack[:, :1] = pn.Column(panel_buttons.pane, tab_inputs, scroll=False)
    # gstack[:, 1:] = panel_plots.pane

    # return gstack.servable()

    return pn.Row(
        pn.Column(
            panel_buttons.pane,
            tab_inputs,
        ),
        panel_plots.pane,
    ).servable()


if __name__.startswith("bokeh"):

    main_app()
