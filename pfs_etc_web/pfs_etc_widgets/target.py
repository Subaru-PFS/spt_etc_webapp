#!/usr/bin/env python3

# Third Party Library
import panel as pn


class TargetWidgets:
    def __init__(self, params):

        # Templates
        self.template = pn.widgets.Select(
            name="Template Spectrum",
            groups={
                "Galaxy": [
                    "Star-forming galaxy",
                    "Quiescent galaxy",
                ],
                "Quasar": ["Quasar"],
                "Star": ["O0V", "A0V", "F0V"],
                "Misc": ["Flat in frequency"],
            },
        )

        self.mag = pn.widgets.FloatInput(
            name="Magnitude (AB)",
            value=params.mag,
        )

        self.redshift = pn.widgets.FloatInput(
            name="Redshift",
            start=0,
            end=20,
            step=0.1,
            value=params.redshift,
        )

        # Custom input spectrum
        self.mag_file = pn.widgets.FileInput(name="Custom Input Spectrum")

        # Misc. information
        self.galactic_extinction = pn.widgets.FloatInput(
            name="Galactic Extinction (mag)",
            value=params.galactic_extinction,
            format="0.0",
        )
        self.r_eff = pn.widgets.FloatInput(
            name="Effective Radius (arcsec)",
            value=params.r_eff,
        )

        _box_template = pn.WidgetBox(
            "#### Target Information",
            pn.Column(self.template, self.mag, self.redshift),
        )
        _box_custom_input = pn.WidgetBox(
            "#### Custom Input Spectrum",
            pn.Column(self.mag_file),
        )
        _box_misc = pn.WidgetBox(
            "#### Miscellaneous Information",
            pn.Column(self.r_eff, self.galactic_extinction),
        )

        self.pane = pn.Column(
            _box_template,
            _box_custom_input,
            _box_misc,
        )
