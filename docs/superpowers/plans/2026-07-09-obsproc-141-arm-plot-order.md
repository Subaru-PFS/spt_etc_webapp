# OBSPROC-141: Arm Plot Order Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show only the spectrograph arm (`r` or `m`) that the ETC actually
computed, in wavelength order (Blue → Red-or-Medium-resolution → Near-IR),
instead of always showing all four arms with one of `r`/`m` empty and out
of wavelength order.

**Architecture:** `create_simspec_plot()` (`src/pfs_etc_web/pfs_etc_utils.py`)
gains an explicit `mr_mode: bool` parameter. A new pure function,
`_active_arm_keys(mr_mode)`, decides which 3 of the 4 possible arm keys to
plot and in what order; a new `ARM_PLOT_SPECS` lookup replaces the four
parallel per-arm dicts/variables that currently exist. The call site in
`PfsSpecSim.show()` (`src/pfs_etc_web/pfs_etc_specsim.py`) passes
`self.instrument.mr_mode`.

**Tech Stack:** Python 3.12, pandas, bokeh, pytest (new dev dependency —
the repo has no test runner installed yet).

## Global Constraints

- Python `>=3.12,<3.13` (from `pyproject.toml`) — safe to use bare
  `list[str]` type hints, no `typing.List` needed.
- This repo's `.claude/settings.json` PostToolUse hook auto-runs
  `ruff check --fix` and `black` on every `.py` file written/edited, so
  manual `ruff`/`black` steps below are a fallback check, not the primary
  formatting mechanism.
- `ruff`'s project config (`pyproject.toml` `[tool.ruff.lint]`) ignores
  `F401`/`F841`/`E501` and several naming-convention rules — don't be
  surprised if a lint pass is clean despite those categories.
- Follow existing patterns in `pfs_etc_utils.py`: module-level pure
  helpers before the functions that use them, `from . import PfsArm` is
  already imported (do not re-import).

---

### Task 1: Add pytest, and add `_active_arm_keys()` with tests

**Files:**
- Modify: `pyproject.toml` (dev extra)
- Modify: `uv.lock`
- Modify: `requirements.txt`
- Modify: `src/pfs_etc_web/pfs_etc_utils.py` (insert before line 305, i.e. between `create_dummy_plot()` and `create_simspec_plot()`)
- Create: `tests/test_pfs_etc_utils.py`

**Interfaces:**
- Produces: `ARM_PLOT_SPECS: dict[str, dict]` keyed by `"b"`/`"r"`/`"n"`/`"m"`, each value a dict with keys `"title"` (str), `"x_range"` (list[int, int]), `"color"` (str, a bokeh `Colorblind[7][i]` hex string).
- Produces: `_active_arm_keys(mr_mode: bool) -> list[str]` — returns exactly 3 keys, in wavelength order: `["b", "r", "n"]` when `mr_mode` is `False`, `["b", "m", "n"]` when `True`.

- [ ] **Step 1: Add pytest as a dev dependency**

Run:
```bash
uv add pytest --optional dev
```
Expected: `pyproject.toml`'s `[project.optional-dependencies]` `dev` list gains a `pytest` entry, and `uv.lock` is updated. Verify with:
```bash
uv run pytest --version
```
Expected: prints a `pytest X.Y.Z` version line (no "Failed to spawn" error).

- [ ] **Step 2: Regenerate requirements.txt**

Run:
```bash
./scripts/gen-requirements.sh uv
```
Expected: `requirements.txt` is rewritten and now contains a `pytest==...` line, matching the version locked in `uv.lock`.

- [ ] **Step 3: Write the failing test**

Create `tests/test_pfs_etc_utils.py`:

```python
from pfs_etc_web.pfs_etc_utils import _active_arm_keys


def test_active_arm_keys_normal_mode():
    assert _active_arm_keys(mr_mode=False) == ["b", "r", "n"]


def test_active_arm_keys_medium_resolution_mode():
    assert _active_arm_keys(mr_mode=True) == ["b", "m", "n"]
```

- [ ] **Step 4: Run the test and confirm it fails**

Run:
```bash
uv run pytest tests/test_pfs_etc_utils.py -v
```
Expected: FAIL — `ImportError: cannot import name '_active_arm_keys' from 'pfs_etc_web.pfs_etc_utils'`.

- [ ] **Step 5: Implement `ARM_PLOT_SPECS` and `_active_arm_keys()`**

In `src/pfs_etc_web/pfs_etc_utils.py`, insert the following between the end of `create_dummy_plot()` (line 302, `    return column(p)`) and the blank lines before `def create_simspec_plot(` (currently line 305):

```python
ARM_PLOT_SPECS = {
    "b": {"title": "Blue arm", "x_range": [380, 650], "color": Colorblind[7][0]},
    "r": {"title": "Red arm", "x_range": [630, 970], "color": Colorblind[7][3]},
    "n": {"title": "Near-IR arm", "x_range": [940, 1260], "color": Colorblind[7][1]},
    "m": {
        "title": "Medium resolution arm",
        "x_range": [710, 885],
        "color": Colorblind[7][6],
    },
}


def _active_arm_keys(mr_mode: bool) -> list[str]:
    """Arm plot keys to display, in wavelength order.

    The ETC computes at most 3 arms per run (n_workers is capped to 3 in
    pfsspecsim's Etc.run()), so r (normal resolution) and m (medium
    resolution) are mutually exclusive depending on ``mr_mode``.
    """
    return ["b", "m" if mr_mode else "r", "n"]
```

- [ ] **Step 6: Run the test and confirm it passes**

Run:
```bash
uv run pytest tests/test_pfs_etc_utils.py -v
```
Expected: `2 passed`.

- [ ] **Step 7: Lint check**

Run:
```bash
uv run ruff check src/pfs_etc_web/pfs_etc_utils.py tests/test_pfs_etc_utils.py
uv run black --check src/pfs_etc_web/pfs_etc_utils.py tests/test_pfs_etc_utils.py
```
Expected: `All checks passed!` and `would be left unchanged` for both.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml uv.lock requirements.txt src/pfs_etc_web/pfs_etc_utils.py tests/test_pfs_etc_utils.py
git commit -m "Add pytest and _active_arm_keys() with tests for OBSPROC-141"
```

---

### Task 2: Refactor `create_simspec_plot()` to build only the active arms

**Files:**
- Modify: `src/pfs_etc_web/pfs_etc_utils.py:305-506` (full function body replacement)

**Interfaces:**
- Consumes: `ARM_PLOT_SPECS`, `_active_arm_keys(mr_mode: bool) -> list[str]` (Task 1). `PfsArm` (already imported at the top of the file via `from . import PfsArm`).
- Produces: `create_simspec_plot(df, df_snline, df_sncont, mr_mode: bool, aspect_ratio: float = 2.5)` — same return type as before (a `bokeh.layouts.column`), now containing exactly `len(_active_arm_keys(mr_mode)) + 1` children (3 arm panels + the emission-line S/N panel), in wavelength order.

- [ ] **Step 1: Replace the function body**

Replace the entire `create_simspec_plot` function (from `def create_simspec_plot(` through the closing `)` of its `return column(...)`, currently lines 305-506) with:

```python
def create_simspec_plot(
    df: pd.DataFrame,
    df_snline: pd.DataFrame,
    df_sncont: pd.DataFrame,
    mr_mode: bool,
    aspect_ratio: float = 2.5,
):
    kwargs_simspec = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="Flux (nJy)",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_drag="box_zoom",
    )
    kwargs_snline = dict(
        x_axis_label="Wavelength (nm)",
        y_axis_label="S/N",
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        output_backend="webgl",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_drag="box_zoom",
    )
    extra_y_axis_label = "S/N per pixel"

    # pandas 3 may return a read-only array from to_numpy(); copy for safe mutation.
    input_spec = df_sncont["input_spec"].to_numpy(copy=True)
    input_spec[np.isclose(input_spec, np.zeros_like(input_spec))] = np.nan
    input_spec = (input_spec * u.ABmag).to(u.nJy).value

    ymin, ymax = -np.nanmax(input_spec) * 0.2, np.nanmax(input_spec) * 2
    ymin2, ymax2 = 0.0, np.nanmax(df_sncont["sncont"]) * 1.5

    df["sncont"] = df_sncont["sncont"]
    df["is_saturated"] = df_sncont["is_saturated"]
    df["input_spec"] = input_spec

    # The ETC computes at most 3 arms per run (n_workers is capped to 3),
    # so r and m are mutually exclusive. Only build the arm that's
    # actually active, in wavelength order.
    arm_keys = _active_arm_keys(mr_mode)

    dict_df_arm = {key: df.loc[df["arm"] == PfsArm[key].value, :] for key in arm_keys}
    dict_source_arm = {key: ColumnDataSource(dict_df_arm[key]) for key in arm_keys}

    tooltips = [
        ("Wavelength", "@wavelength"),
        ("Input", "@input_spec"),
        ("Flux", "@flux"),
        ("Error", "@error"),
        ("S/N", "@sncont"),
    ]
    tooltips_snline = [
        ("Wavelength", "@wavelength"),
        ("S/N", "@snline_tot"),
    ]

    figures = {}
    for key in arm_keys:
        spec = ARM_PLOT_SPECS[key]
        figures[key] = figure(
            title=spec["title"],
            x_range=spec["x_range"],
            y_range=[ymin, ymax],
            tooltips=tooltips,
            **kwargs_simspec,
        )

    p_snline = figure(
        title="Emission Line S/N",
        x_range=[380, 1260],
        tooltips=tooltips_snline,
        **kwargs_snline,
    )

    for arm in arm_keys:
        p_arm = figures[arm]
        color = ARM_PLOT_SPECS[arm]["color"]

        # plot flux
        p_arm.line(
            "wavelength",
            "flux",
            source=dict_source_arm[arm],
            color=color,
            alpha=0.8,
            legend_label="Flux",
        )
        # plot input spectrum
        p_arm.line(
            "wavelength",
            "input_spec",
            source=dict_source_arm[arm],
            color=color,
            line_width=2,
            legend_label="Input",
        )
        # plot error
        p_arm.line(
            "wavelength",
            "error",
            source=dict_source_arm[arm],
            color="gray",
            alpha=0.8,
            legend_label="Error",
        )
        # indicate saturated pixels
        if np.any(dict_df_arm[arm]["is_saturated"]):
            logger.info(f"Saturated pixels in {arm} arm detected.")

            n_sat_sample = 15
            if np.sum(dict_df_arm[arm]["is_saturated"]) < n_sat_sample:
                n_sat_sample = 1
            logger.info(
                f"One in every {n_sat_sample} saturated datapoints are plotted as flagged."
            )
            flag_saturate = np.zeros_like(dict_df_arm[arm]["is_saturated"], dtype=bool)
            flag_saturate[::n_sat_sample] = dict_df_arm[arm]["is_saturated"][
                ::n_sat_sample
            ].to_numpy()

            p_arm.scatter(
                "wavelength",
                "input_spec",
                source=dict_source_arm[arm],
                view=CDSView(
                    filter=BooleanFilter(flag_saturate),
                ),
                marker="circle_x",
                fill_color=None,
                line_color="orangered",
                size=10,
                alpha=0.8,
                legend_label="Saturated",
            )

        # plot S/N using the right-side axis
        p_arm.extra_y_ranges = {"sncont": Range1d(start=ymin2, end=ymax2)}
        p_arm.add_layout(
            LinearAxis(y_range_name="sncont", axis_label=extra_y_axis_label),
            "right",
        )
        p_arm.line(
            "wavelength",
            "sncont",
            source=dict_source_arm[arm],
            color=Colorblind[7][6],
            alpha=0.8,
            y_range_name="sncont",
            legend_label="S/N",
        )
        p_arm.legend.location = "top_left"
        p_arm.legend.click_policy = "mute"
        p_arm.legend.orientation = "horizontal"

    p_snline.line(
        "wavelength",
        "snline_tot",
        source=df_snline,
        color=Colorblind[7][6],
        legend_label="S/N",
    )
    p_snline.legend.location = "top_left"
    p_snline.legend.click_policy = "mute"

    return column(children=[figures[key] for key in arm_keys] + [p_snline])
```

- [ ] **Step 2: Syntax-check the file**

Run:
```bash
uv run python -m py_compile src/pfs_etc_web/pfs_etc_utils.py
```
Expected: no output, exit code 0.

- [ ] **Step 3: Run the full test suite**

Run:
```bash
uv run pytest -v
```
Expected: `2 passed` (the Task 1 tests; unaffected by this change since `create_simspec_plot` isn't under test).

- [ ] **Step 4: Lint check**

Run:
```bash
uv run ruff check src/pfs_etc_web/pfs_etc_utils.py
uv run black --check src/pfs_etc_web/pfs_etc_utils.py
```
Expected: `All checks passed!` and `would be left unchanged`.

- [ ] **Step 5: Commit**

```bash
git add src/pfs_etc_web/pfs_etc_utils.py
git commit -m "Only build the active r/m arm plot, in wavelength order"
```

---

### Task 3: Pass `mr_mode` at the `create_simspec_plot()` call site

**Files:**
- Modify: `src/pfs_etc_web/pfs_etc_specsim.py:289`

**Interfaces:**
- Consumes: `create_simspec_plot(df, df_snline, df_sncont, mr_mode: bool, aspect_ratio: float = 2.5)` (Task 2). `self.instrument` is the `InstrumentConf` instance already stored on `PfsSpecSim` (set in `__init__`, has a `.mr_mode: bool` attribute — see `src/pfs_etc_web/pfs_etc_params.py`'s `InstrumentConf.mr_mode`).

- [ ] **Step 1: Update the call site**

In `src/pfs_etc_web/pfs_etc_specsim.py`, replace line 289:

```python
        self.p_simspec = create_simspec_plot(df_simspec, df_snline, df_sncont)
```

with:

```python
        self.p_simspec = create_simspec_plot(
            df_simspec, df_snline, df_sncont, self.instrument.mr_mode
        )
```

- [ ] **Step 2: Syntax-check the file**

Run:
```bash
uv run python -m py_compile src/pfs_etc_web/pfs_etc_specsim.py
```
Expected: no output, exit code 0.

- [ ] **Step 3: Run the full test suite**

Run:
```bash
uv run pytest -v
```
Expected: `2 passed`.

- [ ] **Step 4: Lint check**

Run:
```bash
uv run ruff check src/pfs_etc_web/pfs_etc_specsim.py
uv run black --check src/pfs_etc_web/pfs_etc_specsim.py
```
Expected: `All checks passed!` and `would be left unchanged`.

- [ ] **Step 5: Commit**

```bash
git add src/pfs_etc_web/pfs_etc_specsim.py
git commit -m "Pass instrument.mr_mode into create_simspec_plot"
```

---

### Task 4: Manual end-to-end verification (both modes)

**Files:** none (verification only; no commit unless a bug is found, in
which case fix it in the relevant task above and re-commit there).

**Interfaces:**
- Consumes: the running app at `http://localhost:5007/etc`, started via `./scripts/serve-app.sh` (see README.md / CLAUDE.md).

- [ ] **Step 1: Start the dev server**

Run in the background:
```bash
./scripts/serve-app.sh
```
Expected: log output showing the Panel server bound to port 5007 with prefix `/etc`. Wait for it to report ready before proceeding.

- [ ] **Step 2: Verify normal-resolution mode (default)**

Open `http://localhost:5007/etc` in a browser. Leave the "Instrument" tab's "Use Medium Resolution? (checked=True)" checkbox unchecked (the default). Click "Run" and wait for it to complete (the "Run" button re-enables and plots appear).

Expected: exactly 4 plot panels appear, top to bottom, titled: "Blue arm", "Red arm", "Near-IR arm", "Emission Line S/N". No "Medium resolution arm" panel is present.

- [ ] **Step 3: Verify medium-resolution mode**

Click "Reset". Go to the "Instrument" tab and check "Use Medium Resolution? (checked=True)". Click "Run" and wait for it to complete.

Expected: exactly 4 plot panels appear, top to bottom, titled: "Blue arm", "Medium resolution arm", "Near-IR arm", "Emission Line S/N". No "Red arm" panel is present.

- [ ] **Step 4: Stop the dev server**

Stop the background process started in Step 1 (e.g. `Ctrl-C` in its terminal, or `kill` the process).

- [ ] **Step 5: If either check in Step 2 or 3 failed**

Go back to Task 2 (panel construction/ordering) or Task 3 (mr_mode wiring), fix the issue, re-run that task's Step 2-4 (syntax check / test suite / lint), commit the fix, and repeat this task from Step 1.
