#!/usr/bin/env python3

import numpy as np
import panel as pn
import param
from loguru import logger


class InitNoteWidgets:
    def __init__(self):
        self.flatpanel = pn.layout.FloatPanel(
            pn.pane.Markdown(
                """
            - This is a development version of a PFS spectral simulator web app using [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/).
            - Documentation is available [here](doc/index.html)
            - Updates may be deployed frequently without any notification, please reload the web site if the app freezes.
            - Feedback would be appreciated. Please feel free to contact either at `obsproc` Slack channel on PFS Slack or by email to Masato Onodera (<monodera@naoj.org>) (Subaru Telescope).
        """,
                # renderer="myst",
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
        self.doc = pn.pane.Markdown(
            "<font size='3'><i class='fa-solid fa-circle-info fa-lg' style='color: #6A589D;'></i> <a href='doc/index.html' target='_blank'>User Guide</a></font>",
        )
        self.pane = pn.Column(self.doc, pn.Row(self.reset, self.exec, height=50))


class TargetWidgets(param.Parameterized):
    def __init__(self, conf):
        self.template = pn.Param(
            conf.param.template,
            widgets={
                "template": {
                    "type": pn.widgets.Select,
                    "groups": {
                        "Galaxy": [
                            "SSP (100 Myr, [M/H]=0, Chabrier IMF)",
                            "SSP (1 Gyr, [M/H]=0, Chabrier IMF)",
                            "Elliptical 2 Gyr",
                            "Elliptical 5 Gyr",
                            "Elliptical 13 Gyr",
                            "S0",
                            "Sa",
                            "Sb",
                            "Sc",
                            "Sd",
                            "Sdm",
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
        self.line_help = pn.pane.Markdown(
            "Emission line S/N is computed at each wavelength pixel based on the noise vector including continuum. "
            "Set the input magnitude to a large value, if you want to know continuum-free, emission line-only S/N."
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
            "Input spectrum must be in a CSV format with exactly two columns. "
            "The first column must be the wavelength in [Å] and "
            "the second column must be the flux in [$$\mathrm{erg}$$ $$\mathrm{s}^{-1}$$ $$\mathrm{cm}^{-2}$$ $$\mathrm{Å}^{\ \ \ -1}$$]. "
            'No header line is needed and lines starting with "#" are regarded as commment. An [example CSV file](https://gist.github.com/monodera/be48be04f376b2db268d0b14ad9cb5e1) is available.',
            # renderer="myst"
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
                self.line_help,
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
            # width=400,
            # sizing_mode="stretch_width",
        )

    def disabled(self, disabled=True):
        for w in [
            self.box_template,
            self.box_line,
            self.box_custom_input,
            self.box_misc,
        ]:
            w.disabled = disabled


class EnvironmentWidgets(param.Parameterized):
    def __init__(self, conf):
        # super().__init__()
        self.conf = conf
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
                    "step": 0.1,
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

    def disabled(self, disabled=True):
        for p in self.panel.parameters:
            self.conf.param[p].constant = disabled


class InstrumentWidgets(param.Parameterized):
    def __init__(self, conf):
        self.conf = conf
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

    def disabled(self, disabled=True):
        for p in self.panel.parameters:
            self.conf.param[p].constant = disabled


class TelescopeWidgets(param.Parameterized):
    def __init__(self, conf):
        self.conf = conf
        self.panel = pn.Param(
            conf,
            widgets={"zenith_angle": {"type": pn.widgets.IntSlider, "step": 5}},
            show_name=False,
            default_layout=pn.Column,
        )

    def disabled(self, disabled=True):
        for p in self.panel.parameters:
            self.conf.param[p].constant = disabled


class MatplotlibWidgets:
    def __init__(self, fig, dpi: int = 144, visible: bool = True):
        self.pane = pn.pane.Matplotlib(fig, dpi=dpi, visible=visible)


class BokehWidgets:
    def __init__(self, p, visible: bool = True, max_height: int = 1080):
        self.plot = pn.pane.Bokeh(
            p,
            visible=visible,
            width=1200,
        )
        self.plot_heading = pn.pane.Markdown(
            "<font size=4>**Simulated PFS Spectrum**</font>", visible=visible
        )
        self.pane = pn.Column(
            self.plot_heading,
            self.plot,
            min_width=700,
            width=1200,
        )


class DownloadWidgets:
    def __init__(self, visible: bool = True):
        self.download_pfsobject_fits = pn.widgets.FileDownload(
            file=None,
            label="pfsObject file (.fits)",
            button_type="default",
            visible=visible,
        )
        self.download_simspec_fits = pn.widgets.FileDownload(
            file=None,
            label="Simulated spectrum (.fits)",
            button_type="default",
            visible=visible,
        )
        self.download_simspec_csv = pn.widgets.FileDownload(
            file=None,
            label="Simulated spectrum (.ecsv)",
            button_type="default",
            visible=visible,
        )
        self.download_snline_fits = pn.widgets.FileDownload(
            file=None,
            label="Emission line S/N (.fits)",
            button_type="default",
            visible=visible,
        )
        self.download_snline_csv = pn.widgets.FileDownload(
            file=None,
            label="Emission line S/N (.ecsv)",
            button_type="default",
            visible=visible,
        )
        self.download_tjtext = pn.widgets.FileDownload(
            file=None,
            label="TJ template (.txt)",
            button_type="default",
            # button_type="primary",
            # button_style="outline",
            visible=visible,
        )
        # self.download_heading = pn.pane.Markdown("## Download Results", visible=visible)
        self.download_heading = pn.pane.Markdown(
            "<font size=4>**Download Results**</font>",
            visible=visible,
        )

        self.simulation_id_text = pn.pane.Markdown(
            "<font size=4>**Simulation ID: None**</font>",
            visible=visible,
            # margin=(0, 0, 0, 0),
            # width=600,
        )
        # self.simulation_id_button = pn.widgets.ButtonIcon(
        #     icon="copy",
        #     width=40,
        #     visible=visible,
        #     align="center",
        # )

        self.pane = pn.Column(
            pn.Row(
                self.simulation_id_text,
                # self.simulation_id_button,
                # pn.HSpacer(),
            ),
            self.download_heading,
            pn.Row(
                self.download_simspec_fits,
                self.download_simspec_csv,
                self.download_pfsobject_fits,
            ),
            pn.Row(
                self.download_snline_fits,
                self.download_snline_csv,
                self.download_tjtext,
            ),
            width=1200,
        )

    def update_simulation_id(self, simulation_id: str):
        self.simulation_id_text.object = (
            f"<font size=4>**Simulation ID: {simulation_id}**</font>"
        )

        # copy_source_code = "navigator.clipboard.writeText(source);"
        # self.simulation_id_button.js_on_click(
        #     args={"source": simulation_id},
        #     code=copy_source_code,
        # )

        logger.info(f"Simulation ID: {simulation_id}")
