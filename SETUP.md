# Setup Guide

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- Node.js 16+ (for frontend build tools)
- Tesseract OCR 4.0+
- Git

## Step 1: Clone Repository

```bash
git clone https://github.com/samirasamrose/ecoledger-pro.git
cd ecoledger-pro
```

## Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Install Tesseract OCR

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### macOS
```bash
brew install tesseract
```

### Windows
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

## Step 5: Configure Environment

Create `.env` file in root directory:

```env
FLASK_APP=backend.app
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/ecoledger
API_PORT=5000
LOG_LEVEL=INFO
TESSERACT_PATH=/usr/bin/tesseract
```

## Step 6: Initialize Database

```bash
python scripts/setup_database.py
```

## Step 7: Train AI Models

```bash
python scripts/train_models.py
```

## Step 8: Run Application

```bash
python backend/app.py
```

Access the application at: http://localhost:5000

## Testing

Run tests:
```bash
pytest tests/
```

## Production Deployment

See docs/ARCHITECTURE.md for production deployment guidelines.
