#!/usr/bin/env python3

# Standard Library
from collections import OrderedDict

# Third Party Library
import panel as pn

pn.extension(sizing_mode="stretch_width")


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
