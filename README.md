# EcoLedger Pro: High-Tech Secondary Market Desktop Suite for Sustainable Debt

## Overview

EcoLedger Pro is an institutional desktop application that automates the lifecycle of Green Loans—loans specifically granted for carbon-offsetting projects or energy-efficient upgrades. It creates a transparent trading floor where loan assets can be packaged and sold to institutional investors.

EcoLedger Pro eliminates greenwashing in sustainable finance by providing verifiable proof of environmental performance through automated monitoring and blockchain audit trails, while creating direct financial incentives for borrowers to exceed green targets. The platform transforms green lending from a manual, trust-based process into an automated, data-verified market where banks process loans in minutes instead of weeks and investors purchase portfolios with confidence in ESG authenticity.

## Links

-**Source Code**: https://github.com/SamiraSamrose/ecoledger-pro
-**Video Demo**: https://youtu.be/aLC_tP6awR0
-**Notebook**: https://github.com/SamiraSamrose/ecoledger-pro/blob/main/EcoLedger_Pro_sustainable_debt_platform.ipynb

https://colab.research.google.com/github/SamiraSamrose/ecoledger-pro/blob/main/EcoLedger_Pro_sustainable_debt_platform.ipynb

## Key Features and Usage List

**Features:**
- Multi-model AI credit scoring combining financial and ESG metrics
- Automated OCR document processing with classification and extraction
- Portfolio construction with yield and risk calculation
- Secondary market trading platform with buyer-seller matching
- Blockchain audit ledger with hash validation
- Real-time covenant monitoring with threshold checking
- Dynamic interest rate adjustment based on milestones
- Borrower savings calculation and reporting
- Compliance alert generation for violations
- Dashboard analytics with trend visualization
- Risk prediction and categorization
- External data integration from multiple APIs
- Document integrity verification with cryptographic hashing
- Trade settlement tracking
- Portfolio performance benchmarking

**Usage:**
- Banks originate green loans with AI-powered approval
- Credit analysts evaluate loan applications with ESG scoring
- Document processors verify authenticity of uploaded files
- Portfolio managers package loans for secondary market sale
- Institutional investors purchase verified green debt portfolios
- Compliance officers monitor covenant adherence
- Risk managers assess default probability
- Borrowers receive rate discounts for environmental performance
- Auditors validate transaction integrity through blockchain ledger
- Regulators review green finance compliance
- Treasury departments optimize portfolio yields
- ESG analysts track carbon reduction impact
- Operations teams automate manual verification workflows

## Technology Stack

**Languages:** Python, JavaScript, SQL, HTML, CSS

**Backend Frameworks:** Flask, Flask-CORS, Flask-SQLAlchemy

**Frontend Frameworks:** Electron.js

**Machine Learning Libraries:** scikit-learn, XGBoost, LightGBM, CatBoost, NumPy, pandas, scipy

**Document Processing:** Tesseract OCR, pytesseract, Pillow, pdf2image, OpenCV

**Data Visualization:** Chart.js, Plotly, Matplotlib, Seaborn

**Database:** PostgreSQL, SQLAlchemy ORM

**APIs:** World Bank API, SEC EDGAR API, OpenCorporates API

**Security:** hashlib (SHA-256), JWT tokens

**Development Tools:** pytest, black, flake8

**Production Server:** Gunicorn

**Data Sources:**
World Bank International Debt Statistics, World Bank Emissions Database, World Bank Energy Metrics, SEC Corporate Filings, OpenCorporates Company Registry

**Datasets Integrated:**
- DT.DOD.DECT.CD (External debt stocks)
- DT.INT.DECT.CD (Interest payments)
- NY.GDP.MKTP.CD (GDP data)
- GC.DOD.TOTL.GD.ZS (Government debt to GDP)
- DT.TDS.DECT.EX.ZS (Debt service to exports)
- EN.ATM.CO2E.KT (CO2 emissions)
- EN.ATM.CO2E.PC (CO2 per capita)
- EG.USE.COMM.FO.ZS (Fossil fuel consumption)
- EG.FEC.RNEW.ZS (Renewable energy consumption)
- EN.ATM.GHGT.KT.CE (GHG emissions)
- EG.USE.ELEC.KH.PC (Electricity consumption per capita)
- EG.ELC.RNEW.ZS (Renewable electricity output)

## Functionality

**01. AI-Powered Credit Scoring**
- Analyzes financial health metrics and ESG scores
- Uses Random Forest, XGBoost, LightGBM and Gradient Boosting models
- Calculates combined credit score weighted 60% financial, 40% ESG
- Provides instant approval/rejection decisions

**02. Automated Document Vault**
- Processes documents via Tesseract OCR
- Extracts structured data from property deeds, energy certificates, financial statements
- Classifies document types automatically
- Calculates confidence scores for verification
- Stores documents with SHA-256 hash integrity

**03. Loan Portfolio Trading Platform**
- Creates portfolios by packaging multiple loans
- Calculates portfolio yield, risk and ESG metrics
- Lists portfolios on exchange for institutional buyers
- Executes trades with settlement dates
- Records all transactions to blockchain ledger

**04. Covenant Monitoring System**
- Tracks energy savings, carbon reduction, renewable energy usage
- Compares performance against threshold requirements
- Generates compliance alerts for violations
- Provides time-series performance data
- Supports IoT sensor, utility report and audit data sources

**05. Dynamic Interest Rate Engine**
- Calculates base rates from credit score, loan term and ESG factors
- Determines milestone tier based on carbon reduction achievement
- Applies rate discounts for energy and renewable energy bonuses
- Calculates total borrower savings
- Adjusts rates monthly based on performance

**06. Blockchain Audit Ledger**
- Implements hash-chained block structure with SHA-256
- Records portfolio creation and trade execution
- Provides proof-of-work mining for block validation
- Enables full chain validation for integrity verification
- Maintains immutable transaction history

**07. Analytics Dashboard**
- Displays loan application trends and approval rates
- Shows ESG score distribution across portfolio
- Visualizes portfolio performance and yields
- Tracks carbon reduction impact by project type
- Provides geographical distribution analysis

**08. Risk Prediction**
- Calculates default probability scores
- Segments loans into risk categories
- Uses ensemble regression models
- Provides risk-adjusted pricing recommendations


## Installation

See [SETUP.md](SETUP.md) for detailed installation instructions.

## Quick Start

1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Initialize database
5. Run the application

## Documentation

- [Setup Guide](SETUP.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [User Guide](docs/USER_GUIDE.md)

## License

MIT License - see LICENSE file for details
