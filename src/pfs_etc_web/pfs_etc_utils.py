#!/usr/bin/env python3

import os

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.table import Column, QTable
from bokeh.layouts import column
from bokeh.models import BooleanFilter, CDSView, LinearAxis, Range1d
from bokeh.palettes import Colorblind
from bokeh.plotting import ColumnDataSource, figure
from loguru import logger

from . import PfsArm


def _looks_like_ecsv(infile: str) -> bool:
    try:
        with open(infile) as f:
            for _ in range(20):
                line = f.readline()
                if line == "":
                    break
                if line.startswith("# %ECSV"):
                    return True
    except (OSError, UnicodeDecodeError):
        return False
    return False


def _quantity_to_unit(tb: QTable, colname: str, unit: u.Unit) -> None:
    """Normalize a QTable column to `unit` in place, if it carries a unit.

    QTable.to_pandas() drops astropy units entirely, returning the raw
    stored value. Without this, an ECSV file that stores wavelength in a
    unit other than the one the rest of the pipeline assumes would be
    silently misinterpreted.
    """
    if colname in tb.colnames and getattr(tb[colname], "unit", None) is not None:
        tb[colname] = tb[colname].to(unit)


def _cast_columns(
    df: pd.DataFrame, dtype: dict[str, type], infile: str
) -> pd.DataFrame:
    """astype(dtype), raising a clear error instead of a confusing pandas
    exception when a column destined for an int dtype contains NaN."""
    for col, col_type in dtype.items():
        if col_type is int and df[col].isna().any():
            raise ValueError(
                f"Column '{col}' in {infile} contains missing values "
                "and cannot be cast to int"
            )
    return df.astype(dtype)


def _load_ecsv(
    infile: str,
    names: list[str],
    dtype: dict[str, type],
    build_rename_map,
    fill_missing_with_nan: bool = False,
    wavelength_columns: tuple[str, ...] = ("wavelength",),
) -> pd.DataFrame:
    """Shared scaffold for the three ECSV loaders below: read the table,
    normalize wavelength units, rename columns to the target schema, then
    validate/select/cast. `build_rename_map(columns, infile)` computes the
    rename dict from the table's actual columns, since which source column
    maps to which target column can depend on what's present (e.g. LR vs
    MR mode in load_snline)."""
    tb = QTable.read(infile, format="ascii.ecsv")
    for col in wavelength_columns:
        _quantity_to_unit(tb, col, u.nm)
    df = tb.to_pandas()
    df = df.rename(columns=build_rename_map(df.columns, infile))
    if fill_missing_with_nan:
        for col in names:
            if col not in df.columns:
                df[col] = np.nan
    if not set(names).issubset(df.columns):
        raise ValueError(f"Unsupported columns in {infile}: {list(df.columns)}")
    return _cast_columns(df[names], dtype, infile)


def _first_data_line_has_header(infile: str) -> bool:
    """Peek at the first non-comment, non-blank line to see whether it is
    a literal column-name header rather than numeric data."""
    with open(infile) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            tokens = stripped.split()
            try:
                [float(token) for token in tokens]
            except ValueError:
                return True
            return False
    return False


def _read_legacy_ascii_with_optional_header(
    infile: str,
    names: list[str],
    dtype: dict[str, type],
) -> pd.DataFrame:
    if not _first_data_line_has_header(infile):
        return pd.read_table(
            infile,
            sep=r"\s+",
            comment="#",
            header=None,
            names=names,
            dtype=dtype,
        )

    # Some legacy outputs include an uncommented header row.
    df = pd.read_table(
        infile,
        sep=r"\s+",
        comment="#",
        header=0,
    )
    if not set(names).issubset(df.columns):
        raise ValueError(f"Unsupported legacy columns in {infile}: {list(df.columns)}")
    return _cast_columns(df[names], dtype, infile)


def load_simspec(infile: str) -> pd.DataFrame:
    names = ["wavelength", "flux", "error", "mask", "sky", "arm"]
    dtype = {
        "wavelength": float,
        "flux": float,
        "error": float,
        "mask": int,
        "sky": float,
        "arm": int,
    }

    if _looks_like_ecsv(infile):
        df = _load_ecsv(
            infile,
            names,
            dtype,
            build_rename_map=lambda cols, infile: {
                "WAVELENGTH": "wavelength",
                "FLUX": "flux",
                "ERROR": "error",
                "MASK": "mask",
                "SKY": "sky",
                "ARM": "arm",
            },
            wavelength_columns=("wavelength", "WAVELENGTH"),
        )
    else:
        df = _read_legacy_ascii_with_optional_header(infile, names, dtype)

    return df


def load_snline(infile: str) -> pd.DataFrame:
    names = [
        "wavelength",
        "fiber_aperture_factor",
        "effective_collecting_area",
        "snline_b",
        "snline_r",
        "snline_n",
        "snline_tot",
    ]
    dtype = {
        "wavelength": float,
        "fiber_aperture_factor": float,
        "effective_collecting_area": float,
        "snline_b": float,
        "snline_r": float,
        "snline_n": float,
        "snline_tot": float,
    }

    def _snline_rename_map(cols, infile):
        rename_map = {
            "effective_area": "effective_collecting_area",
            "snr_b": "snline_b",
            "snr_n": "snline_n",
            "snr_tot": "snline_tot",
        }
        # snr_r (LR mode) and snr_m (MR mode) are mutually exclusive arm
        # columns that both map onto snline_r; guard against a file that
        # unexpectedly carries both, which would otherwise collide into a
        # single duplicated column name after rename.
        if "snr_r" in cols and "snr_m" in cols:
            raise ValueError(
                f"Unsupported snline columns in {infile}: "
                "both snr_r and snr_m are present"
            )
        elif "snr_r" in cols:
            rename_map["snr_r"] = "snline_r"
        elif "snr_m" in cols:
            rename_map["snr_m"] = "snline_r"
        return rename_map

    if _looks_like_ecsv(infile):
        # Fill missing arm columns in MR mode with NaN where needed.
        df = _load_ecsv(
            infile, names, dtype, _snline_rename_map, fill_missing_with_nan=True
        )
    else:
        df = _read_legacy_ascii_with_optional_header(infile, names, dtype)

    return df


def load_sncont(infile: str) -> pd.DataFrame:
    names = [
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
    ]
    dtype = {
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
    }

    if _looks_like_ecsv(infile):
        df = _load_ecsv(
            infile,
            names,
            dtype,
            build_rename_map=lambda cols, infile: {
                "snr": "sncont",
                "signal": "signal_per_exp",
                "noise_variance": "noise_wo_obj_per_exp",
                "noise_variance_tot": "noise_w_obj_per_exp",
                "input_mag": "input_spec",
                "conversion_factor": "convfac_flux2e",
                "sampling_factor": "samplefac",
            },
        )
    else:
        df = _read_legacy_ascii_with_optional_header(infile, names, dtype)

    # saturation counts
    # CCDs: ~50000 e-, H4RGs ~80000-100000 e- (As a upper limit for good linearity)
    # The pixel scale to enclose 90% of the flux is 1.8 pixels in radius.
    # Then the flux at the central pixel is 0.35 times the total flux in the profile.
    # The conversion factor from the profile to a pixel is 0.35.
    total2perpixel = 0.35  # conversion factor from the profile to a pixel
    fudge_factor = 0.9  # fudge factor to make buffers for saturation counts
    saturation_thresh_ccd = 50000.0 / total2perpixel * fudge_factor
    saturation_thresh_h4rg = 80000.0 / total2perpixel * fudge_factor
    SATURATION_THRESH = {
        PfsArm.b: saturation_thresh_ccd,
        PfsArm.r: saturation_thresh_ccd,
        PfsArm.n: saturation_thresh_h4rg,
        PfsArm.m: saturation_thresh_ccd,
    }
    is_saturated = np.zeros_like(df["wavelength"], dtype=bool)

    for arm, thresh in SATURATION_THRESH.items():
        is_saturated[
            np.logical_and(df["arm"] == arm.value, df["signal_per_exp"] > thresh)
        ] = True

    df["is_saturated"] = is_saturated

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


ARM_PLOT_SPECS = {
    "b": {"title": "Blue arm", "x_range": [380, 650], "color": Colorblind[7][0]},
    "r": {"title": "Red arm", "x_range": [630, 970], "color": Colorblind[7][3]},
    "n": {"title": "Near-IR arm", "x_range": [940, 1260], "color": Colorblind[7][1]},
    "m": {
        "title": "Medium resolution arm",
        "x_range": [710, 885],
        "color": Colorblind[7][6],
    },
}


def _active_arm_keys(mr_mode: bool) -> list[str]:
    """Arm plot keys to display, in wavelength order.

    The ETC computes at most 3 arms per run (n_workers is capped to 3 in
    pfsspecsim's Etc.run()), so r (normal resolution) and m (medium
    resolution) are mutually exclusive depending on ``mr_mode``.
    """
    return ["b", "m" if mr_mode else "r", "n"]


def create_simspec_plot(
    df: pd.DataFrame,
    df_snline: pd.DataFrame,
    df_sncont: pd.DataFrame,
    mr_mode: bool,
    aspect_ratio: float = 2.5,
):
    kwargs_simspec = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="Flux (nJy)",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_drag="box_zoom",
    )
    kwargs_snline = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="S/N",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_drag="box_zoom",
    )
    extra_y_axis_label = "S/N per pixel"

    # pandas 3 may return a read-only array from to_numpy(); copy for safe mutation.
    input_spec = df_sncont["input_spec"].to_numpy(copy=True)
    input_spec[np.isclose(input_spec, np.zeros_like(input_spec))] = np.nan
    input_spec = (input_spec * u.ABmag).to(u.nJy).value

    ymin, ymax = -np.nanmax(input_spec) * 0.2, np.nanmax(input_spec) * 2
    ymin2, ymax2 = 0.0, np.nanmax(df_sncont["sncont"]) * 1.5

    df["sncont"] = df_sncont["sncont"]
    df["is_saturated"] = df_sncont["is_saturated"]
    df["input_spec"] = input_spec

    # The ETC computes at most 3 arms per run (n_workers is capped to 3),
    # so r and m are mutually exclusive. Only build the arm that's
    # actually active, in wavelength order.
    arm_keys = _active_arm_keys(mr_mode)

    dict_df_arm = {key: df.loc[df["arm"] == PfsArm[key].value, :] for key in arm_keys}
    dict_source_arm = {key: ColumnDataSource(dict_df_arm[key]) for key in arm_keys}

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

    figures = {}
    for key in arm_keys:
        spec = ARM_PLOT_SPECS[key]
        figures[key] = figure(
            title=spec["title"],
            x_range=spec["x_range"],
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

    for arm in arm_keys:
        p_arm = figures[arm]
        color = ARM_PLOT_SPECS[arm]["color"]

        # plot flux
        p_arm.line(
            "wavelength",
            "flux",
            source=dict_source_arm[arm],
            color=color,
            alpha=0.8,
            legend_label="Flux",
        )
        # plot input spectrum
        p_arm.line(
            "wavelength",
            "input_spec",
            source=dict_source_arm[arm],
            color=color,
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
        # indicate saturated pixels
        if np.any(dict_df_arm[arm]["is_saturated"]):
            logger.info(f"Saturated pixels in {arm} arm detected.")

            n_sat_sample = 15
            if np.sum(dict_df_arm[arm]["is_saturated"]) < n_sat_sample:
                n_sat_sample = 1
            logger.info(
                f"One in every {n_sat_sample} saturated datapoints are plotted as flagged."
            )
            flag_saturate = np.zeros_like(dict_df_arm[arm]["is_saturated"], dtype=bool)
            flag_saturate[::n_sat_sample] = dict_df_arm[arm]["is_saturated"][
                ::n_sat_sample
            ].to_numpy()

            p_arm.scatter(
                "wavelength",
                "input_spec",
                source=dict_source_arm[arm],
                view=CDSView(
                    filter=BooleanFilter(flag_saturate),
                ),
                marker="circle_x",
                fill_color=None,
                line_color="orangered",
                size=10,
                alpha=0.8,
                legend_label="Saturated",
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
        color=Colorblind[7][6],
        legend_label="S/N",
    )
    p_snline.legend.location = "top_left"
    p_snline.legend.click_policy = "mute"

    return column(children=[figures[key] for key in arm_keys] + [p_snline])


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
        logger.info("Custom input is used.")
        template_type = "Custom"
        template_mag, template_wave, template_redshift = None, None, None
        # template_mag, template_wave, template_redshift = np.nan, np.nan, np.nan
        # logger.info(template_mag, template_wave, template_redshift)

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
    tb_out["saturated"] = Column(
        df_sncont["is_saturated"].to_numpy(),
        dtype=bool,
        description="Saturated continuum flux if True",
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


def recover_simulation(
    simulation_id,
    conf_target,
    conf_environment,
    conf_instrument,
    conf_telescope,
    conf_output,
    logger,
):
    dir = conf_output.basedir

    # load the simulation results
    filename_cont = f"pfs_etc_simspec-{simulation_id}.ecsv"
    filename_line = f"pfs_etc_snline-{simulation_id}.ecsv"

    # Validate simulation_id format (must be YYYYMMDD-HHMMSS-...)
    if len(simulation_id) < 8 or not simulation_id[:8].isdigit():
        logger.error(
            f"Invalid simulation_id format: {simulation_id}. "
            "Expected YYYYMMDD-HHMMSS-... format."
        )
        return None, False, None

    # Extract year and month from simulation_id
    year = simulation_id[:4]
    month = simulation_id[4:6]
    session_path = os.path.join(dir, year, month, simulation_id)

    try:

        tb_cont = QTable.read(os.path.join(session_path, filename_cont))
        tb_line = QTable.read(os.path.join(session_path, filename_line))

        if tb_cont.meta["TMPLSPEC"][0] != "Custom":
            conf_target.template = tb_cont.meta["TMPLSPEC"][0]
            conf_target.mag = tb_cont.meta["TMPL_MAG"][0]
            conf_target.wavelength = tb_cont.meta["TMPL_WAV"][0]
            conf_target.redshift = tb_cont.meta["TMPL_Z"][0]
            custom_input_file = None
        else:
            custom_input_file = os.path.join(session_path, "custom_input.csv")
            if os.path.exists(custom_input_file):
                with open(custom_input_file, "rb") as f:
                    conf_target.custom_input = f.read()
                    logger.info("Custom input is used.")

        conf_target.galactic_extinction = tb_cont.meta["GAL_EXT"][0]
        conf_target.r_eff = tb_cont.meta["R_EFF"][0]
        conf_target.line_flux = tb_line.meta["EL_FLUX"][0]
        conf_target.line_width = tb_line.meta["EL_SIG"][0]

        conf_environment.seeing = tb_line.meta["SEEING"][0]
        conf_environment.degrade = tb_line.meta["DEGRADE"][0]
        conf_environment.moon_zenith_angle = tb_line.meta["MOON-ZA"][0]
        conf_environment.moon_target_angle = tb_line.meta["MOON-SEP"][0]
        conf_environment.moon_phase = tb_line.meta["MOON-PH"][0]

        conf_instrument.exp_time = tb_line.meta["EXPTIME1"][0]
        conf_instrument.exp_num = tb_line.meta["EXPNUM"][0]
        conf_instrument.field_angle = tb_line.meta["FLDANG"][0]
        conf_instrument.mr_mode = tb_line.meta["MED_RES"][0]

        conf_telescope.zenith_angle = tb_line.meta["ZANG"][0]

        logger.info(f"Recovering Simulation ID {simulation_id}")

        is_recovered = True

    except FileNotFoundError:
        logger.error(
            f"File not found, {filename_cont}, {filename_line}. No recovery is done."
        )

        simulation_id = None
        is_recovered = False
        custom_input_file = None

    return simulation_id, is_recovered, custom_input_file
