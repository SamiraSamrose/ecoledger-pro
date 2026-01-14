import uuid
from datetime import datetime, timedelta

def generate_loan_id():
    """Generate unique loan ID"""
    return f"GL{str(uuid.uuid4())[:8].upper()}"

def generate_document_id():
    """Generate unique document ID"""
    return f"DOC{str(uuid.uuid4())[:8].upper()}"

def generate_portfolio_id():
    """Generate unique portfolio ID"""
    return f"PORT{str(uuid.uuid4())[:8].upper()}"

def generate_trade_id():
    """Generate unique trade ID"""
    return f"TRADE{str(uuid.uuid4())[:8].upper()}"

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.2f}%"

def calculate_settlement_date(trade_date, days=3):
    """Calculate settlement date"""
    return trade_date + timedelta(days=days)

def parse_loan_term(term_months):
    """Convert months to years and months"""
    years = term_months // 12
    months = term_months % 12
    return years, months

def calculate_monthly_payment(principal, annual_rate, term_months):
    """Calculate monthly loan payment"""
    if annual_rate == 0:
        return principal / term_months
    
    monthly_rate = annual_rate / 12 / 100
    payment = principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
              ((1 + monthly_rate) ** term_months - 1)
    return payment

def paginate_results(query, page=1, per_page=50):
    """Paginate database query results"""
    offset = (page - 1) * per_page
    items = query.limit(per_page).offset(offset).all()
    total = query.count()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
