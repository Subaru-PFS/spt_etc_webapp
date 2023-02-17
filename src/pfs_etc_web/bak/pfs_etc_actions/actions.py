#!/usr/bin/env python3


def exec_etc(event):

    button_exec.button.disabled = True
    button_exec.button.name = "Running"

    panel_plots.pane.object = create_test_plot()

    panel_plots.pane.visible = True
    button_exec.button.name = "Run"
    button_exec.button.disabled = False

    print(panel_target.mag.value)
