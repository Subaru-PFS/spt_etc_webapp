#!/usr/bin/env python3

# Third Party Library
import numpy as np
from bokeh.layouts import column
from bokeh.palettes import Colorblind
from bokeh.plotting import figure


def create_dummy_plot(aspect_ratio=1.5, outline_line_alpha=0.0):

    p = None
    p = figure(
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
        outline_line_alpha=outline_line_alpha,
    )
    p.toolbar.logo = None
    p.toolbar_location = None
    p.line([], [])

    return column(p)


def create_simspec_plot(df, aspect_ratio=2.5):

    df_b = df.loc[df["arm"] == 0, :]
    df_r = df.loc[df["arm"] == 1, :]
    df_n = df.loc[df["arm"] == 2, :]
    df_m = df.loc[df["arm"] == 3, :]

    p_simspec_b = figure(
        title="Blue arm",
        x_range=[380, 650],
        # y_range=[0, 20000],
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
    )
    p_simspec_r = figure(
        title="Red arm",
        x_range=[630, 970],
        # y_range=[0, 20000],
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
    )
    p_simspec_n = figure(
        title="Near-IR arm",
        x_range=[940, 1260],
        # y_range=[0, 20000],
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
    )
    p_simspec_m = figure(
        title="Medium resolution arm",
        x_range=[300, 1400],
        # y_range=[0, 20000],
        aspect_ratio=aspect_ratio,
        sizing_mode="scale_width",
    )

    p_simspec_b.line("wavelength", "flux", source=df_b, color=Colorblind[7][0])
    p_simspec_b.line("wavelength", "error", source=df_b, color="gray")

    p_simspec_r.line("wavelength", "flux", source=df_r, color=Colorblind[7][3])
    p_simspec_r.line("wavelength", "error", source=df_r, color="gray")

    p_simspec_n.line("wavelength", "flux", source=df_n, color=Colorblind[7][1])
    p_simspec_n.line("wavelength", "error", source=df_n, color="gray")

    p_simspec_m.line("wavelength", "flux", source=df_m, color=Colorblind[7][6])
    p_simspec_m.line("wavelength", "error", source=df_m, color="gray")

    return column(p_simspec_b, p_simspec_r, p_simspec_n, p_simspec_m)
