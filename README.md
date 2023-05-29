
# PFS Spectral Simulator Web App

PFS spectral simulator web app using [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/).

## Requirements

For production:
- python (>=3.9)
- panel (>=1.0)
- astropy
- jinja2
- logzero
- matplotlib
- myst-parser
- numpy
- pandas
- setuptools
- synphot
- pfsspecsim @ git+<https://github.com/Subaru-PFS/spt_ExposureTimeCalculator.git@u/monodera/20230116>

For development:

- black
- ipython
- jupyter
- notebook
- pip
- ruff
- pyright
- isort
- specutils

For documentation:

- mkdocs
- mkdocs-material
- mkdocs-macros-plugin
- mkdocs-video
- fontawesome-markdown


## Installation

First of all, please clone this repository. There are several ways to install the app.


### Create a virtual environment

```sh
python3 -m venv .
source .venv/bin/activate
```

### Local installation

```sh
# if you use pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .

# if you use poetry
poetry install

# if you use pdm
pdm install
```

If you wish to build documentation, run the following command in the `docs` directory.

```sh
cd docs

# if you use pip
mkdocs build
cd ../

# if you use poetry
poetry run mkdocs build

# if you use pdm
pdm run mkdocs build
```

The documentation is built under `docs/site`.

### Docker container

If you have Docker installed, you can run the Docker image as follows.

```sh
docker run -it -p 8080:8080 --rm monodera/pfs_etc_web
```

### Google Cloud Run

You can deploy the app to Google Cloud Run.

```sh
gcloud run deploy pfsetcweb --source .
```

## Usage

### Local installation

You can run the app by using the `panel serve` as follows.

```sh
# installed via pip
panel serve ./app.py --static-dirs docs="./docs/site/"

# installed via poetry
poetry run panel serve ./app.py --static-dirs docs="./docs/site/"

# installed via pdm
pdm run panel serve ./app.py --static-dirs docs="./docs/site/"
```

Then open `http://localhost:5006/app` in a web browser.

You can specify the number of threads used by the ETC using `OMP_NUM_THREADS` environment variable. A larger number of threads will enable to achieve faster running time, but reduce the per-thread efficiency of the computation. My experiment with AMD EPYC 7542 is summarized as follows.

| OMP_NUM_THREADS | time (s) |
|----------------:|---------:|
|               1 |   274.09 |
|               2 |   158.04 |
|               4 |    82.05 |
|               8 |    45.94 |
|              16 |    23.91 |
|              32 |    13.17 |
|              64 |     7.99 |
|             128 |     4.83 |

### Docker container

Open `http://localhost:8080/app` in a web browser.

### Google Cloud Run

Open your app URL in a web browser.

## License

[MIT](LICENSE.txt) © [monodera](https://github.com/monodera).
