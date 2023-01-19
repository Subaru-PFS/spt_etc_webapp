#!/usr/bin/env python3

# Third Party Library
import panel as pn


class TelescopeWidgets:
    def __init__(self, params):
        # Telescope Configuration
        self.zenith_angle = pn.widgets.IntSlider(
            name="Zenith Angle (degree)",
            start=30,
            end=90,
            step=15,
            value=params.zenith_angle,
        )

        self.pane = pn.Column(self.zenith_angle)
