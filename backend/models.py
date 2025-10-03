from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    vendor_name = Column(String(255))
    invoice_number = Column(String(100), unique=True, index=True)
    invoice_date = Column(DateTime)
    due_date = Column(DateTime)
    total_amount = Column(Float)
    currency = Column(String(3), default="USD")
    line_items = Column(Text)  # JSON string
    raw_data = Column(Text)    # JSON string with all extracted data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    processing_results = relationship("ProcessingResult", back_populates="invoice")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(100), unique=True, index=True)
    vendor_name = Column(String(255))
    po_date = Column(DateTime)
    expected_delivery = Column(DateTime)
    total_amount = Column(Float)
    currency = Column(String(3), default="USD")
    line_items = Column(Text)  # JSON string
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ValidationRule(Base):
    __tablename__ = "validation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50))  # AMOUNT, DATE, VENDOR, etc.
    field_name = Column(String(100))
    operator = Column(String(10))   # EQ, GT, LT, CONTAINS, etc.
    threshold_value = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProcessingResult(Base):
    __tablename__ = "processing_results"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    status = Column(String(50))  # PASSED, FAILED, WARNING, PENDING
    validation_score = Column(Float)  # 0.0 to 1.0
    discrepancies = Column(Text)  # JSON string
    recommendations = Column(Text)  # JSON string
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="processing_results")