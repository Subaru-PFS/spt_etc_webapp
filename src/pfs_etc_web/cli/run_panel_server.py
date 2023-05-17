#!/usr/bin/env python3

import panel as pn

from ..pn_app import pfs_etc_app


def main():
    pn.serve(
        pfs_etc_app,
        port=55006,
        # num_procs=4,
        # num_threads=4,
        autoreload=True,
        show=False,
    )


if __name__ == "__main__":
    main()
