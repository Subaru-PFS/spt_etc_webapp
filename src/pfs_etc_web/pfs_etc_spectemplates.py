#!/usr/bin/env python3

import os
from io import BytesIO

import numpy as np
import pandas as pd
import synphot
from astropy import units as u


def prepare_spectrum(
    infile: str,
    outfile: str,
    redshift: float = 0.0,
    norm_wavelength: u.Quantity = 400.0 * u.nm,
    norm_mag: u.Quantity = 20.0 * u.ABmag,
    norm_bandwidth: u.Quantity = 10.0 * u.nm,
    wmin: float = 300.0,
    wmax: float = 1300.0,
) -> None:
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
    # print(sp_rest.waveset, sp_rest(sp_rest.waveset))

    # redshifting
    sp_z = synphot.SourceSpectrum(sp_rest, z=redshift)

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


def create_template_spectrum(target, tmpdir: str = "."):
    pkgdir = os.path.dirname(os.path.abspath(__file__))
    datadir = os.path.join("spectemplates", "output")
    templatefiles = {
        "Star-forming galaxy": "galaxy_starforming.fits",
        "Quiescent galaxy": "galaxy_quiescent.fits",
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
        return target

    if target.template == "Flat in frequency":
        target.mag_file = target.mag
        return target
    else:
        target.mag_file = os.path.join(tmpdir, "mag_file_template.txt")
        prepare_spectrum(
            os.path.join(pkgdir, datadir, templatefiles[target.template]),
            target.mag_file,
            redshift=target.redshift,
            norm_wavelength=target.wavelength * u.nm,
            norm_mag=target.mag * u.ABmag,
        )
    # else:
    #     raise ValueError(f"Template {target.template} has not yet implemented")

    return target
