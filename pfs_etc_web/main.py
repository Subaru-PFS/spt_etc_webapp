#!/usr/bin/env python3

# Third Party Library
import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates
from pn_app import main_app

app = FastAPI()

templates = Jinja2Templates(directory="pfs_etc_web/templates")


@app.get("/")
async def bkapp_page(request: Request):
    script = server_document("http://127.0.0.1:5000/app")
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "script": script,
        },
    )


pn.serve(
    {"/app": main_app},
    port=5000,
    allow_websocket_origin=["127.0.0.1:8000"],
    address="127.0.0.1",
    show=False,
)
