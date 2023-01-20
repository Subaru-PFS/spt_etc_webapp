#!/usr/bin/env python3

# Standard Library
import os
from functools import cache

# Third Party Library
import pandas as pd
from pfs_etc_params import OutputConf
from pfs_etc_params import SimulationConf
from pfs_etc_plots import create_simspec_plot
from pfsspecsim import pfsetc
from pfsspecsim import pfsspec


def load_simspec(infile):
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


def load_snline(infile):
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


class PfsSpecSim:
    def __init__(
        self,
        target=None,
        environment=None,
        instrument=None,
        telescope=None,
        # use_default=Tru,
    ):

        self.target = target
        self.environment = environment
        self.instrument = instrument
        self.telescope = telescope

        self.output = OutputConf()
        self.simconf = SimulationConf()

        # if use_default:
        # self.params = params
        self.etc = pfsetc.Etc()
        self.sim = pfsspec.Pfsspec()

    def run_etc(self):
        # environment
        self.etc.set_param("SEEING", self.environment.seeing)
        self.etc.set_param("degrade", self.environment.degrade)
        self.etc.set_param("MOON_ZENITH_ANG", self.environment.moon_zenith_angle)
        self.etc.set_param("MOON_TARGET_ANG", self.environment.moon_target_angle)
        self.etc.set_param("MOON_PHASE", self.environment.moon_phase)

        # instrument
        self.etc.set_param("EXP_TIME", self.instrument.exp_time)
        self.etc.set_param("EXP_NUM", self.instrument.exp_num)
        self.etc.set_param("FIELD_ANG", self.instrument.field_angle)
        self.etc.set_param("MR_MODE", "Y" if self.instrument.mr_mode else "N")

        # telescope
        self.etc.set_param("ZENITH_ANG", self.telescope.zenith_angle)

        # target
        self.etc.set_param("GALACTIC_EXT", self.target.galactic_extinction)

        if self.target.mag_file is None:
            self.etc.set_param("MAG_FILE", f"{self.target.mag}")
        else:
            self.etc.set_param("MAG_FILE", self.target.mag_file)

        self.etc.set_param("REFF", self.target.r_eff)
        self.etc.set_param("LINE_FLUX", self.target.line_flux)
        self.etc.set_param("LINE_WIDTH", self.target.line_width)

        # output
        self.etc.set_param(
            "OUTFILE_NOISE", os.path.join(self.output.outdir, self.output.noise)
        )
        self.etc.set_param(
            "OUTFILE_SNC",
            os.path.join(self.output.outdir, self.output.sn_cont),
        )
        self.etc.set_param(
            "OUTFILE_SNL", os.path.join(self.output.outdir, self.output.sn_line)
        )
        self.etc.set_param(
            "OUTFILE_OII", os.path.join(self.output.outdir, self.output.sn_oii)
        )

        # execute PFS ETC
        self.etc.run()

    def run_sim(self):
        if self.target.mag_file is None:
            self.sim.set_param("MAG_FILE", f"{self.target.mag}")
        else:
            self.sim.set_param("MAG_FILE", self.target.mag_file)

        self.sim.set_param(
            "etcFile",
            os.path.join(self.output.outdir, self.output.sn_cont),
        )

        self.sim.set_param("EXP_NUM", self.instrument.exp_num)
        self.sim.set_param("asciiTable", self.output.simspec)
        self.sim.set_param("nrealize", self.simconf.nrealize)

        self.sim.set_param("outDir", self.output.outdir)

        self.sim.set_param("writeFits", self.output.write_fits)
        self.sim.set_param("writePfsArm", self.output.write_pfs_arm)

        # simulate spectrum
        self.sim.make_sim_spec()

    def exec(self, skip=False):
        if not skip:
            self.run_etc()
            self.run_sim()

    def show(self, infile=None):
        if infile is None:
            infile_simspec = os.path.join(
                self.output.outdir, f"{self.output.simspec}.dat"
            )
            infile_snline = os.path.join(self.output.outdir, f"{self.output.sn_line}")

        df_simspec = load_simspec(infile_simspec)
        df_snline = load_snline(infile_snline)

        print(df_snline)

        self.p_simspec = create_simspec_plot(df_simspec, df_snline)

        return self.p_simspec
        # return None


if __name__ == "__main__":
    pass
    # Third Party Library
    # from pfs_etc_params import PfsSpecParameter

    # x = PfsSpecSim(PfsSpecParameter())
