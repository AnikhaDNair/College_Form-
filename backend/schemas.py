from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    PENDING = "PENDING"

# Invoice schemas
class InvoiceBase(BaseModel):
    filename: str
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    line_items: Optional[str] = None
    raw_data: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Purchase Order schemas
class PurchaseOrderBase(BaseModel):
    po_number: str
    vendor_name: Optional[str] = None
    po_date: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    line_items: Optional[str] = None
    status: str = "PENDING"

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Validation Rule schemas
class ValidationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: Optional[str] = None
    field_name: Optional[str] = None
    operator: Optional[str] = None
    threshold_value: Optional[str] = None
    is_active: bool = True

class ValidationRuleCreate(ValidationRuleBase):
    pass

class ValidationRuleResponse(ValidationRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Processing Result schemas
class ProcessingResultBase(BaseModel):
    invoice_id: int
    status: Optional[str] = None
    validation_score: Optional[float] = None
    discrepancies: Optional[str] = None
    recommendations: Optional[str] = None

class ProcessingResultResponse(ProcessingResultBase):
    id: int
    processed_at: datetime
    
    class Config:
        from_attributes = True

# Request schemas
class InvoiceProcessingRequest(BaseModel):
    invoice_id: int
    validate_against_pos: bool = True
    apply_validation_rules: bool = True

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float

class ExtractedInvoiceData(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    line_items: List[LineItem] = []
    raw_text: Optional[str] = None

class ValidationResult(BaseModel):
    status: ValidationStatus
    score: float
    discrepancies: List[Dict[str, Any]]
    recommendations: List[str]