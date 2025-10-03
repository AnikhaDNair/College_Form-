# Back Office AI Agent for Automated Invoice Processing and Validation

Problem: Back office teams spend significant time manually processing and validating invoices, leading to delay and errors.

## What this provides
- Extract key information from invoice documents (text or JSON)
- Validate extracted data against purchase orders and rules
- Flag discrepancies for manual review
- Produce structured JSON: invoice data, validation status, discrepancy list

## Project layout
```
app/
  main.py            # FastAPI app and endpoints
  extractor.py       # Regex-based extractor for text/JSON
  validator.py       # Validation against POs and rules
  models.py          # Pydantic models
frontend/
  index.html         # Simple UI to upload/process and view results
data/
  sample_invoice.txt
  purchase_orders.json
  validation_rules.json
requirements.txt
```

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the UI: http://localhost:8000/

## API
- POST `/process/text` (form field `text`)
- POST `/process/json` (multipart file upload `file` with JSON)
- GET `/sample` (processes bundled sample)

### Example curl
```bash
curl -s -X POST http://localhost:8000/process/text \
  -F 'text=INVOICE NUMBER: INV-42\nDATE: 2025-10-01\nVENDOR: Acme Supplies LLC\nPO NUMBER: PO-9001\nWidget x 2 @ $5.00 = $10.00\nSubtotal: $10.00\nTax: $0.80\nTotal: $10.80' | jq
```

### JSON schema (simplified)
- invoice: `invoice_number`, `invoice_date`, `vendor_name`, `po_number`, `currency`, `line_items[]`, amounts
- validation: `status` (valid|review|invalid), `checks[]`, `discrepancies[]`

## Notes
- The extractor is lightweight (regex-based). Swap with an OCR/LLM service if needed.
- Validation tolerances and requirements are controlled via `data/validation_rules.json`.