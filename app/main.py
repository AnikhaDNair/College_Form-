from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .extractor import extract_invoice_from_text, extract_invoice_from_json
from .models import ProcessResult
from .validator import validate_invoice

import json


app = FastAPI(title="Back Office AI Agent for Automated Invoice Processing and Validation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_pos_index() -> Dict[str, Any]:
    pos = _load_json(DATA_DIR / "purchase_orders.json")
    return {po["po_number"]: po for po in pos}


def _load_rules() -> Dict[str, Any]:
    return _load_json(DATA_DIR / "validation_rules.json")


@app.get("/", response_class=HTMLResponse)
async def root_page() -> str:
    index_html = (Path(__file__).resolve().parent.parent / "frontend" / "index.html").read_text(encoding="utf-8")
    return index_html


@app.post("/process/text")
async def process_text(text: str = Form(...)) -> JSONResponse:
    try:
        invoice = extract_invoice_from_text(text)
        validation = validate_invoice(invoice, _load_pos_index(), _load_rules())
        return JSONResponse(ProcessResult(invoice=invoice, validation=validation).model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/process/json")
async def process_json(file: UploadFile = File(...)) -> JSONResponse:
    try:
        payload = (await file.read()).decode("utf-8")
        invoice = extract_invoice_from_json(payload)
        validation = validate_invoice(invoice, _load_pos_index(), _load_rules())
        return JSONResponse(ProcessResult(invoice=invoice, validation=validation).model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/sample")
async def sample() -> JSONResponse:
    text = (DATA_DIR / "sample_invoice.txt").read_text(encoding="utf-8")
    invoice = extract_invoice_from_text(text)
    validation = validate_invoice(invoice, _load_pos_index(), _load_rules())
    return JSONResponse(ProcessResult(invoice=invoice, validation=validation).model_dump())

