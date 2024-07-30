#!/usr/bin/env python3

import os
from io import BytesIO

import numpy as np
import pandas as pd
import synphot
from astropy import units as u
from astropy.io.fits import getval


def prepare_spectrum(
    infile: str,
    outfile: str,
    redshift: float = 0.0,
    norm_wavelength: u.Quantity = 400.0 * u.nm,
    norm_mag: u.Quantity = 20.0 * u.ABmag,
    norm_bandwidth: u.Quantity = 10.0 * u.nm,
    wmin: float = 300.0,  # [nm]
    wmax: float = 1300.0,  # [nm]
) -> None or bool:
    # define a tophat filter for flux normalization
    band = synphot.SpectralElement(
        synphot.models.Box1D,
        amplitude=1.0,
        x_0=norm_wavelength,
        width=norm_bandwidth,
    )

    # load the template spectrum
    sp_rest = synphot.SourceSpectrum.from_file(
        infile,
        wave_unit=u.AA,
        # flux_unit=synphot.units.FLAM,
        flux_unit=u.erg / u.s / u.cm**2 / u.AA,
    )
    # min/max wavelenghth supported in the original template
    wmin0 = getval(infile, "WAVE_MIN", 1)  # angstrom
    wmax0 = getval(infile, "WAVE_MAX", 1)  # angstrom
    # print(sp_rest.waveset, sp_rest(sp_rest.waveset))

    # redshifting
    sp_z = synphot.SourceSpectrum(sp_rest, z=redshift)

    # check if wavelength range of the bandpass is included in the template spectrum
    # print(wmin0, wmin0 * (1 + redshift), band.waverange.to(u.nm).value[0])
    # print(wmax0, wmax0 * (1 + redshift), band.waverange.to(u.nm).value[1])
    if (wmin0 * (1 + redshift) > band.waverange.to(u.AA).value[0]) or (
        wmax0 * (1 + redshift) < band.waverange.to(u.AA).value[1]
    ):
        return False

    # normalization
    sp_norm = sp_z.normalize(norm_mag, band=band)

    # write to an ascii file
    wout = sp_norm.waveset.to(u.nm).value
    fout = sp_norm(sp_norm.waveset, flux_unit=u.ABmag).value
    # fout[~np.isfinite(fout)] = 0.0
    fout[~np.isfinite(fout)] = 99.9
    idx = np.logical_and(wout >= wmin, wout <= wmax)

    with open(outfile, "w") as f:
        for i in range(len(wout[idx])):
            f.write(f"{wout[idx][i]}  {fout[idx][i]}\n")

    return None


def create_template_spectrum(target, tmpdir: str = "."):
    pkgdir = os.path.dirname(os.path.abspath(__file__))
    datadir = os.path.join("spectemplates", "output")
    templatefiles = {
        # "Star-forming galaxy": "galaxy_starforming.fits",
        # "Quiescent galaxy": "galaxy_quiescent.fits",
        "SSP (100 Myr, [M/H]=0, Chabrier IMF)": "galaxy_starforming.fits",
        "SSP (1 Gyr, [M/H]=0, Chabrier IMF)": "galaxy_quiescent.fits",
        "Elliptical 2 Gyr": "galaxy_swire_elliptical_2gyr.fits",
        "Elliptical 5 Gyr": "galaxy_swire_elliptical_5gyr.fits",
        "Elliptical 13 Gyr": "galaxy_swire_elliptical_13gyr.fits",
        "S0": "galaxy_swire_spiral_s0.fits",
        "Sa": "galaxy_swire_spiral_sa.fits",
        "Sb": "galaxy_swire_spiral_sb.fits",
        "Sc": "galaxy_swire_spiral_sc.fits",
        "Sd": "galaxy_swire_spiral_sd.fits",
        "Sdm": "galaxy_swire_spiral_sdm.fits",
        "Quasar": "quasar.fits",
        "B0V": "star_b0v.fits",
        "A0V": "star_a0v.fits",
        "F0V": "star_f0v.fits",
        "G2V": "star_g2v.fits",
        "K0V": "star_k0v.fits",
        "M0V": "star_m0v.fits",
        "K0III": "star_k0iii.fits",
        "M0III": "star_m0iii.fits",
        "Flat in frequency": None,
    }

    if target.custom_input is not None:
        print("Custom input spectrum detected!")
        target.mag_file = os.path.join(tmpdir, "mag_file_template.txt")
        df_custom = pd.read_csv(
            BytesIO(target.custom_input),
            encoding="utf8",
            names=["wavelength", "flux"],
            comment="#",
        )
        wout = (df_custom["wavelength"].to_numpy() * u.AA).to(u.nm)
        fout = (df_custom["flux"].to_numpy() * (u.erg / u.s / u.cm**2 / u.AA)).to(
            u.ABmag, equivalencies=u.spectral_density(wout)
        )
        with open(target.mag_file, "w") as f:
            for i in range(len(wout)):
                f.write(f"{wout[i].value}  {fout[i].value}\n")
        return target, None

    if target.template == "Flat in frequency":
        target.mag_file = target.mag
        return target, None
    else:
        target.mag_file = os.path.join(tmpdir, "mag_file_template.txt")
        flag_good_lamnorm = prepare_spectrum(
            os.path.join(pkgdir, datadir, templatefiles[target.template]),
            target.mag_file,
            redshift=target.redshift,
            norm_wavelength=target.wavelength * u.nm,
            norm_mag=target.mag * u.ABmag,
        )
    # else:
    #     raise ValueError(f"Template {target.template} has not yet implemented")

    return target, flag_good_lamnorm
