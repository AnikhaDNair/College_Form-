# Back Office AI Agent - Invoice Processing and Validation

A comprehensive full-stack application for automated invoice processing and validation using AI-powered data extraction and intelligent validation rules.

## 🎯 Problem Statement

Back office teams spend significant time manually processing and validating invoices, leading to delays and errors. This system automates the entire process using AI to extract key information from invoice documents and validate it against purchase orders and business rules.

## ✨ Features

### Core Functionality
- **AI-Powered Data Extraction**: Automatically extracts key information from invoice documents using OCR and machine learning
- **Purchase Order Validation**: Validates extracted invoice data against existing purchase orders
- **Intelligent Validation Rules**: Configurable rules engine for automated validation
- **Discrepancy Detection**: Flags discrepancies for manual review with detailed explanations
- **Comprehensive Reporting**: JSON-formatted structured data with validation status and discrepancy reports

### Technical Features
- **Modern Full-Stack Architecture**: FastAPI backend with React frontend
- **Real-time Processing**: Instant invoice upload and processing
- **Responsive UI**: Modern Material-UI interface optimized for all devices
- **RESTful API**: Well-documented API endpoints for all operations
- **Docker Support**: Easy deployment with Docker containers
- **SQLite Database**: Lightweight database with sample data included

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   SQLite DB     │
│                 │    │                 │    │                 │
│  - Dashboard    │◄──►│  - AI Extractor │◄──►│  - Invoices     │
│  - Upload       │    │  - Validator    │    │  - Purchase O's │
│  - Invoice List │    │  - API Endpoints│    │  - Validation   │
│  - Reports      │    │  - File Upload  │    │  - Results      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### 1. Clone and Setup
```bash
git clone <repository-url>
cd back-office-ai-agent
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python3 init_sample_data.py  # Initialize sample data
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🐳 Docker Deployment

### Using Docker Compose
```bash
docker-compose up --build
```

This will start:
- Backend API on port 8000
- Frontend on port 3000
- PostgreSQL database on port 5432

### Individual Services
```bash
# Backend only
cd backend
docker build -t invoice-backend .
docker run -p 8000:8000 invoice-backend

# Frontend only
cd frontend
docker build -t invoice-frontend .
docker run -p 3000:3000 invoice-frontend
```

## 📊 Sample Data

The application comes with pre-loaded sample data:

### Purchase Orders
- **PO-2024-001**: Acme Corporation ($1,500)
- **PO-2024-002**: Tech Solutions Inc ($2,500)
- **PO-2024-003**: Global Services Ltd ($750)

### Validation Rules
- High Value Invoice Approval (>$1000)
- Recent Invoice Date (within 30 days)
- Approved Vendor Only (contains "Corp")
- Invoice Number Format (contains "INV")

## 🔧 API Endpoints

### Invoice Management
- `POST /api/invoices/upload` - Upload and process invoice
- `GET /api/invoices` - Get all invoices
- `GET /api/invoices/{id}` - Get specific invoice
- `GET /api/invoices/{id}/validation` - Get validation results

### Purchase Orders
- `POST /api/purchase-orders` - Create purchase order
- `GET /api/purchase-orders` - Get all purchase orders

### Validation Rules
- `POST /api/validation-rules` - Create validation rule
- `GET /api/validation-rules` - Get all validation rules

### Reports
- `GET /api/reports/discrepancies` - Get discrepancy report
- `GET /api/reports/summary` - Get processing summary

## 📁 Project Structure

```
back-office-ai-agent/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── requirements.txt        # Python dependencies
│   ├── init_sample_data.py     # Sample data initialization
│   └── services/
│       ├── ai_extractor.py     # AI/OCR data extraction
│       ├── validator.py        # Validation logic
│       └── invoice_processor.py # Main processing pipeline
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React application
│   │   ├── components/         # React components
│   │   │   ├── Dashboard.js    # Dashboard overview
│   │   │   ├── InvoiceUpload.js # File upload interface
│   │   │   ├── InvoiceList.js  # Invoice listing
│   │   │   ├── Reports.js      # Discrepancy reports
│   │   │   └── Navigation.js   # Bottom navigation
│   │   └── services/
│   │       └── api.js          # API client
│   ├── package.json            # Node.js dependencies
│   └── Dockerfile              # Frontend Docker config
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

## 🔍 How It Works

### 1. Invoice Upload
Users upload invoice files (PDF, images) through the web interface.

### 2. AI Data Extraction
The system uses OCR (Tesseract) and intelligent parsing to extract:
- Vendor name
- Invoice number
- Invoice date and due date
- Total amount and currency
- Line items with quantities and prices

### 3. Validation Process
Extracted data is validated against:
- **Purchase Orders**: Amount matching, date validation, vendor verification
- **Business Rules**: Configurable validation rules for amounts, dates, vendors, etc.

### 4. Results & Reporting
- **Validation Score**: 0-100% based on discrepancies found
- **Status**: PASSED, WARNING, or FAILED
- **Discrepancies**: Detailed list of issues found
- **Recommendations**: Suggested actions for resolution

## 🎨 User Interface

### Dashboard
- Overview of processing statistics
- Status breakdown (passed, failed, warnings)
- Quick access to key metrics

### Upload Interface
- Drag & drop file upload
- Real-time processing feedback
- Immediate validation results
- Processing feature highlights

### Invoice List
- Tabular view of all processed invoices
- Sortable columns and filtering
- Quick access to individual invoice details

### Reports
- Comprehensive discrepancy reports
- Expandable details for each issue
- Recommendations for resolution
- Export capabilities

## 🔧 Configuration

### Environment Variables
```bash
# Backend
DATABASE_URL=sqlite:///./invoice_processing.db
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Validation Rules Configuration
Validation rules can be configured through the API or directly in the database:

```json
{
  "name": "High Value Invoice",
  "rule_type": "AMOUNT",
  "operator": "GT",
  "threshold_value": "1000.00",
  "is_active": true
}
```

## 🚀 Production Deployment

### Recommended Setup
1. **Database**: Use PostgreSQL for production
2. **File Storage**: Implement cloud storage (AWS S3, Google Cloud)
3. **AI Services**: Consider cloud OCR services for better accuracy
4. **Monitoring**: Add logging and monitoring (ELK stack)
5. **Security**: Implement authentication and authorization

### Environment Variables for Production
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
STORAGE_BUCKET=your-s3-bucket
OCR_SERVICE_API_KEY=your-ocr-api-key
JWT_SECRET_KEY=your-jwt-secret
```

## 📈 Performance Considerations

- **File Size Limits**: Configure appropriate limits for uploads
- **Processing Timeout**: Set reasonable timeouts for OCR processing
- **Database Indexing**: Ensure proper indexes on frequently queried fields
- **Caching**: Implement Redis for frequently accessed data
- **Load Balancing**: Use multiple backend instances for high availability

## 🔒 Security Features

- **File Validation**: Strict file type and size validation
- **Input Sanitization**: All user inputs are sanitized
- **CORS Configuration**: Properly configured CORS policies
- **Error Handling**: Secure error messages without sensitive data exposure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the sample data and validation rules

## 🔮 Future Enhancements

- **Machine Learning**: Train custom models for better extraction accuracy
- **Workflow Automation**: Implement approval workflows
- **Integration**: Connect with accounting systems (QuickBooks, Xero)
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Business intelligence and insights
- **Multi-language Support**: Support for multiple languages
- **Batch Processing**: Process multiple invoices simultaneously

---

**Built with ❤️ using FastAPI, React, and AI/ML technologies**