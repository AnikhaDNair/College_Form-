from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, PurchaseOrder, ValidationRule
from datetime import datetime, timedelta
import json

# Create tables
Base.metadata.create_all(bind=engine)

def init_sample_data():
    db = SessionLocal()
    
    try:
        # Create sample purchase orders
        sample_pos = [
            PurchaseOrder(
                po_number="PO-2024-001",
                vendor_name="Acme Corporation",
                po_date=datetime.now() - timedelta(days=30),
                expected_delivery=datetime.now() + timedelta(days=10),
                total_amount=1500.00,
                currency="USD",
                line_items=json.dumps([
                    {"description": "Office Supplies", "quantity": 10, "unit_price": 50.00, "total_price": 500.00},
                    {"description": "Software License", "quantity": 1, "unit_price": 1000.00, "total_price": 1000.00}
                ]),
                status="APPROVED"
            ),
            PurchaseOrder(
                po_number="PO-2024-002",
                vendor_name="Tech Solutions Inc",
                po_date=datetime.now() - timedelta(days=15),
                expected_delivery=datetime.now() + timedelta(days=20),
                total_amount=2500.00,
                currency="USD",
                line_items=json.dumps([
                    {"description": "Laptop Computers", "quantity": 5, "unit_price": 500.00, "total_price": 2500.00}
                ]),
                status="PENDING"
            ),
            PurchaseOrder(
                po_number="PO-2024-003",
                vendor_name="Global Services Ltd",
                po_date=datetime.now() - timedelta(days=7),
                expected_delivery=datetime.now() + timedelta(days=14),
                total_amount=750.00,
                currency="USD",
                line_items=json.dumps([
                    {"description": "Consulting Services", "quantity": 10, "unit_price": 75.00, "total_price": 750.00}
                ]),
                status="APPROVED"
            )
        ]
        
        for po in sample_pos:
            db.add(po)
        
        # Create sample validation rules
        sample_rules = [
            ValidationRule(
                name="High Value Invoice Approval",
                description="Invoices over $1000 require special approval",
                rule_type="AMOUNT",
                field_name="total_amount",
                operator="GT",
                threshold_value="1000.00",
                is_active=True
            ),
            ValidationRule(
                name="Recent Invoice Date",
                description="Invoice date should be within last 30 days",
                rule_type="DATE",
                field_name="invoice_date",
                operator="GT",
                threshold_value=(datetime.now() - timedelta(days=30)).isoformat(),
                is_active=True
            ),
            ValidationRule(
                name="Approved Vendor Only",
                description="Only invoices from approved vendors are allowed",
                rule_type="VENDOR",
                field_name="vendor_name",
                operator="CONTAINS",
                threshold_value="Corp",
                is_active=True
            ),
            ValidationRule(
                name="Invoice Number Format",
                description="Invoice numbers should contain INV prefix",
                rule_type="INVOICE_NUMBER",
                field_name="invoice_number",
                operator="CONTAINS",
                threshold_value="INV",
                is_active=True
            )
        ]
        
        for rule in sample_rules:
            db.add(rule)
        
        db.commit()
        print("Sample data initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()