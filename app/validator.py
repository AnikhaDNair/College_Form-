from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import Discrepancy, Invoice, LineItem, ValidationCheck, ValidationResult


def validate_invoice(invoice: Invoice, po_index: Dict[str, Dict[str, Any]], rules: Dict[str, Any]) -> ValidationResult:
    checks: List[ValidationCheck] = []
    discrepancies: List[Discrepancy] = []

    tolerance = float(rules.get("amount_tolerance", 0.01))
    line_tolerance = float(rules.get("line_tolerance", 0.01))
    require_po = bool(rules.get("require_po", True))
    require_vendor_match = bool(rules.get("require_vendor_match", True))

    # PO existence and matching
    po = None
    if invoice.po_number:
        po = po_index.get(invoice.po_number)
        if po is None:
            discrepancies.append(
                Discrepancy(
                    field="po_number",
                    expected="existing PO",
                    actual=invoice.po_number,
                    severity="error",
                    message="PO number not found",
                )
            )
            checks.append(ValidationCheck(check="po_exists", status="fail", details="PO not found"))
        else:
            checks.append(ValidationCheck(check="po_exists", status="pass"))
    else:
        if require_po:
            discrepancies.append(
                Discrepancy(field="po_number", expected="provided", actual=None, severity="error", message="PO is required")
            )
            checks.append(ValidationCheck(check="po_present", status="fail", details="PO is required"))
        else:
            checks.append(ValidationCheck(check="po_present", status="warn", details="PO not provided"))

    # Vendor match
    if po and require_vendor_match:
        expected_vendor = str(po.get("vendor_name", "")).strip().lower()
        actual_vendor = invoice.vendor_name.strip().lower()
        if expected_vendor and expected_vendor != actual_vendor:
            discrepancies.append(
                Discrepancy(
                    field="vendor_name",
                    expected=po.get("vendor_name"),
                    actual=invoice.vendor_name,
                    severity="error",
                    message="Vendor does not match PO",
                )
            )
            checks.append(ValidationCheck(check="vendor_match", status="fail"))
        else:
            checks.append(ValidationCheck(check="vendor_match", status="pass"))

    # Amounts
    # Subtotal check from line items
    if invoice.subtotal_amount is not None:
        computed_subtotal = round(sum(li.line_total for li in invoice.line_items), 2)
        if abs(computed_subtotal - invoice.subtotal_amount) > tolerance:
            discrepancies.append(
                Discrepancy(
                    field="subtotal_amount",
                    expected=computed_subtotal,
                    actual=invoice.subtotal_amount,
                    severity="error",
                    message="Subtotal does not match sum of line items",
                )
            )
            checks.append(ValidationCheck(check="subtotal_matches_lines", status="fail"))
        else:
            checks.append(ValidationCheck(check="subtotal_matches_lines", status="pass"))

    # Total check
    if invoice.total_amount is not None and invoice.subtotal_amount is not None and invoice.tax_amount is not None:
        expected_total = round(invoice.subtotal_amount + invoice.tax_amount, 2)
        if abs(expected_total - invoice.total_amount) > tolerance:
            discrepancies.append(
                Discrepancy(
                    field="total_amount",
                    expected=expected_total,
                    actual=invoice.total_amount,
                    severity="error",
                    message="Total should equal subtotal + tax",
                )
            )
            checks.append(ValidationCheck(check="total_consistency", status="fail"))
        else:
            checks.append(ValidationCheck(check="total_consistency", status="pass"))

    # Compare to PO lines if available
    if po:
        po_lines: List[Dict[str, Any]] = po.get("line_items", [])
        # Index by description (normalized)
        po_by_desc = {str(li.get("description", "")).strip().lower(): li for li in po_lines}
        for inv_line in invoice.line_items:
            key = inv_line.description.strip().lower()
            po_line = po_by_desc.get(key)
            if not po_line:
                discrepancies.append(
                    Discrepancy(
                        field=f"line_items[{inv_line.description}]",
                        expected="present in PO",
                        actual="missing",
                        severity="warning",
                        message="Line not found in PO",
                    )
                )
                continue
            # Quantity
            po_qty = float(po_line.get("quantity", 0))
            if abs(po_qty - inv_line.quantity) > line_tolerance:
                discrepancies.append(
                    Discrepancy(
                        field=f"line_items[{inv_line.description}].quantity",
                        expected=po_qty,
                        actual=inv_line.quantity,
                        severity="error",
                        message="Quantity differs from PO",
                    )
                )
            # Unit price
            po_price = float(po_line.get("unit_price", 0))
            if abs(po_price - inv_line.unit_price) > line_tolerance:
                discrepancies.append(
                    Discrepancy(
                        field=f"line_items[{inv_line.description}].unit_price",
                        expected=po_price,
                        actual=inv_line.unit_price,
                        severity="error",
                        message="Unit price differs from PO",
                    )
                )

    # Determine overall status
    has_error = any(d.severity == "error" for d in discrepancies)
    has_warning = any(d.severity == "warning" for d in discrepancies)
    if has_error:
        status = "invalid"
    elif has_warning:
        status = "review"
    else:
        status = "valid"

    return ValidationResult(status=status, checks=checks, discrepancies=discrepancies)

