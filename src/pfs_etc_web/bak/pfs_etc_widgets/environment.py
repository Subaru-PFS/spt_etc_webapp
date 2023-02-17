#!/usr/bin/env python3

# Third Party Library
import panel as pn


class EnvironmentWidgets:
    def __init__(self, conf):
        self.panel = pn.Param(
            conf,
            widgets={
                "seeing": {
                    "type": pn.widgets.FloatSlider,
                    "step": 0.1,
                    "format": "0.0",
                },
                "degrade": {
                    "type": pn.widgets.FloatSlider,
                    "step": 0.2,
                    "format": "0.0",
                },
                "moon_zenith_angle": {"type": pn.widgets.IntSlider, "step": 15},
                "moon_target_angle": {"type": pn.widgets.IntSlider, "step": 30},
                "moon_phase": {
                    "type": pn.widgets.FloatSlider,
                    "step": 0.05,
                    "format": "0.00",
                },
            },
            # show_name=False,
            default_layout=pn.Column,
        )
