#!/usr/bin/env python3

import glob
import os
from pathlib import Path

import numpy as np
from loguru import logger
from pfsspecsim.etc import EtcParams, run_etc_files
from pfsspecsim.sim import SimSpecParams, run_sim_spec

from . import PfsArm
from .pfs_etc_params import OutputConf, SimulationConf
from .pfs_etc_spectemplates import create_template_spectrum
from .pfs_etc_utils import (
    create_simspec_files,
    create_simspec_plot,
    load_simspec,
    load_sncont,
    load_snline,
)


def _to_bool(value) -> bool:
    """Interpret a "True"/"False"-style string (or bool) as a bool."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "t", "yes", "y")


class PfsSpecSim:
    def __init__(
        self,
        target=None,
        environment=None,
        instrument=None,
        telescope=None,
        output=None,
        simconf=None,
    ):
        self.target = target
        self.environment = environment
        self.instrument = instrument
        self.telescope = telescope

        # Create fresh default instances per call: a `param.Parameterized`
        # default argument would be instantiated once at import time and
        # shared across every session in the process.
        self.output = output if output is not None else OutputConf()
        self.simconf = simconf if simconf is not None else SimulationConf()

        # Resolve the ETC worker-thread count: prefer ETC_N_WORKERS, fall
        # back to OMP_NUM_THREADS (deployment compatibility), else None
        # (leave n_workers unset so EtcParams' own default applies).
        n_workers_env = os.environ.get("ETC_N_WORKERS") or os.environ.get(
            "OMP_NUM_THREADS"
        )
        if n_workers_env is not None:
            self.n_workers = max(1, int(n_workers_env))
        else:
            self.n_workers = None

        self.outfile_simspec_prefix = None
        self.outfile_snline_prefix = None

        self.etc_results = None
        self.sim_result = None

        self.flag_saturation = {"b": False, "r": False, "n": False, "m": False}

    @property
    def outdir(self) -> Path:
        return Path(self.output.basedir) / self.output.sessiondir

    def _mag_kwargs(self) -> dict:
        """mag/mag_file kwargs for EtcParams/SimSpecParams (mutually exclusive)."""
        if self.target.mag_file is None:
            return {"mag": float(self.target.mag), "mag_file": None}
        return {"mag": None, "mag_file": Path(self.target.mag_file)}

    @staticmethod
    def _outfile(name: str):
        """ETC outfile: `None` for the '-' sentinel, else a `Path`."""
        return None if name == "-" else Path(name)

    def _resolve_infile(self, name: str) -> str:
        """Resolve an ETC intermediate input file inside ``outdir``.

        Prefer the configured name (new ``.ecsv``); if it does not exist,
        fall back to the legacy ``.dat``-named sibling (same stem, ``.dat``
        suffix) so pre-migration sessions can still be recovered.
        """
        path = self.outdir / name
        if not path.exists():
            legacy = self.outdir / (Path(name).stem + ".dat")
            if legacy.exists():
                return str(legacy)
        return str(path)

    def run_etc(self):
        self.outdir.mkdir(parents=True, exist_ok=True)

        self.target, flag_good_lamnorm = create_template_spectrum(
            self.target, tmpdir=str(self.outdir)
        )

        if flag_good_lamnorm is False:
            raise ValueError(
                "Failed at normalizing the template. Check the wavelength range of the template and wavelength to normalize."
            )

        if self.target.custom_input is not None:
            with open(self.outdir / "custom_input.csv", "wb") as f:
                f.write(self.target.custom_input)

        params = EtcParams(
            # environment
            seeing=float(self.environment.seeing),
            degrade=float(self.environment.degrade),
            moon_zenith_ang=float(self.environment.moon_zenith_angle),
            moon_target_ang=float(self.environment.moon_target_angle),
            moon_phase=float(self.environment.moon_phase),
            # instrument
            exp_time=float(self.instrument.exp_time),
            exp_num=int(self.instrument.exp_num),
            field_ang=float(self.instrument.field_angle),
            mr_mode=bool(self.instrument.mr_mode),
            # telescope
            zenith_ang=float(self.telescope.zenith_angle),
            # target
            galactic_ext=float(self.target.galactic_extinction),
            reff=float(self.target.r_eff),
            line_flux=float(self.target.line_flux),
            line_width=float(self.target.line_width),
            **self._mag_kwargs(),
            # output
            outdir=self.outdir,
            outfile_noise=self._outfile(self.output.noise),
            outfile_snc=self._outfile(self.output.sn_cont),
            outfile_snl=self._outfile(self.output.sn_line),
            outfile_oii=self._outfile(self.output.sn_oii),
            **({"n_workers": self.n_workers} if self.n_workers is not None else {}),
        )
        params.validate()

        logger.info(f"Input parameters for ETC\n{params}")

        # execute PFS ETC
        self.etc_results = run_etc_files(params)

    def run_sim(self):
        params = SimSpecParams(
            etc_file=self.outdir / self.output.sn_cont,
            exp_num=int(self.instrument.exp_num),
            **self._mag_kwargs(),
            nrealize=int(self.simconf.nrealize),
            out_dir=self.outdir,
            ascii_table=self.output.simspec,
            write_fits=_to_bool(self.output.write_fits),
            write_pfs_arm=_to_bool(self.output.write_pfs_arm),
            counts_min=float(self.simconf.counts_min),
            tract=int(self.simconf.tract),
            patch=self.simconf.patch,
            visit0=int(self.simconf.visit0),
            cat_id=int(self.simconf.catId),
            obj_id=int(self.simconf.objId),
            spectrograph=int(self.simconf.spectrograph),
        )
        params.validate()

        # simulate spectrum
        self.sim_result = run_sim_spec(params)

    def exec(self, skip: bool = False):
        if not skip:
            self.run_etc()
            self.run_sim()

    def show(self, infile: str | None = None, write: bool = True):
        outdir = os.path.join(self.output.basedir, self.output.sessiondir)

        if infile is None:
            infile_simspec = os.path.join(outdir, f"{self.output.simspec}.dat")
            infile_snline = self._resolve_infile(self.output.sn_line)
            infile_sncont = self._resolve_infile(self.output.sn_cont)

        df_simspec = load_simspec(infile_simspec)
        df_snline = load_snline(infile_snline)
        df_sncont = load_sncont(infile_sncont)

        self.flag_saturation = {
            PfsArm.b: np.any(
                df_sncont.loc[df_sncont["arm"] == PfsArm.b.value, "is_saturated"]
            ),
            PfsArm.r: np.any(
                df_sncont.loc[df_sncont["arm"] == PfsArm.r.value, "is_saturated"]
            ),
            PfsArm.n: np.any(
                df_sncont.loc[df_sncont["arm"] == PfsArm.n.value, "is_saturated"]
            ),
            PfsArm.m: np.any(
                df_sncont.loc[df_sncont["arm"] == PfsArm.m.value, "is_saturated"]
            ),
        }

        # Extract session_id from sessiondir (last component of the path)
        session_id = os.path.basename(self.output.sessiondir)

        self.outfile_pfsobject = os.path.join(outdir, f"pfsObject-{session_id}.fits")

        self.outfile_simspec_prefix = os.path.join(
            outdir, f"pfs_etc_simspec-{session_id}"
        )
        self.outfile_snline_prefix = os.path.join(
            outdir, f"pfs_etc_snline-{session_id}"
        )
        self.outfile_tjtext = os.path.join(outdir, f"pfs_etc_tjtext-{session_id}.txt")

        if write:
            tb_simspec, tb_snline, text_tj = create_simspec_files(
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

            text_tj += (
                f"[16] Simulation ID: {os.path.basename(self.output.sessiondir)}\n"
            )
            # text_tj = text_tj.replace("_", "\\_")

            with open(self.outfile_tjtext, "w") as f:
                f.write(text_tj)

        self.p_simspec = create_simspec_plot(
            df_simspec, df_snline, df_sncont, self.instrument.mr_mode
        )

        return self.p_simspec
