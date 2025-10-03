from typing import Dict, Any, Optional
import asyncio
from services.ai_extractor import AIExtractor
from services.validator import InvoiceValidator
from schemas import ExtractedInvoiceData, ValidationResult

class InvoiceProcessor:
    def __init__(self):
        self.ai_extractor = AIExtractor()
        self.validator = InvoiceValidator()
    
    async def process_invoice(self, file_path: str) -> Dict[str, Any]:
        """Complete invoice processing pipeline"""
        try:
            # Step 1: Extract data using AI
            extracted_data = await self.ai_extractor.extract_invoice_data(file_path)
            
            # Step 2: Structure the extracted data
            structured_data = self._structure_extracted_data(extracted_data)
            
            return {
                "success": True,
                "extracted_data": structured_data,
                "raw_data": extracted_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_data": None
            }
    
    def _structure_extracted_data(self, extracted_data: Dict[str, Any]) -> ExtractedInvoiceData:
        """Structure the extracted data into a standardized format"""
        return ExtractedInvoiceData(
            vendor_name=extracted_data.get("vendor_name"),
            invoice_number=extracted_data.get("invoice_number"),
            invoice_date=extracted_data.get("invoice_date"),
            due_date=extracted_data.get("due_date"),
            total_amount=extracted_data.get("total_amount"),
            currency=extracted_data.get("currency", "USD"),
            line_items=extracted_data.get("line_items", []),
            raw_text=extracted_data.get("raw_text")
        )
    
    async def validate_extracted_data(self, extracted_data: ExtractedInvoiceData, db_session) -> ValidationResult:
        """Validate the extracted data"""
        # This would typically involve creating a temporary Invoice object
        # and running validation against it
        return await self.validator.validate_invoice_data(extracted_data, db_session)