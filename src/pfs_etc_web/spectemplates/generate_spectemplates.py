#!/usr/bin/env python3

import os

import numpy as np
import synphot
from astropy import units as u
from astropy.io import fits
from scipy.interpolate import interp1d
from specutils import Spectrum1D
from specutils.manipulation import FluxConservingResampler, LinearInterpolatedResampler


def read_bt_settl(file_dict):
    # col1: wavelength (angstrom)
    # col2: flux (erg/s/cm^2/A)
    spec0 = np.genfromtxt(
        file_dict["infile"], names=["wavelength", "flux"], dtype=[float, float]
    )
    input_spec = Spectrum1D(
        spectral_axis=spec0["wavelength"] * u.AA,
        flux=spec0["flux"] * (u.erg / u.s / u.cm**2 / u.AA),
    )
    return input_spec


def read_miles(file_dict):
    hdu = fits.open(file_dict["infile"])
    w = hdu[0].header["CRVAL1"] + hdu[0].header["CDELT1"] * np.arange(
        hdu[0].header["NAXIS1"]
    )
    spec0 = Spectrum1D(
        spectral_axis=w * u.AA,
        flux=hdu[0].data * (u.erg / u.s / u.cm**2 / u.AA),
    )
    return spec0


def read_stsci(file_dict):
    hdu = fits.open(file_dict["infile"])
    input_spec = Spectrum1D(
        spectral_axis=hdu[1].data["WAVELENGTH"] * u.AA,
        flux=hdu[1].data["FLUX"] * (u.erg / u.s / u.cm**2 / u.AA),
    )
    print(input_spec.spectral_axis, input_spec.flux)
    return input_spec


# def setup_spectrum1d(wave, flux):
#     return


def resample_spec(input_spec, wmin=900 * u.AA, wmax=13000 * u.AA, dw=0.5 * u.AA):
    new_disp_grid = np.linspace(wmin, wmax, int((wmax - wmin) / dw) + 1)
    # resampler = FluxConservingResampler()
    resampler = LinearInterpolatedResampler(extrapolation_treatment="zero_fill")
    new_spec = resampler(input_spec, new_disp_grid)
    return new_spec


def main(k, v):
    if v["library"] == "BT-Settl":
        input_spec = read_bt_settl(v)
        # input_spec = setup_spectrum1d(wave, flux)
        # print(wave, flux)
    elif v["library"] == "MILES":
        input_spec = read_miles(v)
    elif v["library"] == "STScI":
        input_spec = read_stsci(v)

    new_spec = resample_spec(input_spec)

    new_spec.write(v["outfile"], overwrite=True, format="tabular-fits")

    # print(wave_new, flux_new)


if __name__ == "__main__":
    indir = "input"
    outdir = "output"

    infile_dict = {
        "B0V": {
            "infile": os.path.join(indir, "lte300-4.0-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_b0v.fits"),
            "library": "BT-Settl",
        },
        "A0V": {
            "infile": os.path.join(indir, "lte096-4.0-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_a0v.fits"),
            "library": "BT-Settl",
        },
        "G2V": {
            "infile": os.path.join(indir, "lte059-4.5-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_g2v.fits"),
            "library": "BT-Settl",
        },
        "Post-starburst galaxy": {
            "infile": os.path.join(indir, "Ech1.30Zp0.00T01.0000_iPp0.00_baseFe.fits"),
            "outfile": os.path.join(outdir, "galaxy_poststarburst.fits"),
            "library": "MILES",
        },
        "Quiescent galaxy": {
            "infile": os.path.join(indir, "Ech1.30Zp0.00T10.0000_iPp0.00_baseFe.fits"),
            "outfile": os.path.join(outdir, "galaxy_quiescent.fits"),
            "library": "MILES",
        },
        "Star-forming galaxy": {
            "infile": os.path.join(indir, "Ech1.30Zp0.00T00.1000_iPp0.00_baseFe.fits"),
            "outfile": os.path.join(outdir, "galaxy_starforming.fits"),
            "library": "MILES",
        },
        "Quasar": {
            "infile": os.path.join(indir, "optical_nir_qso_sed_001.fits"),
            "outfile": os.path.join(outdir, "quasar.fits"),
            "library": "STScI",
        },
    }
    for k, v in infile_dict.items():
        print(k, v)
        main(k, v)
