#!/usr/bin/env python3

# Third Party Library
import panel as pn


class EnvironmentWidgets:
    def __init__(self, params):

        # Observing Condition
        self.seeing = pn.widgets.FloatSlider(
            name="Seeing FWHM (arcsec)",
            start=0.0,
            end=2.0,
            step=0.1,
            value=params.seeing,
            format="0.0",
        )
        self.transparency = pn.widgets.FloatSlider(
            name="Transparency",
            start=0.0,
            end=1.0,
            step=0.2,
            value=0.8,
            format="0.0",
        )
        self.moon_zenith_angle = pn.widgets.IntSlider(
            name="Moon Zenith Angle (degree)",
            start=0,
            end=90,
            step=15,
            value=params.moon_zenith_angle,
            format="00",
        )
        self.moon_target_angle = pn.widgets.IntSlider(
            name="Moon Separation to Target (degree)",
            start=0,
            end=180,
            step=30,
            value=params.moon_target_angle,
            format="00",
        )
        self.moon_phase = pn.widgets.FloatSlider(
            name="Moon Phase (0=new; 0.5=full; 1=new)",
            start=0.0,
            end=0.5,
            step=0.05,
            value=params.moon_phase,
            format="0.00",
        )

        self.pane = pn.Column(
            self.seeing,
            self.transparency,
            self.moon_zenith_angle,
            self.moon_target_angle,
            self.moon_phase,
        )
