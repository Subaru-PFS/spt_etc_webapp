#!/usr/bin/env python3

import glob
import os
import pprint
import sys

import pandas as pd
from logzero import logger
from pfsspecsim import pfsetc, pfsspec

from .pfs_etc_params import OutputConf, SimulationConf
from .pfs_etc_spectemplates import create_template_spectrum
from .pfs_etc_utils import (
    create_simspec_files,
    create_simspec_plot,
    load_simspec,
    load_sncont,
    load_snline,
)


class PfsSpecSim:
    def __init__(
        self,
        target=None,
        environment=None,
        instrument=None,
        telescope=None,
        output=OutputConf(),
        simconf=SimulationConf(),
    ):
        self.target = target
        self.environment = environment
        self.instrument = instrument
        self.telescope = telescope

        self.output = output
        self.simconf = simconf

        if os.environ.get("OMP_NUM_THREADS") is not None:
            omp_num_threads = int(os.environ.get("OMP_NUM_THREADS"))
        else:
            omp_num_threads = 4

        self.etc = pfsetc.Etc(omp_num_threads=omp_num_threads)
        self.sim = pfsspec.Pfsspec()

        self.outfile_simspec_prefix = None
        self.outfile_snline_prefix = None

    def run_etc(self):
        self.etc.set_param(
            "OUTDIR", os.path.join(self.output.basedir, self.output.sessiondir)
        )
        self.etc.set_param(
            "TMPDIR",
            os.path.join(
                self.output.basedir, self.output.sessiondir, self.output.tmpdir
            ),
        )
        for d in ["OUTDIR", "TMPDIR"]:
            if not os.path.exists(self.etc.params[d]):
                try:
                    os.makedirs(self.etc.params[d])
                except OSError as e:
                    sys.exit("Unable to create outDir: %s" % e)

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

        self.target = create_template_spectrum(
            self.target, tmpdir=self.etc.params["TMPDIR"]
        )
        # self.etc.set_param("MAG_FILE", f"{self.target.mag}")
        self.etc.set_param("MAG_FILE", f"{self.target.mag_file}")
        # self.target.mag_file = mag_file
        # self.etc.set_param("MAG_FILE", self.target.mag_file)

        self.etc.set_param("REFF", self.target.r_eff)
        self.etc.set_param("LINE_FLUX", self.target.line_flux)
        self.etc.set_param("LINE_WIDTH", self.target.line_width)

        # output
        if self.output.noise != "-":
            self.etc.set_param(
                "OUTFILE_NOISE",
                os.path.join(
                    self.output.basedir, self.output.sessiondir, self.output.noise
                ),
            )
        else:
            self.etc.set_param("OUTFILE_NOISE", self.output.noise)

        if self.output.sn_cont != "-":
            self.etc.set_param(
                "OUTFILE_SNC",
                os.path.join(
                    self.output.basedir, self.output.sessiondir, self.output.sn_cont
                ),
            )
        else:
            self.etc.set_param("OUTFILE_SNC", self.output.sn_cont)

        if self.output.sn_line != "-":
            self.etc.set_param(
                "OUTFILE_SNL",
                os.path.join(
                    self.output.basedir, self.output.sessiondir, self.output.sn_line
                ),
            )
        else:
            self.etc.set_param("OUTFILE_SNL", self.output.sn_line)

        if self.output.sn_oii != "-":
            self.etc.set_param(
                "OUTFILE_OII",
                os.path.join(
                    self.output.basedir, self.output.sessiondir, self.output.sn_oii
                ),
            )
        else:
            self.etc.set_param("OUTFILE_OII", self.output.sn_oii)

        logger.info(
            f"""Input parameters for gsetc\n{pprint.pformat(self.etc.params)}"""
        )

        # execute PFS ETC
        self.etc.run()

    def run_sim(self):
        # if self.target.mag_file is None:
        self.sim.set_param("MAG_FILE", f"{self.target.mag_file}")
        # else:
        # self.sim.set_param("MAG_FILE", self.target.mag_file)

        self.sim.set_param(
            "etcFile",
            os.path.join(
                self.output.basedir, self.output.sessiondir, self.output.sn_cont
            ),
        )

        self.sim.set_param("EXP_NUM", self.instrument.exp_num)
        self.sim.set_param("asciiTable", self.output.simspec)
        self.sim.set_param("nrealize", self.simconf.nrealize)

        self.sim.set_param(
            "outDir",
            os.path.join(self.output.basedir, self.output.sessiondir),
        )

        self.sim.set_param("writeFits", self.output.write_fits)
        self.sim.set_param("writePfsArm", self.output.write_pfs_arm)

        # simulate spectrum
        self.sim.make_sim_spec()

    def exec(self, skip: bool = False):
        if not skip:
            self.run_etc()
            self.run_sim()

    def show(self, infile: str = None):
        outdir = os.path.join(self.output.basedir, self.output.sessiondir)

        if infile is None:
            infile_simspec = os.path.join(outdir, f"{self.output.simspec}.dat")
            infile_snline = os.path.join(outdir, f"{self.output.sn_line}")
            infile_sncont = os.path.join(outdir, f"{self.output.sn_cont}")

        df_simspec = load_simspec(infile_simspec)
        df_snline = load_snline(infile_snline)
        df_sncont = load_sncont(infile_sncont)

        self.outfile_pfsobject = os.path.join(
            outdir, f"pfsObject-{self.output.sessiondir}.fits"
        )

        self.outfile_simspec_prefix = os.path.join(
            outdir, f"pfs_etc_simspec-{self.output.sessiondir}"
        )
        self.outfile_snline_prefix = os.path.join(
            outdir, f"pfs_etc_snline-{self.output.sessiondir}"
        )

        tb_simspec, tb_snline = create_simspec_files(
            self.target,
            self.environment,
            self.instrument,
            self.telescope,
            df_simspec,
            df_snline,
            df_sncont,
        )
        tb_simspec.write(
            f"{self.outfile_simspec_prefix}.fits", format="fits", overwrite=True
        )
        tb_simspec.write(
            f"{self.outfile_simspec_prefix}.ecsv",
            format="ascii.ecsv",
            delimiter=",",
            overwrite=True,
        )
        tb_snline.write(
            f"{self.outfile_snline_prefix}.fits", format="fits", overwrite=True
        )
        tb_snline.write(
            f"{self.outfile_snline_prefix}.ecsv",
            format="ascii.ecsv",
            delimiter=",",
            overwrite=True,
        )

        list_pfsobject_files = glob.glob(os.path.join(outdir, "pfsObject*.fits"))
        if len(list_pfsobject_files) != 1:
            logger.error(
                f"something wrong for pfsObject generation: {list_pfsobject_files}"
            )
        self.output.pfsobject = list_pfsobject_files[0]
        os.rename(
            self.output.pfsobject,
            self.outfile_pfsobject,
        )

        self.p_simspec = create_simspec_plot(df_simspec, df_snline, df_sncont)

        # print(type(self.p_simspec))

        return self.p_simspec
