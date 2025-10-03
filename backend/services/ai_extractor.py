import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

class AIExtractor:
    def __init__(self):
        # Configure tesseract path if needed (for different OS)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    async def extract_invoice_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from invoice using OCR and AI processing"""
        try:
            # Read and preprocess image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not read image file")
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            raw_text = pytesseract.image_to_string(processed_image, config='--psm 6')
            
            # Parse structured data from text
            extracted_data = self._parse_invoice_text(raw_text)
            
            return extracted_data
            
        except Exception as e:
            print(f"Error extracting invoice data: {e}")
            # Return basic structure even if extraction fails
            return {
                "vendor_name": "Unknown",
                "invoice_number": "Unknown",
                "invoice_date": None,
                "due_date": None,
                "total_amount": 0.0,
                "currency": "USD",
                "line_items": [],
                "raw_text": str(e)
            }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _parse_invoice_text(self, text: str) -> Dict[str, Any]:
        """Parse structured data from raw OCR text"""
        extracted_data = {
            "vendor_name": self._extract_vendor_name(text),
            "invoice_number": self._extract_invoice_number(text),
            "invoice_date": self._extract_date(text, "invoice"),
            "due_date": self._extract_date(text, "due"),
            "total_amount": self._extract_total_amount(text),
            "currency": self._extract_currency(text),
            "line_items": self._extract_line_items(text),
            "raw_text": text
        }
        
        return extracted_data
    
    def _extract_vendor_name(self, text: str) -> Optional[str]:
        """Extract vendor/company name from text"""
        # Look for common patterns
        patterns = [
            r"(?:from|vendor|bill\s*to):\s*([^\n]+)",
            r"^([A-Z][A-Z\s&,.-]+(?:INC|LLC|CORP|COMPANY|LTD))",
            r"bill\s*from[:\s]+([^\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Fallback: look for capitalized company names
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if len(line) > 5 and line.isupper() and any(word in line.lower() for word in ['inc', 'llc', 'corp', 'ltd']):
                return line.strip()
        
        return None
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text"""
        patterns = [
            r"(?:invoice|inv)[\s#:]*([A-Z0-9-]+)",
            r"(?:invoice\s*number|inv\s*no)[\s#:]*([A-Z0-9-]+)",
            r"#\s*([A-Z0-9-]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_date(self, text: str, date_type: str = "invoice") -> Optional[datetime]:
        """Extract date from text"""
        patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}-\d{1,2}-\d{1,2})",
            r"(\w+\s+\d{1,2},?\s+\d{4})",
        ]
        
        # Look for date labels
        if date_type == "invoice":
            label_patterns = [r"invoice\s*date[:\s]*", r"date[:\s]*"]
        else:
            label_patterns = [r"due\s*date[:\s]*", r"payment\s*due[:\s]*"]
        
        for label_pattern in label_patterns:
            for pattern in patterns:
                full_pattern = label_pattern + pattern
                match = re.search(full_pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    try:
                        # Try different date formats
                        for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%B %d, %Y"]:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                    except:
                        continue
        
        return None
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text"""
        patterns = [
            r"total[:\s]*\$?([\d,]+\.?\d*)",
            r"amount\s*due[:\s]*\$?([\d,]+\.?\d*)",
            r"grand\s*total[:\s]*\$?([\d,]+\.?\d*)",
            r"balance\s*due[:\s]*\$?([\d,]+\.?\d*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        # Look for currency amounts at the end of lines
        currency_pattern = r"\$([\d,]+\.?\d*)"
        matches = re.findall(currency_pattern, text)
        if matches:
            # Return the largest amount (likely the total)
            amounts = [float(m.replace(',', '')) for m in matches]
            return max(amounts)
        
        return None
    
    def _extract_currency(self, text: str) -> str:
        """Extract currency from text"""
        if '$' in text:
            return 'USD'
        elif '€' in text:
            return 'EUR'
        elif '£' in text:
            return 'GBP'
        elif '¥' in text:
            return 'JPY'
        else:
            return 'USD'  # Default
    
    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from text"""
        line_items = []
        
        # Look for table-like structures
        lines = text.split('\n')
        in_items_section = False
        
        for line in lines:
            # Check if we're in a line items section
            if any(keyword in line.lower() for keyword in ['description', 'item', 'product', 'service']):
                in_items_section = True
                continue
            
            if in_items_section:
                # Look for lines with quantity, price patterns
                # This is a simplified extraction - in practice, you'd need more sophisticated parsing
                if re.search(r'\d+\.?\d*\s+\d+\.?\d*', line) and '$' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            quantity = float(parts[0])
                            unit_price = float(parts[1].replace('$', ''))
                            total_price = quantity * unit_price
                            
                            line_items.append({
                                "description": ' '.join(parts[2:]) if len(parts) > 2 else "Item",
                                "quantity": quantity,
                                "unit_price": unit_price,
                                "total_price": total_price
                            })
                        except (ValueError, IndexError):
                            continue
        
        return line_items