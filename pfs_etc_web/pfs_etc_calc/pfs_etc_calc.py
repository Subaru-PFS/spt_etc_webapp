#!/usr/bin/env python3

# Standard Library
import os
from functools import cache

# Third Party Library
import pandas as pd
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


class PfsSpecSim:
    def __init__(self, params):
        self.params = params
        self.etc = pfsetc.Etc()
        self.sim = pfsspec.Pfsspec()

    def run_etc(self):
        # environment
        self.etc.set_param("SEEING", self.params.seeing)
        self.etc.set_param("degrade", self.params.degrade)
        self.etc.set_param("MOON_ZENITH_ANG", self.params.moon_zenith_angle)
        self.etc.set_param("MOON_TARGET_ANG", self.params.moon_target_angle)
        self.etc.set_param("MOON_PHASE", self.params.moon_phase)

        # instrument
        self.etc.set_param("EXP_TIME", self.params.exp_time)
        self.etc.set_param("EXP_NUM", self.params.exp_num)
        self.etc.set_param("FIELD_ANG", self.params.field_angle)
        self.etc.set_param("MR_MODE", "Y" if self.params.mr_mode else "N")

        # telescope
        self.etc.set_param("ZENITH_ANG", self.params.zenith_angle)

        # target
        self.etc.set_param("GALACTIC_EXT", self.params.galactic_extinction)

        if self.params.mag_file is None:
            self.etc.set_param("MAG_FILE", f"{self.params.mag}")
        else:
            self.etc.set_param("MAG_FILE", self.params.mag_file)

        self.etc.set_param("REFF", self.params.r_eff)
        self.etc.set_param("LINE_FLUX", self.params.line_flux)
        self.etc.set_param("LINE_WIDTH", self.params.line_width)

        # output
        self.etc.set_param(
            "OUTFILE_NOISE", os.path.join(self.params.outdir, self.params.outfile_noise)
        )
        self.etc.set_param(
            "OUTFILE_SNC",
            os.path.join(self.params.outdir, self.params.outfile_sn_continuum),
        )
        self.etc.set_param(
            "OUTFILE_SNL", os.path.join(self.params.outdir, self.params.outfile_sn_line)
        )
        self.etc.set_param(
            "OUTFILE_OII", os.path.join(self.params.outdir, self.params.outfile_sn_oii)
        )

        # execute PFS ETC
        self.etc.run()

    def run_sim(self):
        if self.params.mag_file is None:
            self.sim.set_param("MAG_FILE", f"{self.params.mag}")
        else:
            self.sim.set_param("MAG_FILE", self.params.mag_file)

        self.sim.set_param(
            "etcFile",
            os.path.join(self.params.outdir, self.params.outfile_sn_continuum),
        )

        self.sim.set_param("EXP_NUM", self.params.exp_num)
        self.sim.set_param("asciiTable", self.params.outfile_simspec)
        self.sim.set_param("nrealize", self.params.nrealize)

        self.sim.set_param("outDir", self.params.outdir)

        self.sim.set_param("writeFits", self.params.write_fits)
        self.sim.set_param("writePfsArm", self.params.write_pfs_arm)

        # simulate spectrum
        self.sim.make_sim_spec()

    def exec(self, skip=False):
        if not skip:
            self.run_etc()
            self.run_sim()

    def show(self, infile=None):
        if infile is None:
            infile = os.path.join(
                self.params.outdir, f"{self.params.outfile_simspec}.dat"
            )

        df = load_simspec(infile)

        self.p_simspec = create_simspec_plot(df)

        return self.p_simspec
        # return None


if __name__ == "__main__":
    pass
    # Third Party Library
    # from pfs_etc_params import PfsSpecParameter

    # x = PfsSpecSim(PfsSpecParameter())
