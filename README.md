
# PFS Spectral Simulator Web App

PFS spectral simulator web app using [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/).

## Prerequisites

This project supports multiple Python package managers:

- **uv** (recommended) - Modern, fast package manager
- **PDM** - Python Development Master
- **pip + venv** - Traditional Python package management

Choose the one that best fits your workflow.

See `requirements.txt` for the complete list of dependencies.

## Installation

First of all, please clone this repository. There are several ways to install the app.

### Using uv (Recommended)

```sh
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# With documentation dependencies
uv sync --extra mkdocs
```

### Using PDM

```sh
# Install PDM if not already installed
pip install pdm

# Install dependencies
pdm install

# With documentation dependencies
pdm install -G mkdocs
```

### Using pip + venv

```sh
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# With documentation dependencies
pip install -e .[mkdocs]
```

### Building Documentation

```sh
# Using helper script (auto-detects package manager)
./scripts/build-doc.sh

# Or manually
cd docs && mkdocs build
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

### Using Helper Scripts

The project includes helper scripts in the `scripts/` directory that automatically detect your package manager:

```sh
# Start the web application
./scripts/serve-app.sh

# Start documentation server
./scripts/serve-doc.sh

# Build documentation
./scripts/build-doc.sh

# Generate requirements.txt
./scripts/gen-requirements.sh
```

You can force a specific package manager:

```sh
./scripts/serve-app.sh uv    # Force use of uv
./scripts/serve-app.sh pdm   # Force use of PDM
./scripts/serve-app.sh venv  # Force use of venv
```

Access the app at: `http://localhost:5007/etc`

### Direct Commands

**Note:** The project provides a `run_pfs_etc_web` CLI command, but using the shell scripts or direct `panel serve` commands is recommended as they provide more complete configuration (static directories, URL prefix, WebSocket settings, etc.).

**With uv:**

```sh
# Run the web app
uv run panel serve ./app.py --static-dirs doc=docs/site --prefix=etc --port=5007

# Build documentation
cd docs && uv run mkdocs build
```

**With PDM:**

```sh
# Use PDM scripts (existing functionality)
pdm run serve-app
pdm run build-doc
pdm run serve-doc
pdm run gen-requirements

# Or run directly
pdm run panel serve ./app.py --static-dirs doc=docs/site --prefix=etc --port=5007
```

**With venv:**

```sh
source .venv/bin/activate

# Run the web app
panel serve ./app.py --static-dirs doc=docs/site --prefix=etc --port=5007

# Build documentation
cd docs && mkdocs build
```

### Performance Tuning

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

[MIT](LICENSE) © [monodera](https://github.com/monodera).
