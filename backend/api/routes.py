from flask import Blueprint, request, jsonify
from backend.services.loan_origination import LoanOriginationService
from backend.services.document_processor import DocumentProcessor
from backend.services.trading_engine import TradingEngine
from backend.services.covenant_monitor import CovenantMonitor
from backend.services.rate_engine import RateEngine
from backend.database.ledger import LedgerService
from werkzeug.utils import secure_filename
import os
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

loan_service = LoanOriginationService()
doc_processor = DocumentProcessor()
trading_engine = TradingEngine()
covenant_monitor = CovenantMonitor()
rate_engine = RateEngine()
ledger_service = LedgerService()

# Loan Origination Endpoints

@api_bp.route('/loans/apply', methods=['POST'])
def apply_for_loan():
    """Create new loan application"""
    try:
        loan_data = request.json
        result = loan_service.create_loan_application(loan_data)
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in loan application: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/loans/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Get loan application details"""
    try:
        result = loan_service.get_application(loan_id)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'Loan not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving loan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/loans', methods=['GET'])
def list_loans():
    """List loan applications"""
    try:
        filters = {}
        if request.args.get('approved'):
            filters['approved'] = request.args.get('approved').lower() == 'true'
        if request.args.get('country'):
            filters['country'] = request.args.get('country')
        if request.args.get('project_type'):
            filters['project_type'] = request.args.get('project_type')
        
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        result = loan_service.list_applications(filters, limit, offset)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error listing loans: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Document Processing Endpoints

@api_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        loan_id = request.form.get('loan_id')
        doc_type = request.form.get('document_type')
        
        if not loan_id:
            return jsonify({'error': 'loan_id required'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(doc_processor.upload_folder, filename)
        file.save(filepath)
        
        result = doc_processor.process_document(filepath, loan_id, doc_type)
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details"""
    try:
        result = doc_processor.get_document(document_id)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents', methods=['GET'])
def list_documents():
    """List documents"""
    try:
        loan_id = request.args.get('loan_id')
        result = doc_processor.list_documents(loan_id)
        return jsonify({'documents': result}), 200
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Trading Engine Endpoints

@api_bp.route('/portfolios/create', methods=['POST'])
def create_portfolio():
    """Create new portfolio"""
    try:
        data = request.json
        loan_ids = data.get('loan_ids', [])
        seller_id = data.get('seller_id')
        
        if not loan_ids or not seller_id:
            return jsonify({'error': 'loan_ids and seller_id required'}), 400
        
        result = trading_engine.create_portfolio(loan_ids, seller_id)
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error creating portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/portfolios/<portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    """Get portfolio details"""
    try:
        result = trading_engine.get_portfolio(portfolio_id)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'Portfolio not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/portfolios', methods=['GET'])
def list_portfolios():
    """List portfolios"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('seller_id'):
            filters['seller_id'] = request.args.get('seller_id')
        
        result = trading_engine.list_portfolios(filters)
        return jsonify({'portfolios': result}), 200
    except Exception as e:
        logger.error(f"Error listing portfolios: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trades/execute', methods=['POST'])
def execute_trade():
    """Execute trade"""
    try:
        data = request.json
        portfolio_id = data.get('portfolio_id')
        buyer_id = data.get('buyer_id')
        trade_price = data.get('trade_price')
        
        if not portfolio_id or not buyer_id:
            return jsonify({'error': 'portfolio_id and buyer_id required'}), 400
        
        result = trading_engine.execute_trade(portfolio_id, buyer_id, trade_price)
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trades', methods=['GET'])
def list_trades():
    """List trades"""
    try:
        filters = {}
        if request.args.get('portfolio_id'):
            filters['portfolio_id'] = request.args.get('portfolio_id')
        if request.args.get('buyer_id'):
            filters['buyer_id'] = request.args.get('buyer_id')
        
        result = trading_engine.list_trades(filters)
        return jsonify({'trades': result}), 200
    except Exception as e:
        logger.error(f"Error listing trades: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Covenant Monitoring Endpoints

@api_bp.route('/monitoring/generate/<loan_id>', methods=['POST'])
def generate_monitoring_data(loan_id):
    """Generate monitoring data for loan"""
    try:
        months = int(request.json.get('months', 12))
        result = covenant_monitor.generate_monitoring_data(loan_id, months)
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error generating monitoring data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/monitoring/status/<loan_id>', methods=['GET'])
def get_monitoring_status(loan_id):
    """Get current monitoring status"""
    try:
        result = covenant_monitor.get_monitoring_status(loan_id)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'No monitoring data found'}), 404
    except Exception as e:
        logger.error(f"Error getting monitoring status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/monitoring/history/<loan_id>', methods=['GET'])
def get_monitoring_history(loan_id):
    """Get monitoring history"""
    try:
        result = covenant_monitor.get_monitoring_history(loan_id)
        return jsonify({'history': result}), 200
    except Exception as e:
        logger.error(f"Error getting monitoring history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/monitoring/alerts', methods=['GET'])
def get_compliance_alerts():
    """Get compliance alerts"""
    try:
        result = covenant_monitor.get_compliance_alerts()
        return jsonify({'alerts': result}), 200
    except Exception as e:
        logger.error(f"Error getting compliance alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rate Engine Endpoints

@api_bp.route('/rates/calculate/<loan_id>', methods=['POST'])
def calculate_rate_adjustment(loan_id):
    """Calculate rate adjustment"""
    try:
        result = rate_engine.calculate_adjusted_rate(loan_id)
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error calculating rate adjustment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/rates/history/<loan_id>', methods=['GET'])
def get_rate_history(loan_id):
    """Get rate adjustment history"""
    try:
        result = rate_engine.get_rate_history(loan_id)
        return jsonify({'history': result}), 200
    except Exception as e:
        logger.error(f"Error getting rate history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/rates/savings/<loan_id>', methods=['GET'])
def get_borrower_savings(loan_id):
    """Get borrower savings"""
    try:
        result = rate_engine.calculate_borrower_savings(loan_id)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'No rate adjustment data found'}), 404
    except Exception as e:
        logger.error(f"Error calculating borrower savings: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Ledger Endpoints

@api_bp.route('/ledger/validate', methods=['GET'])
def validate_ledger():
    """Validate blockchain ledger"""
    try:
        is_valid, message = ledger_service.validate_chain()
        return jsonify({
            'is_valid': is_valid,
            'message': message
        }), 200
    except Exception as e:
        logger.error(f"Error validating ledger: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ledger/query', methods=['GET'])
def query_ledger():
    """Query ledger transactions"""
    try:
        filters = {}
        if request.args.get('transaction_type'):
            filters['transaction_type'] = request.args.get('transaction_type')
        if request.args.get('portfolio_id'):
            filters['portfolio_id'] = request.args.get('portfolio_id')
        
        blocks = ledger_service.query_ledger(filters)
        
        result = [
            {
                'block_number': block.block_number,
                'timestamp': block.timestamp.isoformat(),
                'transaction_type': block.transaction_type,
                'transaction_id': block.transaction_id,
                'portfolio_id': block.portfolio_id,
                'seller_id': block.seller_id,
                'buyer_id': block.buyer_id,
                'amount': block.amount,
                'block_hash': block.block_hash
            }
            for block in blocks
        ]
        
        return jsonify({'blocks': result}), 200
    except Exception as e:
        logger.error(f"Error querying ledger: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Dashboard Analytics Endpoints

@api_bp.route('/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get dashboard analytics summary"""
    try:
        from backend.database.models import LoanApplication, Portfolio, Trade, MonitoringRecord, RateAdjustment
        from sqlalchemy import func
        
        total_loans = LoanApplication.query.count()
        approved_loans = LoanApplication.query.filter_by(loan_approved=True).count()
        total_portfolios = Portfolio.query.count()
        total_trades = Trade.query.count()
        
        total_loan_value = db.session.query(func.sum(LoanApplication.loan_amount)).filter_by(loan_approved=True).scalar() or 0
        total_trading_volume = db.session.query(func.sum(Trade.trade_price)).scalar() or 0
        
        avg_esg_score = db.session.query(func.avg(LoanApplication.esg_composite_score)).filter_by(loan_approved=True).scalar() or 0
        avg_carbon_reduction = db.session.query(func.avg(MonitoringRecord.carbon_reduction_pct)).scalar() or 0
        
        compliance_rate = db.session.query(func.avg(MonitoringRecord.in_compliance.cast(db.Float))).scalar() or 0
        
        total_savings = 0
        rate_adjustments = RateAdjustment.query.all()
        for adj in rate_adjustments:
            loan = LoanApplication.query.filter_by(loan_id=adj.loan_id).first()
            if loan:
                base_interest = loan.loan_amount * (adj.base_rate / 100) * (loan.loan_term_months / 12)
                adjusted_interest = loan.loan_amount * (adj.adjusted_rate / 100) * (loan.loan_term_months / 12)
                total_savings += (base_interest - adjusted_interest)
        
        return jsonify({
            'total_loans': total_loans,
            'approved_loans': approved_loans,
            'approval_rate': (approved_loans / total_loans * 100) if total_loans > 0 else 0,
            'total_loan_value': total_loan_value,
            'total_portfolios': total_portfolios,
            'total_trades': total_trades,
            'total_trading_volume': total_trading_volume,
            'avg_esg_score': float(avg_esg_score),
            'avg_carbon_reduction': float(avg_carbon_reduction),
            'compliance_rate': float(compliance_rate * 100),
            'total_borrower_savings': total_savings
        }), 200
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500