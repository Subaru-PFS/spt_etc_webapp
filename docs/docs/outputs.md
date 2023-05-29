# Outputs

## Files

Once the calculation is finished, five buttons will show up in the upper part of the right panel.
Four of them correspond to the simulated spectrum before merging different arms in to `pfsObject` file and
emission line S/N in two file formats.
These files are in FITS binary table format and [Enhanced Character-Separated Values (ECSV) format](https://github.com/astropy/astropy-APEs/blob/main/APE6.rst) which can be easily read by astropy or other common libraries and softwares. For example, both FITS binary table and ECSV files are also supported by TOPCAT.

The other file is a `pfsObject` file which stores the arm-merged spectrum as well as various information
defined in the [PFS datamodel](https://github.com/Subaru-PFS/datamodel/blob/37d0bda305ea3fb5c86bc88aaa77581975540112/datamodel.txt).
Note that the file name in the app does not conform the datamodel.
If you have any difficulty handling the `pfsObject` file,
you can use the original file name `pfsObject-000-00000-0,0-0000000000000001-001-0x8cf7641568bdb4ab.fits` (for the case of the number of visits of 1).
Note also that the datamodel adopted in the current ETC is not the latest one.



For the detail of the content, please refer the `README` of [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/) as well.

### Read the output files

A few Python examples are shown below.

```py
# with astropy

from astropy.table import Table

simspec_from_fits = Table.read("pfs_etc_simspec-YYYYMMDD-HHMMSS_################.fits")
simspec_from_ecsv = Table.read("pfs_etc_simspec-YYYYMMDD-HHMMSS_################.ecsv")

print(simspec_from_fits)  # show table content
print(simspec_from_fits.meta)  # show metadata

df_from_astropy = simspec_from_fits.to_pandas()  # convert to pandas.DataFrame

print(df_from_astropy)
```

```py
# with pandas

import pandas as pd

df = pd.read_csv("pfs_etc_simspec-YYYYMMDD-HHMMSS_################.ecsv", comment="#")

print(df)
```




### Simulated spectrum

Files for the simulated spectrum (`pfs_simspec*`) contain the following columns.

| name       | unit    | datatype | description                      |
|------------|---------|----------|----------------------------------|
| wavelength | nm      | float64  | Wavelength in vacuum             |
| flux       | nJy     | float64  | Flux                             |
| error      | nJy     | float64  | Error                            |
| sn         | 1 / pix | float64  | S/N per pixel                    |
| flux_input | nJy     | float64  | Input flux                       |
| sky        | nJy     | float64  | Sky                              |
| mask       |         | bool     | Masked if True                   |
| arm        |         | int64    | Arm ID (0=blue 1=red 2=nir 3=mr) |
| pixel      |         | int64    | Pixel ID in each arm             |

The following metadata from the inputs are also included.

| name     | description                                                    |
|----------|----------------------------------------------------------------|
| TMPLSPEC | Template type                                                  |
| TMPL_MAG | AB mag to normalize template (`None` for custom input)         |
| TMPL_WAV | Wavelength for normalizing template  (`None` for custom input) |
| TMPL_Z   | Reshift of the template   (`None` for custom input)            |
| R_EFF    | Effective radius of the target                                 |
| EXPTIME  | Total exposure time                                            |
| EXPTIME1 | Single exposure time                                           |
| EXPNUM   | Number of exposures                                            |
| SEEING   | Seeing FWHM                                                    |
| ZANG     | Zenith angle                                                   |
| MOON-ZA  | Moon zenith angle                                              |
| MOON-SEP | Moon-target separation                                         |
| MOON-PH  | Moon phase (0=new, 0.25=quater, 1=new)                         |
| FLDANG   | PFS field angle (center=0, edge=0.675)                         |
| DEGRADE  | Throughput degradation factor                                  |
| GAL_EXT  | E(B-V) of Galactive extinction                                 |
| MED_RES  | `True` if medium resolution mode                               |

### Emission line S/N

Files for the emission line S/N (`pfs_snline*`) contain the following columns.

| name                      | unit | datatype | description                          |
|---------------------------|------|----------|--------------------------------------|
| wavelength                | nm   | float64  | Wavelength in vacuum                 |
| fiber_aperture_factor     |      | float64  | Fiber aperture factor                |
| effective_collecting_area | m2   | float64  | Effective collecting area            |
| snline_b                  |      | float64  | Emission line S/N in the blue arm    |
| snline_r                  |      | float64  | Emission line S/N in the red arm     |
| snline_n                  |      | float64  | Emission line S/N in the near-IR arm |
| snline_tot                |      | float64  | Total emission line S/N              |

The following metadata from the inputs are also included.

| name     | description                                                    |
|----------|----------------------------------------------------------------|
| EL_FLUX  | Emission line flux (erg/s/cm^2/A)                              |
| EL_SIG   | Emission line velocity dispersion sigma (km/s)                 |
| TMPLSPEC | Template type                                                  |
| TMPL_MAG | AB mag to normalize template (`None` for custom input)         |
| TMPL_WAV | Wavelength for normalizing template  (`None` for custom input) |
| TMPL_Z   | Reshift of the template   (`None` for custom input)            |
| R_EFF    | Effective radius of the target                                 |
| EXPTIME  | Total exposure time                                            |
| EXPTIME1 | Single exposure time                                           |
| EXPNUM   | Number of exposures                                            |
| SEEING   | Seeing FWHM                                                    |
| ZANG     | Zenith angle                                                   |
| MOON-ZA  | Moon zenith angle                                              |
| MOON-SEP | Moon-target separation                                         |
| MOON-PH  | Moon phase (0=new, 0.25=quater, 1=new)                         |
| FLDANG   | PFS field angle (center=0, edge=0.675)                         |
| DEGRADE  | Throughput degradation factor                                  |
| GAL_EXT  | E(B-V) of Galactive extinction                                 |
| MED_RES  | `True` if medium resolution mode                               |

### pfsObject

The following information is just a copy of the  [PFS datamodel](https://github.com/Subaru-PFS/datamodel/blob/37d0bda305ea3fb5c86bc88aaa77581975540112/datamodel.txt).

```
HDU #0 PDU
HDU #1 FLUX        Flux in units of nJy                       [FLOAT]        NROW
HDU #2 MASK        Pixel mask                                 [32-bit INT]   NROW
HDU #3 TARGET      Binary table                                [FITS BINARY TABLE] NFILTER
               Columns for:
               filterName                              [STRING]
               fiberMag                                [FLOAT]
HDU #4 SKY         Sky flux in same units as FLUX             [FLOAT]        NROW
HDU #5 COVAR       Near-diagonal part of FLUX's covariance    [FLOAT]        NROW*3
HDU #6 COVAR2      Low-resolution non-sparse estimate covariance [FLOAT]      NCOARSE*NCOARSE
HDU #7 OBSERVATIONS    Binary table                            [FITS BINARY TABLE] NOBS
               Columns for:
               visit                                   [32-bit INT]
               arm                                     [STRING]
               spectrograph                            [32-bit INT]
               pfsDesignId                             [64-bit INT]
               fiberId                                 [32-bit INT]
               nominal PFI position (microns)          [FLOAT]*2
               actual PFI position (microns)           [FLOAT]*2
HDU #8 FLUXTABLE   Binary table                                [FITS BINARY TABLE] NOBS*NROW
               Columns for:
		       wavelength in units of nm (vacuum)          [FLOAT]
		       intensity in units of nJy                   [FLOAT]
		       intensity error in same units as intensity  [FLOAT]
		       mask                                        [32-bit INT]
```

## Plots

Five panels will be shown for blue arm, red arm, near-IR arm, medium-resolution arm, and emission line S/N.
You can click the legend to highlight or mute lines of your interest.

![type:video](videos/legend_mute.mp4)

You can also zoom, pan, etc. by using the Bokeh tooltips located at the right side of each plot.


