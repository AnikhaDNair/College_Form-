from __future__ import annotations

import json
import re
from typing import List

from .models import Invoice, LineItem


_MONEY = r"(?:\$)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+(?:\.[0-9]{2})?)"


def _parse_money(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace(",", "").replace("$", "").strip()
    try:
        return float(cleaned)
    except Exception:
        return None


def extract_invoice_from_text(text: str) -> Invoice:
    # Basic regex-based extraction from semi-structured text
    invoice_number = _first_group(r"(?i)invoice\s*(?:no\.?|number)\s*[:#-]?\s*(\S+)", text)
    invoice_date = _first_group(r"(?i)date\s*[:#-]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})", text) or ""
    vendor_name = _first_group(r"(?i)vendor\s*[:#-]?\s*([\w\s&.,'-]{2,})", text) or _first_group(r"(?i)from\s*[:#-]?\s*([\w\s&.,'-]{2,})", text) or "Unknown Vendor"
    po_number = _first_group(r"(?i)po\s*(?:no\.?|number)?\s*[:#-]?\s*(\S+)", text)

    subtotal_amount = _first_money(rf"(?i)subtotal\s*[:#-]?\s*{_MONEY}", text)
    tax_amount = _first_money(rf"(?i)(?:tax|vat)\s*[:#-]?\s*{_MONEY}", text)
    total_amount = _first_money(rf"(?i)total\s*[:#-]?\s*{_MONEY}", text)

    # Line items: support formats like "Item: Desc x QTY @ PRICE = TOTAL" or CSV-like lines
    line_items: List[LineItem] = []
    for line in text.splitlines():
        # Pattern 1: Desc x qty @ price = total
        m = re.search(rf"(?i)([\w\s/().,'-]+?)\s+x\s*([0-9]+(?:\.[0-9]+)?)\s*@\s*{_MONEY}\s*=\s*{_MONEY}", line)
        if m:
            desc = m.group(1).strip()
            qty = float(m.group(2))
            unit = _parse_money(m.group(3)) or 0.0
            total = _parse_money(m.group(4)) or round(qty * unit, 2)
            line_items.append(LineItem(description=desc, quantity=qty, unit_price=unit, line_total=total))
            continue
        # Pattern 2: CSV-like: desc, qty, unit, total
        m2 = re.search(rf"^\s*([^,]+),\s*([0-9]+(?:\.[0-9]+)?),\s*{_MONEY},\s*{_MONEY}\s*$", line)
        if m2:
            desc = m2.group(1).strip()
            qty = float(m2.group(2))
            unit = _parse_money(m2.group(3)) or 0.0
            total = _parse_money(m2.group(4)) or round(qty * unit, 2)
            line_items.append(LineItem(description=desc, quantity=qty, unit_price=unit, line_total=total))

    # Compute subtotal if missing
    if subtotal_amount is None and line_items:
        subtotal_amount = round(sum(li.line_total for li in line_items), 2)
    if total_amount is None and subtotal_amount is not None and tax_amount is not None:
        total_amount = round(subtotal_amount + tax_amount, 2)

    return Invoice(
        invoice_number=invoice_number or "UNKNOWN",
        invoice_date=invoice_date or "",
        vendor_name=vendor_name,
        po_number=po_number,
        currency="USD",
        subtotal_amount=subtotal_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        line_items=line_items,
    )


def extract_invoice_from_json(json_str: str) -> Invoice:
    data = json.loads(json_str)
    # Allow direct match to model
    line_items = [
        LineItem(
            description=li.get("description", ""),
            quantity=float(li.get("quantity", 0)),
            unit_price=float(li.get("unit_price", 0)),
            line_total=float(li.get("line_total", li.get("quantity", 0) * li.get("unit_price", 0))),
        )
        for li in data.get("line_items", [])
    ]
    return Invoice(
        invoice_number=str(data.get("invoice_number", "UNKNOWN")),
        invoice_date=str(data.get("invoice_date", "")),
        vendor_name=str(data.get("vendor_name", "Unknown Vendor")),
        po_number=data.get("po_number"),
        currency=str(data.get("currency", "USD")),
        subtotal_amount=float(data["subtotal_amount"]) if data.get("subtotal_amount") is not None else None,
        tax_amount=float(data["tax_amount"]) if data.get("tax_amount") is not None else None,
        total_amount=float(data["total_amount"]) if data.get("total_amount") is not None else None,
        line_items=line_items,
    )


def _first_group(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _first_money(pattern: str, text: str) -> float | None:
    m = re.search(pattern, text)
    if not m:
        return None
    return _parse_money(m.group(1))

