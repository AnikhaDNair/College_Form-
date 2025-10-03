import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import Invoice, PurchaseOrder, ValidationRule
from schemas import ValidationResult, ValidationStatus

class InvoiceValidator:
    def __init__(self):
        pass
    
    async def validate_invoice(self, invoice: Invoice, db: Session) -> ValidationResult:
        """Validate an invoice against purchase orders and validation rules"""
        discrepancies = []
        recommendations = []
        
        # Validate against purchase orders
        po_discrepancies = await self._validate_against_purchase_orders(invoice, db)
        discrepancies.extend(po_discrepancies)
        
        # Apply validation rules
        rule_discrepancies = await self._apply_validation_rules(invoice, db)
        discrepancies.extend(rule_discrepancies)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(discrepancies)
        
        # Calculate validation score
        score = self._calculate_validation_score(discrepancies)
        
        # Determine overall status
        status = self._determine_status(discrepancies, score)
        
        return ValidationResult(
            status=status,
            score=score,
            discrepancies=discrepancies,
            recommendations=recommendations
        )
    
    async def _validate_against_purchase_orders(self, invoice: Invoice, db: Session) -> List[Dict[str, Any]]:
        """Validate invoice against matching purchase orders"""
        discrepancies = []
        
        # Find matching purchase orders by vendor name
        matching_pos = db.query(PurchaseOrder).filter(
            PurchaseOrder.vendor_name.ilike(f"%{invoice.vendor_name}%")
        ).all()
        
        if not matching_pos:
            discrepancies.append({
                "type": "MISSING_PO",
                "severity": "HIGH",
                "message": f"No matching purchase order found for vendor: {invoice.vendor_name}",
                "field": "vendor_name",
                "expected": "Matching PO",
                "actual": invoice.vendor_name
            })
            return discrepancies
        
        # Validate against the most recent matching PO
        latest_po = max(matching_pos, key=lambda po: po.po_date or datetime.min)
        
        # Compare amounts
        if invoice.total_amount and latest_po.total_amount:
            amount_diff = abs(invoice.total_amount - latest_po.total_amount)
            if amount_diff > 0.01:  # Allow for small rounding differences
                discrepancies.append({
                    "type": "AMOUNT_MISMATCH",
                    "severity": "HIGH",
                    "message": f"Invoice amount doesn't match PO amount",
                    "field": "total_amount",
                    "expected": latest_po.total_amount,
                    "actual": invoice.total_amount,
                    "difference": amount_diff
                })
        
        # Compare dates
        if invoice.invoice_date and latest_po.po_date:
            days_diff = (invoice.invoice_date - latest_po.po_date).days
            if days_diff < 0:
                discrepancies.append({
                    "type": "DATE_ISSUE",
                    "severity": "MEDIUM",
                    "message": f"Invoice date is before PO date",
                    "field": "invoice_date",
                    "expected": f"After {latest_po.po_date}",
                    "actual": invoice.invoice_date,
                    "days_difference": days_diff
                })
        
        # Validate line items if available
        if invoice.line_items and latest_po.line_items:
            invoice_items = json.loads(invoice.line_items)
            po_items = json.loads(latest_po.line_items)
            
            if len(invoice_items) != len(po_items):
                discrepancies.append({
                    "type": "LINE_ITEM_COUNT",
                    "severity": "MEDIUM",
                    "message": f"Different number of line items between invoice and PO",
                    "field": "line_items",
                    "expected": len(po_items),
                    "actual": len(invoice_items)
                })
        
        return discrepancies
    
    async def _apply_validation_rules(self, invoice: Invoice, db: Session) -> List[Dict[str, Any]]:
        """Apply validation rules to the invoice"""
        discrepancies = []
        
        # Get active validation rules
        rules = db.query(ValidationRule).filter(ValidationRule.is_active == True).all()
        
        for rule in rules:
            discrepancy = await self._apply_single_rule(invoice, rule)
            if discrepancy:
                discrepancies.append(discrepancy)
        
        return discrepancies
    
    async def _apply_single_rule(self, invoice: Invoice, rule: ValidationRule) -> Optional[Dict[str, Any]]:
        """Apply a single validation rule to the invoice"""
        try:
            if rule.rule_type == "AMOUNT":
                return self._validate_amount_rule(invoice, rule)
            elif rule.rule_type == "DATE":
                return self._validate_date_rule(invoice, rule)
            elif rule.rule_type == "VENDOR":
                return self._validate_vendor_rule(invoice, rule)
            elif rule.rule_type == "INVOICE_NUMBER":
                return self._validate_invoice_number_rule(invoice, rule)
            else:
                return None
        except Exception as e:
            return {
                "type": "RULE_ERROR",
                "severity": "LOW",
                "message": f"Error applying rule {rule.name}: {str(e)}",
                "rule_id": rule.id
            }
    
    def _validate_amount_rule(self, invoice: Invoice, rule: ValidationRule) -> Optional[Dict[str, Any]]:
        """Validate amount-based rules"""
        if not invoice.total_amount or not rule.threshold_value:
            return None
        
        threshold = float(rule.threshold_value)
        actual = invoice.total_amount
        
        if rule.operator == "GT" and actual <= threshold:
            return {
                "type": "AMOUNT_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Amount {actual} is not greater than {threshold}",
                "field": "total_amount",
                "rule_name": rule.name,
                "expected": f"> {threshold}",
                "actual": actual
            }
        elif rule.operator == "LT" and actual >= threshold:
            return {
                "type": "AMOUNT_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Amount {actual} is not less than {threshold}",
                "field": "total_amount",
                "rule_name": rule.name,
                "expected": f"< {threshold}",
                "actual": actual
            }
        elif rule.operator == "EQ" and abs(actual - threshold) > 0.01:
            return {
                "type": "AMOUNT_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Amount {actual} does not equal {threshold}",
                "field": "total_amount",
                "rule_name": rule.name,
                "expected": threshold,
                "actual": actual
            }
        
        return None
    
    def _validate_date_rule(self, invoice: Invoice, rule: ValidationRule) -> Optional[Dict[str, Any]]:
        """Validate date-based rules"""
        if not invoice.invoice_date or not rule.threshold_value:
            return None
        
        # Parse threshold date
        try:
            threshold_date = datetime.fromisoformat(rule.threshold_value)
        except:
            return None
        
        actual_date = invoice.invoice_date
        
        if rule.operator == "GT" and actual_date <= threshold_date:
            return {
                "type": "DATE_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Date {actual_date} is not after {threshold_date}",
                "field": "invoice_date",
                "rule_name": rule.name,
                "expected": f"> {threshold_date}",
                "actual": actual_date
            }
        elif rule.operator == "LT" and actual_date >= threshold_date:
            return {
                "type": "DATE_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Date {actual_date} is not before {threshold_date}",
                "field": "invoice_date",
                "rule_name": rule.name,
                "expected": f"< {threshold_date}",
                "actual": actual_date
            }
        
        return None
    
    def _validate_vendor_rule(self, invoice: Invoice, rule: ValidationRule) -> Optional[Dict[str, Any]]:
        """Validate vendor-based rules"""
        if not invoice.vendor_name or not rule.threshold_value:
            return None
        
        actual = invoice.vendor_name.lower()
        expected = rule.threshold_value.lower()
        
        if rule.operator == "CONTAINS" and expected not in actual:
            return {
                "type": "VENDOR_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Vendor name '{actual}' does not contain '{expected}'",
                "field": "vendor_name",
                "rule_name": rule.name,
                "expected": f"contains '{expected}'",
                "actual": actual
            }
        elif rule.operator == "EQ" and actual != expected:
            return {
                "type": "VENDOR_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Vendor name '{actual}' does not match '{expected}'",
                "field": "vendor_name",
                "rule_name": rule.name,
                "expected": expected,
                "actual": actual
            }
        
        return None
    
    def _validate_invoice_number_rule(self, invoice: Invoice, rule: ValidationRule) -> Optional[Dict[str, Any]]:
        """Validate invoice number-based rules"""
        if not invoice.invoice_number or not rule.threshold_value:
            return None
        
        actual = invoice.invoice_number
        expected = rule.threshold_value
        
        if rule.operator == "CONTAINS" and expected not in actual:
            return {
                "type": "INVOICE_NUMBER_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Invoice number '{actual}' does not contain '{expected}'",
                "field": "invoice_number",
                "rule_name": rule.name,
                "expected": f"contains '{expected}'",
                "actual": actual
            }
        elif rule.operator == "EQ" and actual != expected:
            return {
                "type": "INVOICE_NUMBER_RULE_VIOLATION",
                "severity": "MEDIUM",
                "message": f"Invoice number '{actual}' does not match '{expected}'",
                "field": "invoice_number",
                "rule_name": rule.name,
                "expected": expected,
                "actual": actual
            }
        
        return None
    
    def _generate_recommendations(self, discrepancies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on discrepancies"""
        recommendations = []
        
        for discrepancy in discrepancies:
            if discrepancy["type"] == "MISSING_PO":
                recommendations.append("Create a purchase order for this vendor before processing the invoice")
            elif discrepancy["type"] == "AMOUNT_MISMATCH":
                recommendations.append("Verify the invoice amount with the vendor and update the PO if necessary")
            elif discrepancy["type"] == "DATE_ISSUE":
                recommendations.append("Confirm the invoice date with the vendor")
            elif discrepancy["severity"] == "HIGH":
                recommendations.append("Manual review required before approval")
            elif discrepancy["severity"] == "MEDIUM":
                recommendations.append("Verify this information with the vendor")
        
        # Remove duplicates
        return list(set(recommendations))
    
    def _calculate_validation_score(self, discrepancies: List[Dict[str, Any]]) -> float:
        """Calculate validation score based on discrepancies"""
        if not discrepancies:
            return 1.0
        
        # Weight discrepancies by severity
        severity_weights = {"HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2}
        total_weight = 0
        penalty = 0
        
        for discrepancy in discrepancies:
            weight = severity_weights.get(discrepancy.get("severity", "LOW"), 0.2)
            total_weight += weight
            penalty += weight
        
        if total_weight == 0:
            return 1.0
        
        # Calculate score (1.0 - penalty ratio)
        score = max(0.0, 1.0 - (penalty / total_weight))
        return round(score, 2)
    
    def _determine_status(self, discrepancies: List[Dict[str, Any]], score: float) -> ValidationStatus:
        """Determine overall validation status"""
        if score >= 0.9:
            return ValidationStatus.PASSED
        elif score >= 0.7:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.FAILED