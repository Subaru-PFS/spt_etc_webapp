#!/usr/bin/env python3

# Third Party Library
import panel as pn


class InstrumentWidgets:
    def __init__(self, conf):
        self.panel = pn.Param(
            conf,
            widgets={
                "exp_time": {"type": pn.widgets.IntInput},
                "exp_num": {"type": pn.widgets.IntInput},
                "field_angle": {"type": pn.widgets.FloatSlider, "step": 0.1},
                "mr_mode": {"type": pn.widgets.Checkbox},
            },
            show_name=False,
            default_layout=pn.Column
            # expand=True,
        )
