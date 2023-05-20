#!/usr/bin/env python3

import numpy as np
from astropy import units as u
from astropy.table import Column, QTable, Table
from bokeh.layouts import column
from bokeh.models import LinearAxis, Range1d
from bokeh.palettes import Colorblind
from bokeh.plotting import ColumnDataSource, figure


def create_dummy_plot(aspect_ratio=1.5, outline_line_alpha=0.0):
    p = None
    p = figure(
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        outline_line_alpha=outline_line_alpha,
        # outline_line_color="red",
        # outline_line_width=0,
        # border_fill_color="red"
        # width=0,
        # height=0,
    )
    p.toolbar.logo = None
    p.toolbar_location = None
    p.line([], [])

    return column(p)


def create_simspec_plot(df, df_snline, df_sncont, aspect_ratio=2.5):
    kwargs_simspec = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="Flux (nJy)",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
    )
    kwargs_snline = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="S/N",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
    )
    extra_y_axis_label = "S/N per pixel"

    input_spec = df_sncont["input_spec"].to_numpy()
    input_spec[np.isclose(input_spec, np.zeros_like(input_spec))] = np.nan
    input_spec = (input_spec * u.ABmag).to(u.nJy).value

    ymin, ymax = -np.nanmax(input_spec) * 0.2, np.nanmax(input_spec) * 2
    ymin2, ymax2 = 0.0, np.nanmax(df_sncont["sncont"]) * 1.5

    df["sncont"] = df_sncont["sncont"]

    dict_df_arm = dict(
        b=df.loc[df["arm"] == 0, :],
        r=df.loc[df["arm"] == 1, :],
        n=df.loc[df["arm"] == 2, :],
        m=df.loc[df["arm"] == 3, :],
    )

    dict_source_arm = dict(
        b=ColumnDataSource(dict_df_arm["b"]),
        r=ColumnDataSource(dict_df_arm["r"]),
        n=ColumnDataSource(dict_df_arm["n"]),
        m=ColumnDataSource(dict_df_arm["m"]),
    )

    dict_line_color = dict(
        b=Colorblind[7][0],
        r=Colorblind[7][3],
        n=Colorblind[7][1],
        m=Colorblind[7][6],
    )

    tooltips = [
        ("Wavelength", "@wavelength"),
        ("Flux", "@flux"),
        ("Error", "@error"),
        ("S/N", "@sncont"),
    ]
    tooltips_snline = [
        ("Wavelength", "@wavelength"),
        ("S/N", "@snline_tot"),
    ]

    p_simspec_b = figure(
        title="Blue arm",
        x_range=[380, 650],
        y_range=[ymin, ymax],
        tooltips=tooltips,
        **kwargs_simspec,
    )
    p_simspec_r = figure(
        title="Red arm",
        x_range=[630, 970],
        y_range=[ymin, ymax],
        tooltips=tooltips,
        **kwargs_simspec,
    )
    p_simspec_n = figure(
        title="Near-IR arm",
        x_range=[940, 1260],
        y_range=[ymin, ymax],
        tooltips=tooltips,
        **kwargs_simspec,
    )
    p_simspec_m = figure(
        title="Medium resolution arm",
        x_range=[710, 885],
        y_range=[ymin, ymax],
        tooltips=tooltips,
        **kwargs_simspec,
    )

    p_snline = figure(
        title="Emission Line S/N",
        x_range=[380, 1260],
        tooltips=tooltips_snline,
        **kwargs_snline,
    )

    for arm, p_arm in zip(
        ["b", "r", "n", "m"], [p_simspec_b, p_simspec_r, p_simspec_n, p_simspec_m]
    ):
        # plot flux
        p_arm.line(
            "wavelength",
            "flux",
            source=dict_source_arm[arm],
            color=dict_line_color[arm],
            legend_label="Flux",
        )
        # plot error
        p_arm.line(
            "wavelength",
            "error",
            source=dict_source_arm[arm],
            color="gray",
            legend_label="Error",
        )
        # plot S/N using the right-side axis
        p_arm.extra_y_ranges = {"sncont": Range1d(start=ymin2, end=ymax2)}
        p_arm.add_layout(
            LinearAxis(y_range_name="sncont", axis_label=extra_y_axis_label),
            "right",
        )
        p_arm.line(
            "wavelength",
            "sncont",
            source=dict_source_arm[arm],
            color=Colorblind[7][5],
            alpha=0.75,
            y_range_name="sncont",
            legend_label="S/N",
        )
        p_arm.legend.location = "top_left"
        p_arm.legend.click_policy = "mute"
        p_arm.legend.orientation = "horizontal"

    p_snline.line(
        "wavelength",
        "snline_tot",
        source=df_snline,
        color=Colorblind[7][4],
        legend_label="S/N",
    )
    p_snline.legend.location = "top_left"
    p_snline.legend.click_policy = "mute"

    return column(
        children=[p_simspec_b, p_simspec_r, p_simspec_n, p_simspec_m, p_snline]
    )


def create_simspec_files(params, df_simspec, df_snline, df_sncont):
    # initialize output table
    tb_out = QTable()
    tb_out["wavelength"] = Column(
        df_simspec["wavelength"].to_numpy(),
        unit="nm",
        description="Wavelength in vacuum (nm)",
    )
    tb_out["flux"] = Column(
        df_simspec["flux"].to_numpy(), unit="nJy", description="Flux (nJy)"
    )
    tb_out["error"] = Column(
        df_simspec["error"].to_numpy(), unit="nJy", description="Error (nJy)"
    )
    tb_out["sn"] = Column(
        df_sncont["sncont"].to_numpy(),
        dtype=float,
        unit="pix^-1",
        description="S/N per pixel",
    )
    tb_out["flux_input"] = Column(
        (df_sncont["input_spec"].to_numpy() * u.ABmag).to(u.nJy),
        dtype=float,
        description="Input flux (nJy)",
    )
    tb_out["sky"] = Column(df_simspec["sky"], unit="nJy", description="Sky (nJy)")
    tb_out["mask"] = Column(
        df_simspec["mask"], dtype=bool, description="Masked if True"
    )
    tb_out["arm"] = Column(
        df_simspec["arm"], dtype=int, description="Arm ID (0=blue, 1=red, 2=nir, 3=mr)"
    )
    tb_out["pixel"] = Column(
        df_sncont["pixel"], dtype=int, description="Pixel ID in each arm"
    )

    # add meta data
    tb_out.meta["EXPTIME"] = (params["EXP_TIME"], "[s] Single exposure time")
    tb_out.meta["EXPNUM"] = (params["EXP_NUM"], "Number of exposures")
    tb_out.meta["SEEING"] = (params["SEEING"], "[arcsec] Seeing FWHM")
    tb_out.meta["ZANG"] = (params["ZENITH_ANG"], "[degree] Zenith angle")
    tb_out.meta["MOON-ZA"] = (params["MOON_ZENITH_ANG"], "[degree] Moon zenith angle")
    tb_out.meta["MOON-SEP"] = (
        params["MOON_TARGET_ANG"],
        "[degree] Moon-target separation",
    )
    tb_out.meta["MOON-PH"] = (
        params["MOON_PHASE"],
        "Moon phase (0=new, 0.25=quater, 1=new)",
    )
    tb_out.meta["FLDANG"] = (
        params["FIELD_ANG"],
        "[degree] PFS field angle (center=0, edge=0.675)",
    )
    tb_out.meta["DEGRADE"] = (params["degrade"], "Throughput degradation factor")
    tb_out.meta["R_EFF"] = (params["REFF"], "[arcsec] Effective radius of the target")
    tb_out.meta["GAL_EXT"] = (
        params["GALACTIC_EXT"],
        "[mag] E(B-V) of Galactive extinction",
    )

    # initialize a table for emission line S/N
    tb_snline = QTable()
    tb_snline["wavelength"] = Column(
        df_snline["wavelength"].to_numpy(),
        unit="nm",
        description="Wavelength in vacuum (nm)",
    )
    tb_snline["fiber_aperture_factor"] = Column(
        df_snline["fiber_aperture_factor"].to_numpy(),
        dtype=float,
        description="Fiber aperture factor",
    )
    tb_snline["effective_collecting_are"] = Column(
        df_snline["effective_collecting_area"].to_numpy(),
        unit="m^2",
        description="Fiber aperture factor",
    )
    tb_snline["snline_b"] = Column(
        df_snline["snline_b"],
        dtype=float,
        description="Emission line S/N in the blue arm",
    )
    tb_snline["snline_r"] = Column(
        df_snline["snline_r"],
        dtype=float,
        description="Emission line S/N in the red arm",
    )
    tb_snline["snline_n"] = Column(
        df_snline["snline_n"],
        dtype=float,
        description="Emission line S/N in the near-IR arm",
    )
    tb_snline["snline_tot"] = Column(
        df_snline["snline_tot"],
        dtype=float,
        description="Total emission line S/N",
    )
    # add meta data
    tb_snline.meta["EL_FLUX"] = (
        params["LINE_FLUX"],
        "[erg/s^(-1)/cm^(-2)] Emission line flux",
    )
    tb_snline.meta["EL_SIG"] = (
        params["LINE_WIDTH"],
        "[km/s] Emission line width sigma",
    )
    tb_snline.meta["EXPTIME"] = (params["EXP_TIME"], "[s] Single exposure time")
    tb_snline.meta["EXPNUM"] = (params["EXP_NUM"], "Number of exposures")
    tb_snline.meta["SEEING"] = (params["SEEING"], "[arcsec] Seeing FWHM")
    tb_snline.meta["ZANG"] = (params["ZENITH_ANG"], "[degree] Zenith angle")
    tb_snline.meta["MOON-ZA"] = (
        params["MOON_ZENITH_ANG"],
        "[degree] Moon zenith angle",
    )
    tb_snline.meta["MOON-SEP"] = (
        params["MOON_TARGET_ANG"],
        "[degree] Moon-target separation",
    )
    tb_snline.meta["MOON-PH"] = (
        params["MOON_PHASE"],
        "Moon phase (0=new, 0.25=quater, 1=new)",
    )
    tb_snline.meta["FLDANG"] = (
        params["FIELD_ANG"],
        "[degree] PFS field angle (center=0, edge=0.675)",
    )
    tb_snline.meta["DEGRADE"] = (params["degrade"], "Throughput degradation factor")
    tb_snline.meta["R_EFF"] = (
        params["REFF"],
        "[arcsec] Effective radius of the target",
    )
    tb_snline.meta["GAL_EXT"] = (
        params["GALACTIC_EXT"],
        "[mag] E(B-V) of Galactive extinction",
    )

    return tb_out, tb_snline

    # tb_out[:10].write(sys.stdout, format="ascii.ecsv", delimiter=",")
    # tb_out.write(
    #     "test_download.ecsv", format="ascii.ecsv", delimiter=",", overwrite=True
    # )
    # tb_out.write("test_download.fits", format="fits", overwrite=True)

    # tb_snline.write(
    #     "test_download2.ecsv", format="ascii.ecsv", delimiter=",", overwrite=True
    # )
    # tb_snline.write("test_download2.fits", format="fits", overwrite=True)

    pass
