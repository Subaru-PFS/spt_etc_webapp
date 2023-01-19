# Third Party Library
import panel as pn


class ExecButtonWidgets:
    def __init__(self):
        self.reset = pn.widgets.Button(name="Reset", disabled=True)
        self.exec = pn.widgets.Button(name="Run", button_type="danger")

        self.pane = pn.Row(
            self.reset,
            self.exec,
        )
