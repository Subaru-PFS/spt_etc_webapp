#!/usr/bin/env python

import os

import matplotlib.pyplot as plt
import seaborn as sns
import synphot
from astropy import units as u
from astropy.io.fits import getval

# plt.style.use("seaborn-v0_8-colorblind")
# plt.style.use("tableau-colorblind10")


def plot_spectra(
    spec,
    ax=None,
    plot_prefix="spec",
    specdir=".",
    plotdir=".",
    norm_wavelength: u.Quantity = 550.0 * u.nm,
    norm_mag: u.Quantity = 20.0 * u.ABmag,
    norm_bandwidth: u.Quantity = 10.0 * u.nm,
    sample=1,
    ncol_legend=1,
    pltkwargs={},
):

    band = synphot.SpectralElement(
        synphot.models.Box1D,
        amplitude=1.0,
        x_0=norm_wavelength,
        width=norm_bandwidth,
    )

    for k, v in spec.items():
        infile = os.path.join(specdir, v)
        sp_rest = synphot.SourceSpectrum.from_file(
            infile,
            # wave_unit=u.AA,
            # flux_unit=u.erg / u.s / u.cm**2 / u.AA,
        )
        # min/max wavelenghth supported in the original template
        wmin0 = getval(infile, "WAVE_MIN", 1)  # angstrom
        wmax0 = getval(infile, "WAVE_MAX", 1)  # angstrom

        sp_norm = sp_rest.normalize(norm_mag, band=band)

        wout = sp_norm.waveset.to(u.nm).value
        fout = sp_norm(sp_norm.waveset, flux_unit=u.ABmag).value

        ax.plot(wout[::sample], fout[::sample], label=k, **pltkwargs)

    ax.set_xlim(100, 1300)
    ax.set_ylim(23.9, 17.1)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Normalized Flux (AB mag)")
    # ax.grid(True)

    ax.legend(loc="lower right", ncol=ncol_legend)
    # fig.legend(loc="outside upper right")


if __name__ == "__main__":
    specdir = "output"
    plotdir = "figures"
    spec_stars = {
        "B0V": "star_b0v.fits",
        "A0V": "star_a0v.fits",
        "F0V": "star_f0v.fits",
        "G2V": "star_g2v.fits",
        "K0V": "star_k0v.fits",
        "K0III": "star_k0iii.fits",
        "M0V": "star_m0v.fits",
        "M0III": "star_m0iii.fits",
    }

    spec_ssp = {
        "SSP 100 Myr": "galaxy_starforming.fits",
        "SSP 1 Gyr": "galaxy_quiescent.fits",
    }
    spec_swire = {
        "Elliptical 2 Gyr": "galaxy_swire_elliptical_2gyr.fits",
        "Elliptical 5 Gyr": "galaxy_swire_elliptical_5gyr.fits",
        "Elliptical 13 Gyr": "galaxy_swire_elliptical_13gyr.fits",
        "S0": "galaxy_swire_spiral_s0.fits",
        "Sa": "galaxy_swire_spiral_sa.fits",
        "Sb": "galaxy_swire_spiral_sb.fits",
        "Sc": "galaxy_swire_spiral_sc.fits",
        "Sd": "galaxy_swire_spiral_sd.fits",
        "Sdm": "galaxy_swire_spiral_sdm.fits",
        # "Quasar": "quasar.fits",
    }

    spec_quasar = {
        "Quasar": "quasar.fits",
    }

    sns.set_style("whitegrid")
    sns.set_context("notebook")
    # sns.set_palette(sns.color_palette("flare", len(spec.keys())))
    fig, ax = plt.subplots(
        ncols=2,
        nrows=2,
        figsize=(16, 9),
        gridspec_kw={"hspace": 0.2, "wspace": 0.15},
    )

    plot_spectra(
        spec_stars,
        ax=ax[1, 1],
        plot_prefix="stars",
        specdir=specdir,
        plotdir=plotdir,
        sample=25,
        ncol_legend=2,
        pltkwargs={"lw": 1, "alpha": 0.8},
    )

    plot_spectra(
        spec_ssp,
        ax=ax[0, 0],
        plot_prefix="galaxy_ssp",
        specdir=specdir,
        plotdir=plotdir,
        # sample=25,
        ncol_legend=1,
        pltkwargs={"lw": 1, "alpha": 0.8},
    )

    plot_spectra(
        spec_swire,
        ax=ax[0, 1],
        plot_prefix="galaxy_swire",
        specdir=specdir,
        plotdir=plotdir,
        # sample=25,
        ncol_legend=2,
        pltkwargs={"lw": 1, "alpha": 0.8},
    )

    plot_spectra(
        spec_quasar,
        ax=ax[1, 0],
        plot_prefix="quasar",
        specdir=specdir,
        plotdir=plotdir,
        # sample=25,
        # ncol_legend=2,
        pltkwargs={"lw": 1, "alpha": 0.8},
    )
    plt.savefig(os.path.join(plotdir, "template_spectra.pdf"), bbox_inches="tight")
    plt.savefig(
        os.path.join(plotdir, "template_spectra.png"), dpi=300, bbox_inches="tight"
    )
