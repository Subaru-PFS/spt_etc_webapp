#!/usr/bin/env python3

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.table import Column, QTable, Table
from bokeh.layouts import column
from bokeh.models import LinearAxis, Range1d
from bokeh.palettes import Colorblind
from bokeh.plotting import ColumnDataSource, figure


def load_simspec(infile: str) -> pd.DataFrame:
    df = pd.read_table(
        infile,
        sep="\s+",
        comment="#",
        header=None,
        # header=0,
        names=["wavelength", "flux", "error", "mask", "sky", "arm"],
        dtype={
            "wavelength": float,
            "flux": float,
            "error": float,
            "mask": int,
            "sky": float,
            "arm": int,
        },
    )
    return df


def load_snline(infile: str) -> pd.DataFrame:
    df = pd.read_table(
        infile,
        sep="\s+",
        comment="#",
        header=None,
        # header=0,
        names=[
            "wavelength",
            "fiber_aperture_factor",
            "effective_collecting_area",
            "snline_b",
            "snline_r",
            "snline_n",
            "snline_tot",
        ],
        dtype={
            "wavelength": float,
            "fiber_aperture_factor": float,
            "effective_collecting_area": float,
            "snline_b": float,
            "snline_r": float,
            "snline_n": float,
            "snline_tot": float,
        },
    )
    return df


def load_sncont(infile: str) -> pd.DataFrame:
    df = pd.read_table(
        infile,
        sep="\s+",
        comment="#",
        header=None,
        names=[
            "arm",
            "pixel",
            "wavelength",
            "sncont",
            "signal_per_exp",
            "noise_wo_obj_per_exp",
            "noise_w_obj_per_exp",
            "input_spec",
            "convfac_flux2e",
            "samplefac",
            "sky",
        ],
        dtype={
            "arm": int,
            "pixel": int,
            "wavelength": float,
            "sncont": float,
            "signal_per_exp": float,
            "noise_wo_obj_per_exp": float,
            "noise_w_obj_per_exp": float,
            "input_spec": float,
            "convfac_flux2e": float,
            "samplefac": float,
            "sky": float,
        },
    )
    return df


def create_dummy_plot(
    aspect_ratio: float = 1.5,
    outline_line_alpha: float = 0.0,
):
    p = None
    p = figure(
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        outline_line_alpha=outline_line_alpha,
    )
    p.toolbar.logo = None
    p.toolbar_location = None
    p.line([], [])

    return column(p)


def create_simspec_plot(
    df: pd.DataFrame,
    df_snline: pd.DataFrame,
    df_sncont: pd.DataFrame,
    aspect_ratio: float = 2.5,
):
    kwargs_simspec = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="Flux (nJy)",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
        active_drag="box_zoom",
    )
    kwargs_snline = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="S/N",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
        active_drag="box_zoom",
    )
    extra_y_axis_label = "S/N per pixel"

    input_spec = df_sncont["input_spec"].to_numpy()
    input_spec[np.isclose(input_spec, np.zeros_like(input_spec))] = np.nan
    input_spec = (input_spec * u.ABmag).to(u.nJy).value

    ymin, ymax = -np.nanmax(input_spec) * 0.2, np.nanmax(input_spec) * 2
    ymin2, ymax2 = 0.0, np.nanmax(df_sncont["sncont"]) * 1.5

    df["sncont"] = df_sncont["sncont"]
    df["input_spec"] = input_spec

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
        ("Input", "@input_spec"),
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
            alpha=0.8,
            legend_label="Flux",
        )
        # plot input spectrum
        p_arm.line(
            "wavelength",
            "input_spec",
            source=dict_source_arm[arm],
            color=dict_line_color[arm],
            # color="black",
            line_width=2,
            legend_label="Input",
        )
        # plot error
        p_arm.line(
            "wavelength",
            "error",
            source=dict_source_arm[arm],
            color="gray",
            alpha=0.8,
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
            # color=Colorblind[7][5],
            color=Colorblind[7][6],
            alpha=0.8,
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
        # color=Colorblind[7][4],
        color=Colorblind[7][6],
        legend_label="S/N",
    )
    p_snline.legend.location = "top_left"
    p_snline.legend.click_policy = "mute"

    return column(
        children=[p_simspec_b, p_simspec_r, p_simspec_n, p_simspec_m, p_snline]
    )


def create_simspec_files(
    param_target,
    param_env,
    param_inst,
    param_tel,
    df_simspec: pd.DataFrame,
    df_snline: pd.DataFrame,
    df_sncont: pd.DataFrame,
):
    if param_target.custom_input is None:
        template_type = param_target.template
        template_mag = param_target.mag
        template_wave = param_target.wavelength
        template_redshift = param_target.redshift
    else:
        template_type = "Custom"
        template_mag, template_wave, template_redshift = None, None, None
        # template_mag, template_wave, template_redshift = np.nan, np.nan, np.nan
        print(template_mag, template_wave, template_redshift)

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
    tb_out.meta["TMPLSPEC"] = (template_type, "Template type")
    tb_out.meta["TMPL_MAG"] = (template_mag, "[mag] AB mag to normalize template")
    tb_out.meta["TMPL_WAV"] = (
        template_wave,
        "[nm] Wavelength for normalizing template",
    )
    tb_out.meta["TMPL_Z"] = (template_redshift, "Reshift of the template")
    tb_out.meta["R_EFF"] = (
        param_target.r_eff,
        "[arcsec] Effective radius of the target",
    )
    tb_out.meta["EXPTIME"] = (
        param_inst.exp_time * param_inst.exp_num,
        "[s] Total exposure time",
    )
    tb_out.meta["EXPTIME1"] = (param_inst.exp_time, "[s] Single exposure time")
    tb_out.meta["EXPNUM"] = (param_inst.exp_num, "Number of exposures")
    tb_out.meta["SEEING"] = (param_env.seeing, "[arcsec] Seeing FWHM")
    tb_out.meta["ZANG"] = (param_tel.zenith_angle, "[degree] Zenith angle")
    tb_out.meta["MOON-ZA"] = (param_env.moon_zenith_angle, "[degree] Moon zenith angle")
    tb_out.meta["MOON-SEP"] = (
        param_env.moon_target_angle,
        "[degree] Moon-target separation",
    )
    tb_out.meta["MOON-PH"] = (
        param_env.moon_phase,
        "Moon phase (0=new, 0.25=quater, 1=new)",
    )
    tb_out.meta["FLDANG"] = (
        param_inst.field_angle,
        "[degree] PFS field angle (center=0, edge=0.675)",
    )
    tb_out.meta["DEGRADE"] = (param_env.degrade, "Throughput degradation factor")
    tb_out.meta["GAL_EXT"] = (
        param_target.galactic_extinction,
        "[mag] E(B-V) of Galactive extinction",
    )
    tb_out.meta["MED_RES"] = (param_inst.mr_mode, "True if medium resolution mode")

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
        description="Effective collecting area",
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
        param_target.line_flux,
        "[erg/s^(-1)/cm^(-2)] Emission line flux",
    )
    tb_snline.meta["EL_SIG"] = (
        param_target.line_width,
        "[km/s] Emission line width sigma",
    )
    tb_snline.meta["TMPLSPEC"] = (template_type, "Template type")
    tb_snline.meta["TMPL_MAG"] = (
        template_mag,
        "[mag] AB mag to normalize template",
    )
    tb_snline.meta["TMPL_WAV"] = (
        template_wave,
        "[nm] Wavelength for normalizing template",
    )
    tb_snline.meta["TMPL_Z"] = (template_redshift, "Reshift of the template")
    tb_snline.meta["R_EFF"] = (
        param_target.r_eff,
        "[arcsec] Effective radius of the target",
    )
    tb_snline.meta["EXPTIME"] = (
        param_inst.exp_time * param_inst.exp_num,
        "[s] Total exposure time",
    )
    tb_snline.meta["EXPTIME1"] = (param_inst.exp_time, "[s] Single exposure time")
    tb_snline.meta["EXPNUM"] = (param_inst.exp_num, "Number of exposures")
    tb_snline.meta["SEEING"] = (param_env.seeing, "[arcsec] Seeing FWHM")
    tb_snline.meta["ZANG"] = (param_tel.zenith_angle, "[degree] Zenith angle")
    tb_snline.meta["MOON-ZA"] = (
        param_env.moon_zenith_angle,
        "[degree] Moon zenith angle",
    )
    tb_snline.meta["MOON-SEP"] = (
        param_env.moon_target_angle,
        "[degree] Moon-target separation",
    )
    tb_snline.meta["MOON-PH"] = (
        param_env.moon_phase,
        "Moon phase (0=new, 0.25=quater, 1=new)",
    )
    tb_snline.meta["FLDANG"] = (
        param_inst.field_angle,
        "[degree] PFS field angle (center=0, edge=0.675)",
    )
    tb_snline.meta["DEGRADE"] = (param_env.degrade, "Throughput degradation factor")
    tb_snline.meta["GAL_EXT"] = (
        param_target.galactic_extinction,
        "[mag] E(B-V) of Galactive extinction",
    )
    tb_snline.meta["MED_RES"] = (param_inst.mr_mode, "True if medium resolution mode")

    tj_text = f"""The following parameters are used with the PFS spectral simulator:
[1] Template spectrum: {template_type};
[2] AB mag: {template_mag};
[3] Wavelength: {template_wave};
[4] Redshift: {template_redshift};
[5] (1) Emission line flux: {param_target.line_flux}, (2) Emission line width {param_target.line_width};
[6] (1) Galactic extinction: {param_target.galactic_extinction}, (2) Effective radius: {param_target.r_eff};
[7] Seeing FWHM: {param_env.seeing};
[8] Throughput degradation factor: {param_env.degrade};
[9] Moon zenith angle: {param_env.moon_zenith_angle};
[10] Moon-target separation: {param_env.moon_target_angle};
[11] Moon phase: {param_env.moon_phase};
[12] Exposure time: {param_inst.exp_time};
[13] Number of exposures: {param_inst.exp_num};
[14] Distance from FoV center: {param_inst.field_angle};
[15] Zenith angle: {param_tel.zenith_angle};
"""

    return tb_out, tb_snline, tj_text
