#!/usr/bin/env python3

import panel as pn


class ExecButtonWidgets:
    def __init__(self):
        self.reset = pn.widgets.Button(name="Reset")
        self.exec = pn.widgets.Button(name="Run", button_type="danger")

        self.pane = pn.Row(
            self.reset,
            self.exec,
        )


class TargetWidgets:
    def __init__(self, conf):
        _template = pn.Param(
            conf.param.template,
            widgets={
                "template": {
                    "type": pn.widgets.Select,
                    "groups": {
                        "Galaxy": [
                            "Star-forming galaxy",
                            "Quiescent galaxy",
                        ],
                        "Quasar": ["Quasar"],
                        "Star": ["O0V", "A0V", "F0V"],
                        "Misc": ["Flat in frequency"],
                    },
                },
            },
            default_layout=pn.Column,
        )
        _mag = pn.Param(
            conf.param.mag,
            widgets={"mag": {"type": pn.widgets.FloatInput}},
            default_layout=pn.Column,
        )
        _wavelength = pn.Param(
            conf.param.wavelength,
            widgets={"wavelength": {"type": pn.widgets.FloatInput}},
            default_layout=pn.Column,
        )
        _redshift = pn.Param(
            conf.param.redshift,
            widgets={"redshift": {"type": pn.widgets.FloatInput}},
            default_layout=pn.Column,
        )
        _line_flux = pn.Param(
            conf.param.line_flux,
            widgets={"line_flux": {"type": pn.widgets.FloatInput}},
            default_layout=pn.Column,
        )
        _line_width = pn.Param(
            conf.param.line_width,
            widgets={"line_width": {"type": pn.widgets.FloatInput}},
            default_layout=pn.Column,
        )

        # Custom input spectrum
        _mag_file = pn.Param(
            conf.param.mag_file,
            widgets={
                "mag_file": {"type": pn.widgets.FileInput},
                "accept": ".csv",
            },
        )

        # Misc. information
        _galactic_extinction = pn.Param(
            conf.param.galactic_extinction,
            widgets={
                "galactic_extinction": {
                    "type": pn.widgets.FloatInput,
                    "format": "0.0",
                }
            },
        )
        _r_eff = pn.Param(
            conf.param.r_eff,
            widgets={"r_eff": {"type": pn.widgets.FloatInput}},
        )

        # Put widgets into categories
        _box_template = pn.WidgetBox(
            "##### Target Information",
            pn.Column(_template, _mag, _wavelength, _redshift),
        )

        _box_line = pn.WidgetBox(
            "##### Emission Line Properties",
            pn.Column(_line_flux, _line_width),
        )

        _box_custom_input = pn.WidgetBox(
            "##### Custom Input Spectrum",
            pn.Column(_mag_file),
        )
        _box_misc = pn.WidgetBox(
            "##### Miscellaneous Information",
            pn.Column(_r_eff, _galactic_extinction),
        )

        # Arrange into a layout
        self.panel = pn.Column(
            _box_template,
            _box_line,
            _box_custom_input,
            _box_misc,
        )


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
            default_layout=pn.Column,
        )


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
            default_layout=pn.Column,
        )


class TelescopeWidgets:
    def __init__(self, conf):
        self.panel = pn.Param(
            conf,
            widgets={"zenith_angle": {"type": pn.widgets.IntSlider, "step": 5}},
            default_layout=pn.Column,
        )


class MatplotlibWidgets:
    def __init__(self, fig, dpi=144, visible=True):
        self.pane = pn.pane.Matplotlib(fig, dpi=dpi, visible=visible)
        pass


class BokehWidgets:
    def __init__(self, p, visible=True):
        self.plot = pn.pane.Bokeh(p, visible=visible, sizing_mode="stretch_width")
        self.pane = pn.Column(self.plot)
