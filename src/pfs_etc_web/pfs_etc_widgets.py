#!/usr/bin/env python3

import numpy as np
import panel as pn


class InitNoteWidgets:
    def __init__(self):
        self.flatpanel = pn.layout.FloatPanel(
            pn.pane.Markdown(
                """
            - This is a development version of a PFS spectral simulator web app using [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/).
            - Documentation is available [here](/docs/index.html)
            - Updates may be deployed frequently without any notification, please reload the web site if the app freezes.
            - Feedback would be appreciated. Please feel free to contact either at `obsproc` Slack channel on PFS Slack or by email to Masato Onodera (<monodera@naoj.org>) (Subaru Telescope).

            If you are using via `run.app` domain:
            - The app is running on Google Cloud Run
            - Computation takes about 20-40 seconds. This may vary depending on the concurrent connections by users.
            - The app will not be responsive after 5 minutes of inactivity. Just reload the page would make the app active again.
        """,
                renderer="myst",
            ),
            name="Notes",
            contained=False,
            position="center",
            # theme="none",
            theme="#6A589D",
            width=600,
        )


class ExecButtonWidgets:
    def __init__(self):
        self.reset = pn.widgets.Button(
            name="Reset", button_style="solid", button_type="default"
        )
        self.exec = pn.widgets.Button(
            name="Run", button_style="outline", button_type="primary"
        )
        # self.doc = pn.pane.Markdown("[Manual](/docs/index.html)")
        self.doc = pn.pane.HTML(
            "<i class='fa-sharp fa-solid fa-book' ></i> <a href='/docs/index.html' target='_blank'>Manual</a>",
            width=80,
            height=26,
            styles={
                "display": "inline-block",
                "padding": "3px 0px 0px 5px",
                "margin": "4px 0px 0px 6px",
                # "background-color": "#4CAF50",
                # "background-color": "#f3f3f3",
                # "border-radius": "5px",
                # "border-style": "solid",
                # "border-color": "#000000",
                "text-align": "left",
                "text-decoration": "none",
                "font-size": "110%",
            },
        )
        self.pane = pn.Row(self.doc, self.reset, self.exec, height=40)


class TargetWidgets:
    def __init__(self, conf):
        self.template = pn.Param(
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
                        "Star": [
                            "B0V",
                            "A0V",
                            "F0V",
                            "G2V",
                            "K0V",
                            "M0V",
                            "K0III",
                            "M0III",
                        ],
                        "Misc": ["Flat in frequency"],
                    },
                },
            },
        )
        self.mag = pn.Param(
            conf.param.mag,
            widgets={"mag": {"type": pn.widgets.FloatInput}},
        )
        self.wavelength = pn.Param(
            conf.param.wavelength,
            widgets={"wavelength": {"type": pn.widgets.FloatInput}},
        )
        self.redshift = pn.Param(
            conf.param.redshift,
            widgets={"redshift": {"type": pn.widgets.FloatInput}},
        )
        self.line_sn = pn.Param(
            conf.param.line_sn,
            widgets={"line_sn": {"type": pn.widgets.Checkbox}},
        )
        self.line_flux = pn.Param(
            conf.param.line_flux,
            widgets={"line_flux": {"type": pn.widgets.FloatInput}},
        )
        self.line_width = pn.Param(
            conf.param.line_width,
            widgets={"line_width": {"type": pn.widgets.FloatInput}},
        )

        # Custom input spectrum
        self.custom_input = pn.Param(
            conf.param.custom_input,
            widgets={
                "custom_input": {"type": pn.widgets.FileInput},
                "accept": ".csv",
            },
        )
        self.custom_input_help = pn.pane.Markdown(
            """
            Input spectrum must be in a CSV format with exactly two columns.
            The first column must be the wavelength in [Å] and
            the second column must be the flux in [$$\mathrm{erg}$$ $$\mathrm{s}^{-1}$$ $$\mathrm{cm}^{-2}$$ $$\mathrm{Å}^{\ \ \ -1}$$]
            No header line is needed and lines starting with "#" are regarded as commment. An [example CSV file](https://gist.github.com/monodera/be48be04f376b2db268d0b14ad9cb5e1) is available.
            """,
            renderer="myst"
            # markdown-it', 'markdown', 'myst
        )

        # Misc. information
        self.galactic_extinction = pn.Param(
            conf.param.galactic_extinction,
            widgets={
                "galactic_extinction": {"type": pn.widgets.FloatInput, "format": "0.0"}
            },
        )
        self.r_eff = pn.Param(
            conf.param.r_eff,
            widgets={"r_eff": {"type": pn.widgets.FloatInput}},
        )

        # Put widgets into categories
        self.box_template = pn.WidgetBox(
            "### Target Information",
            pn.Column(self.template, self.mag, self.wavelength, self.redshift),
        )

        self.box_line = pn.WidgetBox(
            "### Emission Line Properties",
            pn.Column(
                # self.line_sn,
                self.line_flux,
                self.line_width,
            ),
        )

        self.box_custom_input = pn.WidgetBox(
            "### Custom Input Spectrum (.csv)",
            pn.Column(
                self.custom_input_help,
                self.custom_input,
            ),
        )
        self.box_misc = pn.WidgetBox(
            "### Miscellaneous Information",
            pn.Column(self.r_eff, self.galactic_extinction),
        )

        # Arrange into a layout
        self.panel = pn.Column(
            self.box_template,
            self.box_line,
            self.box_custom_input,
            self.box_misc,
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
            show_name=False,
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
            show_name=False,
            default_layout=pn.Column,
        )


class MatplotlibWidgets:
    def __init__(self, fig, dpi: int = 144, visible: bool = True):
        self.pane = pn.pane.Matplotlib(fig, dpi=dpi, visible=visible)


class BokehWidgets:
    def __init__(self, p, visible: bool = True):
        self.plot = pn.pane.Bokeh(p, visible=visible, sizing_mode="stretch_width")
        self.pane = pn.Column(self.plot)


class DownloadWidgets:
    def __init__(self, visible: bool = True):
        self.download_pfsobject_fits = pn.widgets.FileDownload(
            file=None,
            label="Download pfsObject file (.fits)",
            button_type="default",
            visible=visible,
            sizing_mode="stretch_height",
        )
        self.download_simspec_fits = pn.widgets.FileDownload(
            file=None,
            label="Download simulated spectrum (.fits)",
            button_type="default",
            visible=visible,
        )
        self.download_simspec_csv = pn.widgets.FileDownload(
            file=None,
            label="Download simulated spectrum (.ecsv)",
            button_type="default",
            visible=visible,
        )
        self.download_snline_fits = pn.widgets.FileDownload(
            file=None,
            label="Download emission line S/N (.fits)",
            button_type="default",
            visible=visible,
        )
        self.download_snline_csv = pn.widgets.FileDownload(
            file=None,
            label="Download emission line S/N (.ecsv)",
            button_type="default",
            visible=visible,
        )
        self.pane = pn.Row(
            pn.Column(
                pn.Row(self.download_simspec_fits, self.download_simspec_csv),
                pn.Row(self.download_snline_fits, self.download_snline_csv),
            ),
            pn.Column(self.download_pfsobject_fits),
        )
