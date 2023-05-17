#!/usr/bin/env python3

import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from pfs_etc_web.pn_app import pfs_etc_app

app = FastAPI(
    title="PFS Spectral Simulator",
)

templates = Jinja2Templates(directory="src/pfs_etc_web/templates")


@app.get("/")
async def bkapp_page(request: Request):
    script = server_document("http://127.0.0.1:55006/app")

    return templates.TemplateResponse(
        "base_first.html",
        {
            "request": request,
            "script": script,
        },
    )


server = pn.serve(
    {"/app": pfs_etc_app},
    port=55006,
    allow_websocket_origin=["127.0.0.1:8000"],
    address="127.0.0.1",
    show=False,
    # num_procs=2,
    # threaded=True,
)
