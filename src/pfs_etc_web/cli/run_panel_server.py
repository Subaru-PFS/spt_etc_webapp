#!/usr/bin/env python3

import argparse
from pydoc import describe

import panel as pn

from ..pn_app import pfs_etc_app


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Run panel server (not Uvicorn/FastAPI)"
    )
    parser.add_argument(
        "--allow-websocket-origin",
        dest="allow_websocket_origin",
        type=str,
        default="127.0.0.1:55006",
        help="`--allow-websocket-origin` sent to `panel.serve` (default: ).",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=55006,
        help="Port number used on the remote server (default: 55006).",
    )
    parser.add_argument(
        "--autoreload",
        action="store_true",
        help="Enable autoreload.",
    )

    args = parser.parse_args()

    return args


def main():
    args = get_arguments()

    pn.serve(
        pfs_etc_app,
        port=args.port,
        allow_websocket_origin=[args.allow_websocket_origin],
        # num_procs=4,
        # num_threads=4,
        autoreload=args.autoreload,
        show=False,
    )


if __name__ == "__main__":
    main()
