#!/usr/bin/env python3

import panel as pn
from pfs_etc_web.pn_app import pfs_etc_app

pn.extension(
    "floatpanel",
    "mathjax",
    notifications=True,
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
    js_files={
        "font-awesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"
    },
    css_files=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        # "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext",
    ],
    layout_compatibility="error",
)
pn.state.notifications.position = "bottom-left"

pfs_etc_app()
