
# PFS Spectral Simulator Web App

PFS spectral simulator web app using [PFS Exposure Time Calculator and Spectrum Simulator](https://github.com/Subaru-PFS/spt_ExposureTimeCalculator/).

## Prerequisites

This project uses [**uv**](https://docs.astral.sh/uv/) as its package manager. A
plain **pip + venv** install is also supported as a fallback for environments
without uv.

Dependencies are declared in `pyproject.toml`:

- `[project.dependencies]` - runtime dependencies needed to run the app
- `[dependency-groups]` - non-runtime dependencies, split by purpose:
  - `dev` - lint/format/typecheck/test tools (ruff, black, ty, pytest) and
    Panel's autoreload dependency (watchfiles)
  - `docs` - MkDocs and its plugins, needed to build `docs/site`
  - `spectemplates` - matplotlib/seaborn/scipy/specutils, needed only by the
    template-spectrum helper scripts under `scripts/`

### Using uv (Recommended)

```sh
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (uv includes the "dev" group by default)
uv sync

# With documentation dependencies too
uv sync --group docs

# With everything (dev + docs + spectemplates)
uv sync --all-groups

# Runtime dependencies only, no groups at all (e.g. for a production image)
uv sync --no-default-groups
```

### Using pip + venv

```sh
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install runtime dependencies
pip install -e .

# Documentation and development dependencies are declared as
# dependency-groups (PEP 735), which `pip install -e .` does not resolve.
# Install the packages directly instead, e.g.:
pip install mkdocs mkdocs-material mkdocs-macros-plugin mkdocs-video myst-parser
pip install ruff black ty pytest ipython watchfiles
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
```

`./scripts/serve-app.sh` enables Panel development autoreload and will ensure `watchfiles` is installed before startup. If you prefer to install it yourself, use the development dependency commands above.

You can force a specific package manager:

```sh
./scripts/serve-app.sh uv    # Force use of uv
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

**With venv:**

```sh
source .venv/bin/activate

# Run the web app
panel serve ./app.py --static-dirs doc=docs/site --prefix=etc --port=5007

# Build documentation
cd docs && mkdocs build
```

### Performance Tuning

The ETC engine (`pfsspecsim` v2, pure Python) runs its computation with a
`ThreadPoolExecutor`. You can set the number of worker threads with the
`ETC_N_WORKERS` environment variable (if unset, `OMP_NUM_THREADS` is used as a
fallback for compatibility with older deployments; if neither is set, the
engine defaults to `min(8, number of CPUs)`). Results are bit-identical
regardless of the worker count — it only affects the running time.

Note: the OpenMP thread-count benchmark that used to be listed here was
measured with the pre-v2 C implementation and no longer applies.

### Docker container

Open `http://localhost:8080/app` in a web browser.

### Google Cloud Run

Open your app URL in a web browser.

## License

[MIT](LICENSE) © [monodera](https://github.com/monodera).
