#!/usr/bin/env python3

import argparse
from pydoc import describe

import panel as pn

from ..pn_app import app

# from ..pn_app import pfs_etc_app, pfs_etc_app2


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Run panel server (not Uvicorn/FastAPI)"
    )
    parser.add_argument(
        "--allow-websocket-origin",
        dest="allow_websocket_origin",
        type=str,
        default=None,
        # default="127.0.0.1:55006",
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

    if args.allow_websocket_origin is None:
        ws = None
    else:
        ws = [args.allow_websocket_origin]

    pn.serve(
        app,
        # pfs_etc_app,
        # pfs_etc_app2,
        port=args.port,
        websocket_origin=ws,
        # allow_websocket_origin=ws,
        autoreload=args.autoreload,
        # basic_auth=args.basic_auth,
        # cookie_secret="my_super_safe_cookie_secret",
        threaded=True,
        show=False,
    )


if __name__ == "__main__":
    main()
