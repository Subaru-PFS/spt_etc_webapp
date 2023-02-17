#!/usr/bin/env python3

# Third Party Library
import panel as pn


class TelescopeWidgets:
    def __init__(self, conf):
        self.panel = pn.Param(
            conf,
            widgets={"zenith_angle": {"type": pn.widgets.IntSlider, "step": 5}},
            # show_name=False,
            default_layout=pn.Column
            # expand=True,
        )
