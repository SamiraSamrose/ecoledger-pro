from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()

class LoanApplication(db.Model):
    __tablename__ = 'loan_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String(50), unique=True, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10))
    year = db.Column(db.Integer)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term_months = db.Column(db.Integer, nullable=False)
    project_type = db.Column(db.String(100), nullable=False)
    
    # Financial Metrics
    debt_to_income_ratio = db.Column(db.Float)
    credit_score = db.Column(db.Integer)
    annual_revenue = db.Column(db.Float)
    years_in_business = db.Column(db.Integer)
    existing_debt = db.Column(db.Float)
    
    # ESG Metrics
    carbon_reduction_target_pct = db.Column(db.Float)
    renewable_energy_pct = db.Column(db.Float)
    energy_efficiency_rating = db.Column(db.String(10))
    environmental_certifications = db.Column(db.Integer)
    social_impact_score = db.Column(db.Float)
    governance_score = db.Column(db.Float)
    
    # Calculated Scores
    financial_health_score = db.Column(db.Float)
    esg_composite_score = db.Column(db.Float)
    combined_credit_score = db.Column(db.Float)
    loan_approved = db.Column(db.Boolean, default=False)
    
    # Metadata
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_loan_id', 'loan_id'),
        Index('idx_country', 'country'),
        Index('idx_status', 'processing_status'),
    )

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(50), unique=True, nullable=False)
    loan_id = db.Column(db.String(50), db.ForeignKey('loan_applications.loan_id'))
    document_type = db.Column(db.String(100), nullable=False)
    
    upload_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ocr_confidence = db.Column(db.Float)
    document_hash = db.Column(db.String(64), nullable=False)
    verification_status = db.Column(db.String(50))
    extracted_data = db.Column(db.JSON)
    file_path = db.Column(db.String(255))
    file_size_kb = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_loan_id_doc', 'loan_id'),
    )

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.String(50), unique=True, nullable=False)
    seller_id = db.Column(db.String(50), nullable=False)
    buyer_id = db.Column(db.String(50))
    
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    loan_count = db.Column(db.Integer, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    portfolio_price = db.Column(db.Float, nullable=False)
    portfolio_yield = db.Column(db.Float)
    
    weighted_credit_score = db.Column(db.Float)
    weighted_esg_score = db.Column(db.Float)
    avg_carbon_reduction_pct = db.Column(db.Float)
    avg_loan_term_months = db.Column(db.Float)
    
    status = db.Column(db.String(50), default='Listed')
    sale_date = db.Column(db.DateTime)
    final_price = db.Column(db.Float)
    
    loan_ids = db.Column(db.JSON)
    project_type_mix = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_portfolio_id', 'portfolio_id'),
        Index('idx_seller', 'seller_id'),
        Index('idx_status_portfolio', 'status'),
    )

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(50), unique=True, nullable=False)
    portfolio_id = db.Column(db.String(50), db.ForeignKey('portfolios.portfolio_id'))
    seller_id = db.Column(db.String(50), nullable=False)
    buyer_id = db.Column(db.String(50), nullable=False)
    
    trade_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    trade_price = db.Column(db.Float, nullable=False)
    loan_count = db.Column(db.Integer)
    portfolio_yield = db.Column(db.Float)
    settlement_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Executed')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_trade_id', 'trade_id'),
        Index('idx_portfolio_trade', 'portfolio_id'),
    )

class MonitoringRecord(db.Model):
    __tablename__ = 'monitoring_records'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String(50), db.ForeignKey('loan_applications.loan_id'))
    month = db.Column(db.Integer, nullable=False)
    monitoring_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    energy_consumption_index = db.Column(db.Float)
    energy_savings_pct = db.Column(db.Float)
    carbon_emissions_tons = db.Column(db.Float)
    carbon_reduction_pct = db.Column(db.Float)
    renewable_energy_pct = db.Column(db.Float)
    esg_score = db.Column(db.Float)
    
    in_compliance = db.Column(db.Boolean)
    project_status = db.Column(db.String(50))
    data_source = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_loan_monitoring', 'loan_id'),
        Index('idx_monitoring_date', 'monitoring_date'),
    )

class RateAdjustment(db.Model):
    __tablename__ = 'rate_adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String(50), db.ForeignKey('loan_applications.loan_id'))
    month = db.Column(db.Integer)
    adjustment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    base_rate = db.Column(db.Float, nullable=False)
    milestone_tier = db.Column(db.String(20))
    milestone_discount = db.Column(db.Float)
    energy_bonus = db.Column(db.Float)
    renewable_bonus = db.Column(db.Float)
    total_discount = db.Column(db.Float)
    adjusted_rate = db.Column(db.Float, nullable=False)
    
    carbon_reduction_pct = db.Column(db.Float)
    energy_savings_pct = db.Column(db.Float)
    renewable_energy_pct = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_loan_rate', 'loan_id'),
    )

class BlockchainLedger(db.Model):
    __tablename__ = 'blockchain_ledger'
    
    block_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transaction_type = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(50), nullable=False)
    
    portfolio_id = db.Column(db.String(50))
    seller_id = db.Column(db.String(50))
    buyer_id = db.Column(db.String(50))
    amount = db.Column(db.Float)
    
    previous_hash = db.Column(db.String(64), nullable=False)
    block_hash = db.Column(db.String(64), nullable=False, unique=True)
    merkle_root = db.Column(db.String(64))
    nonce = db.Column(db.Integer)
    
    validated = db.Column(db.Boolean, default=True)
    validator_id = db.Column(db.String(50))
    
    __table_args__ = (
        Index('idx_block_hash', 'block_hash'),
        Index('idx_transaction_id_ledger', 'transaction_id'),
    )
