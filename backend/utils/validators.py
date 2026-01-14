import re
from datetime import datetime

def validate_loan_amount(amount):
    """Validate loan amount"""
    try:
        amount = float(amount)
        return 1000 <= amount <= 100000000
    except (ValueError, TypeError):
        return False

def validate_credit_score(score):
    """Validate credit score range"""
    try:
        score = int(score)
        return 300 <= score <= 850
    except (ValueError, TypeError):
        return False

def validate_percentage(value):
    """Validate percentage value"""
    try:
        value = float(value)
        return 0 <= value <= 100
    except (ValueError, TypeError):
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_loan_id(loan_id):
    """Validate loan ID format"""
    pattern = r'^GL[A-Z0-9]{8}$'
    return re.match(pattern, loan_id) is not None

def validate_country_code(code):
    """Validate country code format"""
    return len(code) == 3 and code.isalpha()

def validate_file_extension(filename):
    """Validate file extension"""
    allowed = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def validate_date(date_string):
    """Validate date format"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
