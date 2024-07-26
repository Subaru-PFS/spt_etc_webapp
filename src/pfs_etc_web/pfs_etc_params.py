#!/usr/bin/env python3


from dataclasses import dataclass

# from typing import Any
import numpy as np
import param

# from traitlets import default


@dataclass(frozen=True)
class PfsSpecParameter:
    # target
    template: str = "Flat in frequency"
    mag: float = 20.0
    mag_file: float | str = None
    wavelength: float = 550.0
    redshift: float = 0.0
    custom_input: str = None
    r_eff: float = 0.3
    galactic_extinction: float = 0.0
    line_flux: float = 1e-17
    line_width: float = 70.0
    line_sn: bool = True

    # observing condition
    seeing: float = 0.8
    degrade: float = 1.0  # equivalent to throughput
    moon_zenith_angle: int = 30
    moon_target_angle: int = 60
    moon_phase: int = 0.0

    # instrument
    exp_time: int = 900
    exp_num: int = 1
    field_angle: float = 0.0
    mr_mode: bool = False

    # telescope
    zenith_angle: int = 45

    # misc
    noise_reused: bool = False

    # output for ETC
    basedir: str = "tmp"
    sessiondir: str = "out"
    tmpdir: str = "tmp"
    outfile_noise: str = "noise.dat"
    outfile_sn_continuum: str = "sn_continuum.dat"
    outfile_sn_line: str = "sn_line.dat"
    # outfile_sn_oii: str = "sn_oii.dat"
    outfile_sn_oii: str = "-"

    # For Simulator
    outfile_simspec: str = "simulated_spectrum"  # ".dat" will be added by the simulator
    nrealize: int = 1
    write_fits: str = "True"
    write_pfs_arm: str = "False"
    outfile_pfsobject: str = None

    tract: int = 0
    patch: str = "0,0"
    visit0: int = 1
    objId: np.int64 = 1
    catId: int = 0
    counts_min: float = 0.1
    # etc_file: str = outfile_sn_continuum
    spectrograph: int = 1


default_parameters = PfsSpecParameter()


class TargetConf(param.Parameterized):
    # Templates
    template = param.String(
        label="Template Spectrum",
        default=default_parameters.template,
        # doc="Template Spectrum",
    )

    mag = param.Number(
        label="Magnitude (AB)",
        default=default_parameters.mag,
    )

    wavelength = param.Number(
        label="Wavelength (nm) for normalization",
        default=default_parameters.wavelength,
        bounds=(440, 1240),
    )

    redshift = param.Number(
        label="Redshift",
        default=default_parameters.redshift,
        bounds=(0, 20),
    )

    line_flux = param.Number(
        label="Line flux (erg/s/cm^2)",
        default=default_parameters.line_flux,
        bounds=(0, None),
        # doc="Emission line flux in the units of erg/s/cm^2. The emission line S/N "
        # "is computed on top of the main target source spectrum. "
        # "If you wish to compute emission line only S/N, you can set very large Magnitude value.",
    )
    line_width = param.Number(
        label="Line width sigma (km/s)",
        default=default_parameters.line_width,
        bounds=(0, None),
    )
    line_sn = param.Boolean(
        label="Calculate emission line S/N on the target spectrum",
        default=default_parameters.line_sn,
    )

    # Custom input spectrum
    custom_input = param.Parameter(
        label="Custom Input Spectrum (.csv)",
        default=default_parameters.custom_input,
    )

    # Misc. information
    galactic_extinction = param.Number(
        label="Galactic Extinction E(B-V) (mag)",
        default=default_parameters.galactic_extinction,
        bounds=(0.0, None),
    )
    r_eff = param.Number(
        label="Effective Radius (arcsec)",
        default=default_parameters.r_eff,
        bounds=(0.0, None),
    )

    def reset(self):
        self.template = default_parameters.template
        self.mag = default_parameters.mag
        self.wavelength = default_parameters.wavelength
        self.redshift = default_parameters.redshift
        self.mag_file = default_parameters.mag_file
        self.galactic_extinction = default_parameters.galactic_extinction
        self.r_eff = default_parameters.r_eff
        self.line_flux = default_parameters.line_flux
        self.line_width = default_parameters.line_width
        self.line_sn = default_parameters.line_sn


class EnvironmentConf(param.Parameterized):
    seeing = param.Number(
        label="Seeing FWHM (arcsec)",
        default=default_parameters.seeing,
        bounds=(0.0, 2.0),
    )
    degrade = param.Number(
        label="Throughput",
        default=default_parameters.degrade,
        bounds=(0.0, 1.0),
    )
    moon_zenith_angle = param.Integer(
        label="Moon Zenith Angle (degree)",
        default=default_parameters.moon_zenith_angle,
        bounds=(0, 90),
    )
    moon_target_angle = param.Integer(
        label="Moon Separation to Target (degree)",
        default=default_parameters.moon_target_angle,
        bounds=(0, 180),
    )
    moon_phase = param.Number(
        label="Moon Phase (0=new; 0.5=full; 1=new)",
        default=default_parameters.moon_phase,
        bounds=(0.0, 1.0),
    )

    def reset(self):
        self.seeing = default_parameters.seeing
        self.degrade = default_parameters.degrade
        self.moon_zenith_angle = default_parameters.moon_zenith_angle
        self.moon_target_angle = default_parameters.moon_target_angle
        self.moon_phase = default_parameters.moon_phase


class InstrumentConf(param.Parameterized):
    exp_time = param.Integer(
        label="Integration Time per Exposure (s)",
        default=default_parameters.exp_time,
        bounds=(0, None),
    )
    exp_num = param.Integer(
        label="Number of Exposures",
        default=default_parameters.exp_num,
        bounds=(1, None),
    )
    field_angle = param.Number(
        label="Distance from FoV center (degree)",
        default=default_parameters.field_angle,
        bounds=(0.0, 0.7),
    )
    mr_mode = param.Boolean(
        label="Use Medium Resolution? (checked=True)",
        default=default_parameters.mr_mode,
    )

    def reset(self):
        self.exp_time = default_parameters.exp_time
        self.exp_num = default_parameters.exp_num
        self.field_angle = default_parameters.field_angle
        self.mr_mode = default_parameters.mr_mode


class TelescopeConf(param.Parameterized):
    zenith_angle = param.Integer(
        label="Zenith Angle (degree)",
        default=default_parameters.zenith_angle,
        bounds=(30, 90),
    )

    def reset(self):
        self.zenith_angle = default_parameters.zenith_angle


class OutputConf(param.Parameterized):
    basedir = param.String(
        label="Base directory to write outputs (default: ./tmp)",
        default=default_parameters.basedir,
    )
    sessiondir = param.String(
        label="Output Directory",
        default=default_parameters.sessiondir,
    )
    tmpdir = param.String(
        label="Temporary Directory",
        default=default_parameters.tmpdir,
    )
    noise = param.String(
        label="Noise spectrum",
        default=default_parameters.outfile_noise,
    )
    sn_cont = param.String(
        label="Continuum S/N",
        default=default_parameters.outfile_sn_continuum,
    )
    sn_line = param.String(
        label="Line S/N",
        default=default_parameters.outfile_sn_line,
    )
    sn_oii = param.String(
        label="[OII] S/N",
        default=default_parameters.outfile_sn_oii,
    )

    simspec = param.String(
        label="Simulation output",
        default=default_parameters.outfile_simspec,
    )
    write_fits = param.String(
        label='Flag to write a FITS file (caution: "True" or "False" in string)',
        default=default_parameters.write_fits,
    )
    write_pfs_arm = param.String(
        label='Flag to write a FITS file for each arm (caution: "True" or "False" in string)',
        default=default_parameters.write_pfs_arm,
    )
    pfsobject = param.String(
        label="pfsObject file", default=default_parameters.outfile_pfsobject
    )

    def __init__(self, **params):
        super().__init__(**params)


class SimulationConf(param.Parameterized):
    nrealize = param.Integer(label="nrealize", default=default_parameters.nrealize)
    tract = param.Integer(label="tract", default=default_parameters.tract)
    patch = param.String(
        label="patch (caution: str value)", default=default_parameters.patch
    )
    visit0 = param.Integer(label="visit0", default=default_parameters.visit0)
    objId = param.Integer(label="objId", default=default_parameters.objId)
    catId = param.Integer(label="catId", default=default_parameters.catId)
    counts_min = param.Number(label="counts_min", default=default_parameters.counts_min)
    spectrograph = param.Integer(
        label="Spectrograph (0-3)", default=default_parameters.spectrograph
    )
