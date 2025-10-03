from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(..., description="Item description")
    quantity: float = Field(..., description="Ordered quantity")
    unit_price: float = Field(..., description="Unit price")
    line_total: float = Field(..., description="quantity * unit_price (or provided)")


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: str
    vendor_name: str
    po_number: Optional[str] = None
    currency: str = "USD"
    subtotal_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)


class ValidationCheck(BaseModel):
    check: str
    status: str  # pass | fail | warn
    details: Optional[str] = None


class Discrepancy(BaseModel):
    field: str
    expected: Optional[float | str] = None
    actual: Optional[float | str] = None
    severity: str  # error | warning
    message: Optional[str] = None


class ValidationResult(BaseModel):
    status: str  # valid | invalid | review
    checks: List[ValidationCheck]
    discrepancies: List[Discrepancy]


class ProcessResult(BaseModel):
    title: str = "back office ai agent for automated invoice processing and validation"
    problem_statement: str = (
        "Back office teams spend significant time manually processing and validating invoices, "
        "leading to delay and errors."
    )
    invoice: Invoice
    validation: ValidationResult
