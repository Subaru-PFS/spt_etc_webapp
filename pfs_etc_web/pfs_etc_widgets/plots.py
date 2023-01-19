#!/usr/bin/env python3

# Third Party Library
import panel as pn


class MatplotlibWidgets:
    def __init__(self, fig, dpi=144, visible=True):
        self.pane = pn.pane.Matplotlib(fig, dpi=dpi, visible=visible)
        pass


class BokehWidgets:
    def __init__(self, p, visible=True):
        self.plot = pn.pane.Bokeh(p, visible=visible)
        self.pane = pn.Column(self.plot, sizing_mode="stretch_width")
