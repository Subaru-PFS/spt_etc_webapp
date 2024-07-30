#!/usr/bin/env python3

import os

import numpy as np
import synphot
from astropy import units as u
from astropy.io import fits
from astropy.table import Table
from scipy.interpolate import interp1d
from specutils import Spectrum1D
from specutils.io.registers import custom_writer
from specutils.manipulation import FluxConservingResampler, LinearInterpolatedResampler


@custom_writer("fits-table-writer")
def generic_fits_table(spectrum, file_name, **kwargs):
    flux = spectrum.flux
    disp = spectrum.spectral_axis
    meta = spectrum.meta

    tab = Table([disp, flux], names=("wavelength", "flux"), meta=meta)

    tab.write(file_name, format="fits", overwrite=kwargs["overwrite"])


def read_bt_settl(file_dict):
    # col1: wavelength (angstrom)
    # col2: flux (erg/s/cm^2/A)
    spec0 = np.genfromtxt(
        file_dict["infile"], names=["wavelength", "flux"], dtype=[float, float]
    )
    input_spec = Spectrum1D(
        spectral_axis=spec0["wavelength"] * u.AA,
        flux=spec0["flux"] * (u.erg / u.s / u.cm**2 / u.AA),
        meta={
            "WAVE_MIN": (
                (spec0["wavelength"][0] * u.AA).value,
                "Min original wavelength [angstrom]",
            ),
            "WAVE_MAX": (
                (spec0["wavelength"][-1] * u.AA).value,
                "Max original wavelength [angstrom]",
            ),
        },
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
        meta={
            "WAVE_MIN": ((w[0] * u.AA).value, "Min original wavelength [angstrom]"),
            "WAVE_MAX": ((w[-1] * u.AA).value, "Max original wavelength [angstrom]"),
        },
    )
    return spec0


def read_stsci(file_dict):
    hdu = fits.open(file_dict["infile"])
    input_spec = Spectrum1D(
        spectral_axis=hdu[1].data["WAVELENGTH"] * u.AA,
        flux=hdu[1].data["FLUX"] * (u.erg / u.s / u.cm**2 / u.AA),
        meta={
            "WAVE_MIN": (
                (hdu[1].data["WAVELENGTH"][0] * u.AA).value,
                "Min original wavelength [angstrom]",
            ),
            "WAVE_MAX": (
                (hdu[1].data["WAVELENGTH"][-1] * u.AA).value,
                "Max original wavelength [angstrom]",
            ),
        },
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
    new_spec.meta = input_spec.meta
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
    elif v["library"] == "SWIRE":
        input_spec = read_bt_settl(v)

    new_spec = resample_spec(input_spec)

    print(new_spec.meta)

    # new_spec.write(v["outfile"], overwrite=True, format="tabular-fits")
    new_spec.write(v["outfile"], overwrite=True, format="fits-table-writer")

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
        "F0V": {
            "infile": os.path.join(indir, "lte072-4.5-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_f0v.fits"),
            "library": "BT-Settl",
        },
        "G2V": {
            "infile": os.path.join(indir, "lte059-4.5-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_g2v.fits"),
            "library": "BT-Settl",
        },
        "K0V": {
            "infile": os.path.join(indir, "lte052-4.5-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_k0v.fits"),
            "library": "BT-Settl",
        },
        "M0V": {
            "infile": os.path.join(indir, "lte038-4.5-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_m0v.fits"),
            "library": "BT-Settl",
        },
        "K0III": {
            "infile": os.path.join(indir, "lte048-2.0-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_k0iii.fits"),
            "library": "BT-Settl",
        },
        "M0III": {
            "infile": os.path.join(indir, "lte037-1.5-0.0a+0.0.BT-Settl.7.dat.txt"),
            "outfile": os.path.join(outdir, "star_m0iii.fits"),
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

    infile_stsci_swire = {
        "Elliptical 2 Gyr": {
            "infile": os.path.join(indir, "elliptical_swire_2gyr.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_elliptical_2gyr.fits"),
            "library": "STScI",
        },
        "Elliptical 5 Gyr": {
            "infile": os.path.join(indir, "elliptical_swire_5gyr.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_elliptical_5gyr.fits"),
            "library": "STScI",
        },
        "Elliptical 13 Gyr": {
            "infile": os.path.join(indir, "elliptical_swire_13gyr.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_elliptical_13gyr.fits"),
            "library": "STScI",
        },
        "S0": {
            "infile": os.path.join(indir, "spiral_swire_s0.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_s0.fits"),
            "library": "STScI",
        },
        "Sa": {
            "infile": os.path.join(indir, "spiral_swire_sa.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sa.fits"),
            "library": "STScI",
        },
        "Sb": {
            "infile": os.path.join(indir, "spiral_swire_sb.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sb.fits"),
            "library": "STScI",
        },
        "Sc": {
            "infile": os.path.join(indir, "spiral_swire_sc.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sc.fits"),
            "library": "STScI",
        },
        "Sd": {
            "infile": os.path.join(indir, "spiral_swire_sd.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sd.fits"),
            "library": "STScI",
        },
        "Sdm": {
            "infile": os.path.join(indir, "spiral_swire_sdm.fits"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sdm.fits"),
            "library": "STScI",
        },
    }

    indir_swire_original = "input/swire_original"
    infile_swire_original = {
        "Elliptical 2 Gyr": {
            "infile": os.path.join(indir_swire_original, "Ell2_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_elliptical_2gyr.fits"),
            "library": "SWIRE",
        },
        "Elliptical 5 Gyr": {
            "infile": os.path.join(indir_swire_original, "Ell5_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_elliptical_5gyr.fits"),
            "library": "SWIRE",
        },
        "Elliptical 13 Gyr": {
            "infile": os.path.join(indir_swire_original, "Ell13_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_elliptical_13gyr.fits"),
            "library": "SWIRE",
        },
        "S0": {
            "infile": os.path.join(indir_swire_original, "S0_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_s0.fits"),
            "library": "SWIRE",
        },
        "Sa": {
            "infile": os.path.join(indir_swire_original, "Sa_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sa.fits"),
            "library": "SWIRE",
        },
        "Sb": {
            "infile": os.path.join(indir_swire_original, "Sb_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sb.fits"),
            "library": "SWIRE",
        },
        "Sc": {
            "infile": os.path.join(indir_swire_original, "Sc_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sc.fits"),
            "library": "SWIRE",
        },
        "Sd": {
            "infile": os.path.join(indir_swire_original, "Sd_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sd.fits"),
            "library": "SWIRE",
        },
        "Sdm": {
            "infile": os.path.join(indir_swire_original, "Sdm_template_norm.sed"),
            "outfile": os.path.join(outdir, "galaxy_swire_spiral_sdm.fits"),
            "library": "SWIRE",
        },
    }

    # for k, v in infile_dict.items():
    #     print(k, v)
    #     main(k, v)

    for k, v in infile_swire_original.items():
        print(k, v)
        main(k, v)
