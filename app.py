#!/usr/bin/env python3


import panel as pn
from pfs_etc_web.pn_app import pfs_etc_app

pn.extension(
    "floatpanel",
    "mathjax",
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
    css_files=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    js_files={
        "font-awesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"
    },
)


pfs_etc_app()
