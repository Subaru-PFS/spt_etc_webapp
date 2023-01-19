#!/usr/bin/env python3

# Standard Library
import os
from dataclasses import dataclass

# Third Party Library
import numpy as np


@dataclass
class PfsSpecParameter:
    # target
    mag: float = 22.5
    redshift: float = 1.0
    mag_file: str = None
    r_eff: float = 0.3
    galactic_extinction: float = 0.0
    line_flux: float = 1e-17
    line_width: float = 70.0

    # observing condition
    seeing: float = 0.8
    degrade: float = 1.0  # equivalent to transparency
    moon_zenith_angle: int = 30
    moon_target_angle: int = 60
    moon_phase: int = 0.0

    # instrument
    exp_time: int = 900
    exp_num: int = 1
    field_angle: float = 0.0
    mr_mode: str = False

    # telescope
    zenith_angle: int = 45

    # output
    outfile_noise: str = None
    outfile_snc: str = None
    outfile_snl: str = None
    outfile_oii: str = None
    overwrite: str = True

    # misc
    noise_reused: bool = False

    # output for ETC
    tmpdir: str = "tmp"
    outdir: str = "out"
    outfile_noise: str = "noise.dat"
    outfile_sn_continuum: str = "sn_continuum.dat"
    outfile_sn_line: str = "sn_line.dat"
    outfile_sn_oii: str = "sn_oii.dat"

    # For Simulator
    outfile_simspec: str = "simulated_spectrum"  # ".dat" will be added by the simulator
    nrealize: int = 1
    write_fits: str = "False"
    write_pfs_arm: str = "False"

    tract: int = 0
    patch: str = "0,0"
    visit0: int = 1
    objId: np.int64 = 1
    catId: int = 0
    counts_min: float = 0.1
    # etc_file: str = outfile_sn_continuum
    spectrograph: int = 1
