
# PFS Spectral Simulator Web App

PFS spectral simulator web app using [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/).

## Requirements

For production:
- python (>3.9)
- panel
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

## Installation

First of all, please clone this repository. There are several ways to install the app.

### Local installation

```sh
# if you use pip
pip install -r requirements.txt
pip install -e .

# if you use poetry
poetry install

# if you use pdm
pdm install
```

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
panel serve ./app.py

# installed via poetry
poetry run panel serve ./app.py

# installed via pdm
pdm run panel serve ./app.py
```

Then open `http://localhost:5006/app` in a web browser.

### Docker container

Open `http://localhost:8080/app` in a web browser.

### Google Cloud Run

Open your app URL in a web browser.

## License

[MIT](LICENSE) © [monodera](https://github.com/monodera).
