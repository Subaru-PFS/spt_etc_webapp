# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Panel (HoloViz) web app that wraps the PFS (Prime Focus Spectrograph) Exposure Time
Calculator and Spectrum Simulator. The heavy computation is delegated to the external
`pfsspecsim` package (`Subaru-PFS/spt_ExposureTimeCalculator`, pinned to tag `v2.0.0` in
`pyproject.toml`) — this repo is the UI/orchestration layer around it, not the simulator
itself.

## Commands

The project supports uv, PDM, and pip+venv interchangeably; `./scripts/*.sh` auto-detect
which one is available (priority: uv > pdm > venv) or accept an explicit
`uv`/`pdm`/`venv` argument.

```sh
# Run the dev server (autoreload, port 5007, prefix /etc)
./scripts/serve-app.sh

# Equivalent direct command
uv run panel serve ./app.py --static-dirs doc=docs/site --prefix=etc --port=5007

# Docs
./scripts/build-doc.sh     # cd docs && mkdocs build -> docs/site
./scripts/serve-doc.sh     # mkdocs serve (live preview)

# Regenerate requirements.txt from lockfile (uv/pdm export)
./scripts/gen-requirements.sh

# Lint / format / typecheck (requires the dev extra)
uv sync --extra dev
uv run ruff check .
uv run black .
uv run ty check
```

`docs/site` must exist before serving the app (`--static-dirs doc=docs/site`), so run the
doc build once after cloning.

A `PostToolUse` hook (`.claude/settings.json` → `.claude/hooks/format_python.sh`) auto-runs
`ruff check --fix` and `black` on any `.py` file Claude writes/edits. `ty check` is not
wired into a hook — it currently has ~75 pre-existing repo-wide findings, so run it manually
when needed rather than treating it as a gate.

**Environment:** output location is controlled by `OUTPUT_DIR` in `.env` (defaults to
`tmp` if `.env` is absent) — every simulation writes under
`OUTPUT_DIR/YYYY/MM/<simulation_id>/`.

There is currently no test suite (`tests/__init__.py` is the only file, and it's empty) —
there is nothing to run with pytest yet.

## Architecture

**Entry point:** `app.py` configures Panel extensions (mathjax, floatpanel, notifications)
and calls `pfs_etc_app()` in `src/pfs_etc_web/pn_app.py`, which builds the `MaterialTemplate`
UI and is the only place that wires everything together.

**Config objects (`pfs_etc_params.py`):** `PfsSpecParameter` is a frozen dataclass holding
every default value; `TargetConf`, `EnvironmentConf`, `InstrumentConf`, `TelescopeConf`,
`OutputConf`, `SimulationConf` are `param.Parameterized` classes that read their defaults
from it. These are the live, UI-bound state objects — widgets and the simulator both operate
on the same instances.

**Widgets (`pfs_etc_widgets.py`):** One `param.Parameterized` widget class per config group
(`TargetWidgets`, `EnvironmentWidgets`, `InstrumentWidgets`, `TelescopeWidgets`), plus
non-param helper classes for buttons, plot panes, and download links
(`ExecButtonWidgets`, `BokehWidgets`, `DownloadWidgets`, `VersionInfoWidgets`). Each widget
class is constructed with the matching `*Conf` instance and keeps it in sync with the UI.

**Simulation engine (`pfs_etc_specsim.py`):** `PfsSpecSim` wraps pfsspecsim's typed v2 API.
`run_etc()` builds an `EtcParams` (mapping the `*Conf` objects; `mag` and `mag_file` are
mutually exclusive — flat-in-frequency targets leave `target.mag_file` as `None`) and calls
`run_etc_files()`, which writes the `noise`/`sn_continuum`/`sn_line` ECSV files; `run_sim()`
builds a `SimSpecParams` pointing at the `sn_continuum.ecsv` output and calls
`run_sim_spec()`; `show()` loads the resulting files (falling back to legacy `.dat` names so
pre-migration sessions still recover), builds the Bokeh plot, and writes the downloadable
`pfsObject`/simspec/snline FITS+ECSV files. `exec()` is the `run_etc` + `run_sim` entry
point called from the UI. The compute is fully in-process pure Python (no subprocess).

**Session/output model:** Each "Run" click generates a UTC-timestamped
`simulation_id` (`YYYYMMDD-HHMMSS-<hex>`), which becomes the output subdirectory
`OUTPUT_DIR/YYYY/MM/<simulation_id>/` (`OUTPUT_DIR` from `.env`, default `tmp`). The
`simulation_id` is synced to the page's `?id=` query parameter so reloading the page (or
sharing the URL) can recover a previous simulation via `recover_simulation()` in
`pfs_etc_utils.py`, which re-reads the saved output files rather than re-running the
simulation.

**Async callbacks:** `on_click_exec` is an `async def` handler: all UI mutations run on the
session's event loop (so `curdoc` is automatically correct), and only the blocking
computation is pushed off the loop via `await asyncio.to_thread(specsim.exec)`. Widget
re-enabling and the loading spinner are cleared in a `finally` block so the UI never sticks
on errors, and a re-entrancy guard (`if panel_buttons.exec.disabled: return`) prevents
double-clicks. Follow this pattern for any new long-running action: async handler +
`asyncio.to_thread` for the blocking part, never a bare thread or polling loop.

**`pfs_etc_utils.py`:** I/O and plotting helpers — loaders for the ETC's legacy
whitespace-delimited ASCII output and newer ECSV output (`load_simspec`, `load_snline`,
`load_sncont`, with `_looks_like_ecsv` auto-detecting format), Bokeh plot construction
(`create_simspec_plot`), FITS/ECSV table writers (`create_simspec_files`), and
`recover_simulation`.

**`pfs_etc_spectemplates.py`:** Builds the magnitude/template spectrum file
(`create_template_spectrum`) fed into the ETC as `EtcParams.mag_file`, from the built-in
template library or a user-uploaded custom spectrum; for flat-in-frequency targets it sets
`target.mag_file = None` and the ETC uses the scalar `mag` instead.

**`PfsArm` enum** (`src/pfs_etc_web/__init__.py`): the four PFS arms (`b`/`r`/`n`/`m` =
Blue/Red/Near-IR/Medium-resolution), each carrying a display `label`. Used wherever
per-arm results (e.g. saturation flags) are indexed.

**CLI (`src/pfs_etc_web/cli/`):** `run_panel_server.py` provides the `run_pfs_etc_web`
console script, but it's a simplified launcher — prefer `scripts/serve-app.sh` or direct
`panel serve` (see README) since the CLI lacks static-dir/prefix/websocket config.
`clean_outputs.py` is an unfinished stub (`main()` is a no-op).

## Deployment

`Dockerfile` builds a container that runs `panel serve` on port 8080; the app is also
deployable directly to Google Cloud Run (`gcloud run deploy pfsetcweb --source .`).
`ETC_N_WORKERS` (fallback: `OMP_NUM_THREADS`, kept for deployment compatibility) sets the
ETC engine's `ThreadPoolExecutor` worker count (`EtcParams.n_workers`, results are
bit-identical regardless of the value); unset, pfsspecsim defaults to `min(8, cpu)`.
