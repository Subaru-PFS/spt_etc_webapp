#!/usr/bin/env python3

# Third Party Library
import panel as pn


class InstrumentWidgets:
    def __init__(self, params):

        # Instrument Configuration
        self.exp_time = pn.widgets.IntInput(
            name="Exposure Time per Exposure (s)",
            value=params.exp_time,
        )
        self.exp_num = pn.widgets.IntInput(
            name="Number of Exposures",
            value=params.exp_num,
        )
        self.field_angle = pn.widgets.FloatSlider(
            name="Distance from FoV center (degree)",
            start=0.0,
            end=0.7,
            step=0.1,
            value=params.field_angle,
        )
        self.mr_mode = pn.widgets.Checkbox(
            name="Use Medium Resolution? (checked=True)",
            value=params.mr_mode,
        )

        self.pane = pn.Column(
            self.exp_time,
            self.exp_num,
            self.field_angle,
            self.mr_mode,
        )
