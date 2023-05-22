import os
from pathlib import Path

import panel as pn
import pfs_etc_web
from pfs_etc_web.pn_app import pfs_etc_app

pn.extension(
    "floatpanel",
    "mathjax",
    loading_spinner="dots",
    loading_color="#6A589D",
    sizing_mode="stretch_width",
    # notifications=True,
)

# PFS_LOGO = Path(os.path.dirname(pfs_etc_web.__file__)) / "assets/logo-pfs.png"
# print(PFS_LOGO)

pfs_etc_app()
