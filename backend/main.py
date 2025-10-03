from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
from datetime import datetime
import json

from database import get_db, engine
from models import Base, Invoice, PurchaseOrder, ValidationRule, ProcessingResult
from schemas import (
    InvoiceCreate, InvoiceResponse, PurchaseOrderCreate, PurchaseOrderResponse,
    ValidationRuleCreate, ValidationRuleResponse, ProcessingResultResponse,
    InvoiceProcessingRequest, ValidationStatus
)
from services.invoice_processor import InvoiceProcessor
from services.ai_extractor import AIExtractor
from services.validator import InvoiceValidator

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Back Office AI Agent - Invoice Processing",
    description="Automated invoice processing and validation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
invoice_processor = InvoiceProcessor()
ai_extractor = AIExtractor()
validator = InvoiceValidator()

@app.get("/")
async def root():
    return {"message": "Back Office AI Agent - Invoice Processing API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Invoice endpoints
@app.post("/api/invoices/upload", response_model=ProcessingResultResponse)
async def upload_and_process_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process an invoice using AI extraction and validation"""
    try:
        # Save uploaded file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract data using AI
        extracted_data = await ai_extractor.extract_invoice_data(file_path)
        
        # Create invoice record
        invoice_data = InvoiceCreate(
            filename=file.filename,
            vendor_name=extracted_data.get("vendor_name", ""),
            invoice_number=extracted_data.get("invoice_number", ""),
            invoice_date=extracted_data.get("invoice_date"),
            due_date=extracted_data.get("due_date"),
            total_amount=extracted_data.get("total_amount", 0.0),
            currency=extracted_data.get("currency", "USD"),
            line_items=json.dumps(extracted_data.get("line_items", [])),
            raw_data=json.dumps(extracted_data)
        )
        
        # Save to database
        db_invoice = Invoice(**invoice_data.dict())
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        
        # Validate against purchase orders
        validation_result = await validator.validate_invoice(db_invoice, db)
        
        # Create processing result
        processing_result = ProcessingResult(
            invoice_id=db_invoice.id,
            status=validation_result.status,
            validation_score=validation_result.score,
            discrepancies=json.dumps(validation_result.discrepancies),
            recommendations=json.dumps(validation_result.recommendations)
        )
        
        db.add(processing_result)
        db.commit()
        db.refresh(processing_result)
        
        # Clean up temporary file
        os.remove(file_path)
        
        return ProcessingResultResponse.from_orm(processing_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all invoices with pagination"""
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices

@app.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/api/invoices/{invoice_id}/validation", response_model=ProcessingResultResponse)
async def get_invoice_validation(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get validation results for a specific invoice"""
    result = db.query(ProcessingResult).filter(
        ProcessingResult.invoice_id == invoice_id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Validation result not found")
    return result

# Purchase Order endpoints
@app.post("/api/purchase-orders", response_model=PurchaseOrderResponse)
async def create_purchase_order(
    po_data: PurchaseOrderCreate,
    db: Session = Depends(get_db)
):
    """Create a new purchase order"""
    db_po = PurchaseOrder(**po_data.dict())
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po

@app.get("/api/purchase-orders", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all purchase orders"""
    pos = db.query(PurchaseOrder).offset(skip).limit(limit).all()
    return pos

# Validation Rules endpoints
@app.post("/api/validation-rules", response_model=ValidationRuleResponse)
async def create_validation_rule(
    rule_data: ValidationRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new validation rule"""
    db_rule = ValidationRule(**rule_data.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.get("/api/validation-rules", response_model=List[ValidationRuleResponse])
async def get_validation_rules(
    db: Session = Depends(get_db)
):
    """Get all validation rules"""
    rules = db.query(ValidationRule).all()
    return rules

# Reports endpoints
@app.get("/api/reports/discrepancies")
async def get_discrepancy_report(
    db: Session = Depends(get_db)
):
    """Get a report of all invoices with discrepancies"""
    results = db.query(ProcessingResult).filter(
        ProcessingResult.status.in_(["FAILED", "WARNING"])
    ).all()
    
    discrepancies = []
    for result in results:
        invoice = db.query(Invoice).filter(Invoice.id == result.invoice_id).first()
        if invoice:
            discrepancies.append({
                "invoice_id": result.invoice_id,
                "invoice_number": invoice.invoice_number,
                "vendor_name": invoice.vendor_name,
                "status": result.status,
                "validation_score": result.validation_score,
                "discrepancies": json.loads(result.discrepancies),
                "recommendations": json.loads(result.recommendations)
            })
    
    return {"discrepancies": discrepancies, "count": len(discrepancies)}

@app.get("/api/reports/summary")
async def get_processing_summary(
    db: Session = Depends(get_db)
):
    """Get processing summary statistics"""
    total_invoices = db.query(Invoice).count()
    total_results = db.query(ProcessingResult).count()
    
    status_counts = db.query(
        ProcessingResult.status,
        db.func.count(ProcessingResult.id)
    ).group_by(ProcessingResult.status).all()
    
    return {
        "total_invoices": total_invoices,
        "total_processed": total_results,
        "status_breakdown": dict(status_counts)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)