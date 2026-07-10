# OBSPROC-141: Show only the active r/m arm, in wavelength order

## Problem

`create_simspec_plot()` (`src/pfs_etc_web/pfs_etc_utils.py:305-506`) always
renders four stacked spectrum panels in the fixed order `[b, r, n, m]`
(Blue, Red, Near-IR, Medium-resolution).

The ETC only ever computes three spectrograph arms per run — `Etc.run()`
clamps `n_workers` to a maximum of 3 (see
`pfsspecsim/legacy/pfsetc.py:239-241`) — because `r` (normal resolution)
and `m` (medium resolution) are mutually exclusive alternatives selected
by `instrument.mr_mode`. Whichever of the two isn't active ends up as an
empty plot (`df.loc[df["arm"] == <value>, :]` has zero rows), but it's
still built and displayed.

Independently, the fixed display order isn't wavelength order: `m`'s
range (710-885 nm) sits inside `r`'s range (630-970 nm), both of which
come before `n` (940-1260 nm) — but `m` is currently plotted *after* `n`.

## Goal

Only the active arm (`r` or `m`, depending on `instrument.mr_mode`) is
built and displayed, and the panels are shown in wavelength order:
Blue → Red-or-Medium-resolution → Near-IR → (Emission Line S/N, unchanged
last panel).

Out of scope: changing panel titles/colors/tooltips, the emission-line
S/N panel, the output FITS/ECSV files (`create_simspec_files`), or the
saturation-notification logic in `pn_app.py` (already safe: `np.any()` on
an empty array is `False`, so the inactive arm never fires a spurious
saturation warning).

## Design

### 1. `mr_mode` becomes an explicit input to plotting

`create_simspec_plot()` gains an `mr_mode: bool` parameter, mirroring how
`create_simspec_files()` already threads `param_inst.mr_mode` through as
the `MED_RES` metadata field — the plot and the saved files should agree
on which arm was active by the same signal, not by re-deriving it from
whichever DataFrame happens to be non-empty.

`PfsSpecSim.show()` (`src/pfs_etc_web/pfs_etc_specsim.py`) passes
`self.instrument.mr_mode` at the existing call site.

### 2. Per-arm metadata collapses into one table, keyed by arm

Today, titles/x-ranges/colors for all four arms are declared as four
parallel `dict(b=..., r=..., n=..., m=...)` literals, and the plotting
loop at line 412 zips two hardcoded lists together. Replace these with a
single lookup:

```python
ARM_PLOT_SPECS = {
    "b": {"title": "Blue arm", "x_range": [380, 650], "color": Colorblind[7][0]},
    "r": {"title": "Red arm", "x_range": [630, 970], "color": Colorblind[7][3]},
    "n": {"title": "Near-IR arm", "x_range": [940, 1260], "color": Colorblind[7][1]},
    "m": {"title": "Medium resolution arm", "x_range": [710, 885], "color": Colorblind[7][6]},
}
```

### 3. A pure function decides which arms to plot, in order

```python
def _active_arm_keys(mr_mode: bool) -> list[str]:
    """Arm plot keys to display, in wavelength order.

    The ETC computes at most 3 arms per run (n_workers is capped to 3),
    so r (normal resolution) and m (medium resolution) are mutually
    exclusive depending on ``mr_mode``.
    """
    return ["b", "m" if mr_mode else "r", "n"]
```

This is the one place the r-vs-m branching lives. It takes no bokeh
dependency, so it's directly unit-testable.

### 4. `create_simspec_plot()` builds only the active figures

Replace the four parallel `dict_df_arm` / `dict_source_arm` literals and
the four separately-named `p_simspec_b/r/n/m` variables with a loop over
`_active_arm_keys(mr_mode)`:

```python
arm_keys = _active_arm_keys(mr_mode)

dict_df_arm = {k: df.loc[df["arm"] == PfsArm[k].value, :] for k in arm_keys}
dict_source_arm = {k: ColumnDataSource(dict_df_arm[k]) for k in arm_keys}

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

for key in arm_keys:
    # existing per-arm body (flux/input/error/saturation/S-N lines),
    # reading from figures[key], dict_source_arm[key], dict_df_arm[key],
    # ARM_PLOT_SPECS[key]["color"]
    ...

return column(children=[figures[k] for k in arm_keys] + [p_snline])
```

The inactive r-or-m figure is never constructed (today it's built, wired
up, and discarded).

`PfsArm[key].value` relies on the existing `PfsArm` enum member names
(`b`, `r`, `n`, `m`) matching the plot keys 1:1 — already true today.

## Testing

The repo currently has no automated tests (`tests/__init__.py` is empty).
`_active_arm_keys()` is a small, dependency-free pure function, so this
is a reasonable first case to seed `tests/`:

```python
def test_active_arm_keys_normal_mode():
    assert _active_arm_keys(mr_mode=False) == ["b", "r", "n"]

def test_active_arm_keys_medium_resolution_mode():
    assert _active_arm_keys(mr_mode=True) == ["b", "m", "n"]
```

Manual verification (no automated coverage for the bokeh rendering
itself): run the app once with MR mode off and once on
(`./scripts/serve-app.sh`), confirm exactly 3 spectrum panels appear in
Blue → Red/Medium-res → Near-IR order, and that the inactive arm's panel
is absent rather than empty.

## Files touched

- `src/pfs_etc_web/pfs_etc_utils.py` — `ARM_PLOT_SPECS`, `_active_arm_keys()`, `create_simspec_plot()` signature and body
- `src/pfs_etc_web/pfs_etc_specsim.py` — pass `mr_mode` at the `create_simspec_plot()` call site
- `tests/test_pfs_etc_utils.py` (new) — unit tests for `_active_arm_keys()`
