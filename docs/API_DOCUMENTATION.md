# API Documentation

## Base URL
`http://localhost:5000/api`

## Authentication
Include JWT token in Authorization header: `Bearer <token>`

## Endpoints

### Loan Origination
- POST `/loans/apply` - Submit loan application
- GET `/loans/<loan_id>` - Retrieve loan details
- GET `/loans` - List loans with filters

### Document Processing
- POST `/documents/upload` - Upload document for OCR
- GET `/documents/<document_id>` - Get document details
- GET `/documents` - List documents by loan

### Portfolio Trading
- POST `/portfolios/create` - Create portfolio
- GET `/portfolios/<portfolio_id>` - Get portfolio details
- GET `/portfolios` - List portfolios
- POST `/trades/execute` - Execute trade
- GET `/trades` - List trades

### Covenant Monitoring
- POST `/monitoring/generate/<loan_id>` - Generate monitoring data
- GET `/monitoring/status/<loan_id>` - Get current status
- GET `/monitoring/history/<loan_id>` - Get history
- GET `/monitoring/alerts` - Get compliance alerts

### Rate Engine
- POST `/rates/calculate/<loan_id>` - Calculate rate adjustment
- GET `/rates/history/<loan_id>` - Get rate history
- GET `/rates/savings/<loan_id>` - Get borrower savings

### Ledger
- GET `/ledger/validate` - Validate blockchain
- GET `/ledger/query` - Query transactions

### Analytics
- GET `/analytics/dashboard` - Get dashboard metrics
