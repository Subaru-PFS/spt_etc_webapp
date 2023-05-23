#!/usr/bin/env python3

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
            width=70,
            height=25,
            styles={
                "display": "inline-block",
                # "padding": "1px 0px",
                # "background-color": "#4CAF50",
                # "background-color": "#f3f3f3",
                "border-radius": "5px",
                # "border-style": "solid",
                # "border-color": "#ffffff",
                "text-align": "center",
                "text-decoration": "none",
                "font-size": "110%",
            },
        )
        self.pane = pn.Row(self.doc, self.reset, self.exec, height=40)


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
                        "Star": ["B0V", "A0V", "G2V"],
                        "Misc": ["Flat in frequency"],
                    },
                },
            },
        )
        _mag = pn.Param(
            conf.param.mag,
            widgets={"mag": {"type": pn.widgets.FloatInput}},
        )
        _wavelength = pn.Param(
            conf.param.wavelength,
            widgets={"wavelength": {"type": pn.widgets.FloatInput}},
        )
        _redshift = pn.Param(
            conf.param.redshift,
            widgets={"redshift": {"type": pn.widgets.FloatInput}},
        )
        _line_flux = pn.Param(
            conf.param.line_flux,
            widgets={"line_flux": {"type": pn.widgets.FloatInput}},
        )
        _line_width = pn.Param(
            conf.param.line_width,
            widgets={"line_width": {"type": pn.widgets.FloatInput}},
        )

        # Custom input spectrum
        _custom_input = pn.Param(
            conf.param.custom_input,
            widgets={
                "custom_input": {"type": pn.widgets.FileInput},
                "accept": ".csv",
            },
        )
        _custom_input_help = pn.pane.Markdown(
            # r"$$\frac{1}{n}$$",
            """
            Input spectrum must be in a CSV format with exactly two columns.
            The first column must be the wavelength in [$$\mathrm{A}$$] and
            the second column must be the flux in [$$\mathrm{erg}$$ $$\mathrm{s}^{-1}$$ $$\mathrm{cm}^{-2}$$ $$\mathrm{A}^{-1}$$]
            No header line is needed and lines starting with "#" are regarded as commment. An [example CSV file](https://gist.github.com/monodera/be48be04f376b2db268d0b14ad9cb5e1) is available.
            """,
            renderer="myst"
            # markdown-it', 'markdown', 'myst
        )

        # Misc. information
        _galactic_extinction = pn.Param(
            conf.param.galactic_extinction,
            widgets={
                "galactic_extinction": {"type": pn.widgets.FloatInput, "format": "0.0"}
            },
        )
        _r_eff = pn.Param(
            conf.param.r_eff,
            widgets={"r_eff": {"type": pn.widgets.FloatInput}},
        )

        # Put widgets into categories
        _box_template = pn.WidgetBox(
            "### Target Information",
            pn.Column(_template, _mag, _wavelength, _redshift),
        )

        _box_line = pn.WidgetBox(
            "### Emission Line Properties",
            pn.Column(_line_flux, _line_width),
        )

        _box_custom_input = pn.WidgetBox(
            "### Custom Input Spectrum (.csv)",
            pn.Column(
                _custom_input_help,
                _custom_input,
            ),
        )
        # _box_custom_input = pn.WidgetBox(
        #     "### Custom Input Spectrum (.csv)",
        #     pn.Column(
        #         _custom_input,
        #         _custom_input_help,
        #     ),
        # )
        _box_misc = pn.WidgetBox(
            "### Miscellaneous Information",
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
        self.pane = pn.Column(
            pn.Row(self.download_simspec_fits, self.download_simspec_csv),
            pn.Row(self.download_snline_fits, self.download_snline_csv),
        )
