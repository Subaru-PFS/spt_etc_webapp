#!/usr/bin/env python3


import panel as pn
from pfs_etc_web.pn_app import pfs_etc_app

pn.extension(
    "floatpanel",
    "mathjax",
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
)


pfs_etc_app()
