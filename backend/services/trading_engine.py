import uuid
from datetime import datetime, timedelta
import logging
from backend.database.models import db, Portfolio, Trade, LoanApplication
from backend.database.ledger import LedgerService

logger = logging.getLogger(__name__)

class TradingEngine:
    
    def __init__(self):
        self.ledger = LedgerService()
    
    def create_portfolio(self, loan_ids, seller_id):
        """Create portfolio from loans"""
        try:
            portfolio_id = f"PORT{str(uuid.uuid4())[:8].upper()}"
            
            loans = LoanApplication.query.filter(
                LoanApplication.loan_id.in_(loan_ids)
            ).all()
            
            if not loans:
                raise ValueError("No valid loans found")
            
            total_value = sum(loan.loan_amount for loan in loans)
            
            weighted_credit = sum(
                loan.combined_credit_score * loan.loan_amount for loan in loans
            ) / total_value
            
            weighted_esg = sum(
                loan.esg_composite_score * loan.loan_amount for loan in loans
            ) / total_value
            
            avg_carbon = sum(loan.carbon_reduction_target_pct for loan in loans) / len(loans)
            avg_term = sum(loan.loan_term_months for loan in loans) / len(loans)
            
            project_mix = {}
            for loan in loans:
                project_mix[loan.project_type] = project_mix.get(loan.project_type, 0) + 1
            
            base_yield = 0.05
            esg_premium = (weighted_esg / 100) * 0.02
            risk_adjustment = ((100 - weighted_credit) / 100) * 0.03
            
            portfolio_yield = base_yield + esg_premium + risk_adjustment
            portfolio_price = total_value * (1 - risk_adjustment * 0.5)
            
            portfolio = Portfolio(
                portfolio_id=portfolio_id,
                seller_id=seller_id,
                creation_date=datetime.utcnow(),
                loan_count=len(loans),
                total_value=total_value,
                portfolio_price=portfolio_price,
                portfolio_yield=portfolio_yield,
                weighted_credit_score=weighted_credit,
                weighted_esg_score=weighted_esg,
                avg_carbon_reduction_pct=avg_carbon,
                avg_loan_term_months=avg_term,
                status='Listed',
                loan_ids=loan_ids,
                project_type_mix=project_mix
            )
            
            db.session.add(portfolio)
            db.session.commit()
            
            self.ledger.add_transaction(
                'PORTFOLIO_CREATED',
                portfolio_id,
                portfolio_id=portfolio_id,
                seller_id=seller_id,
                amount=total_value
            )
            
            logger.info(f"Portfolio {portfolio_id} created with {len(loans)} loans")
            
            return {
                'portfolio_id': portfolio_id,
                'loan_count': len(loans),
                'total_value': total_value,
                'portfolio_price': portfolio_price,
                'portfolio_yield': portfolio_yield,
                'weighted_credit_score': weighted_credit,
                'weighted_esg_score': weighted_esg,
                'status': 'Listed'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating portfolio: {str(e)}")
            raise
    
    def execute_trade(self, portfolio_id, buyer_id, trade_price=None):
        """Execute trade for portfolio"""
        try:
            portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id).first()
            
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            if portfolio.status != 'Listed':
                raise ValueError("Portfolio not available for trading")
            
            if not trade_price:
                trade_price = portfolio.portfolio_price
            
            trade_id = f"TRADE{str(uuid.uuid4())[:8].upper()}"
            
            trade = Trade(
                trade_id=trade_id,
                portfolio_id=portfolio_id,
                seller_id=portfolio.seller_id,
                buyer_id=buyer_id,
                trade_timestamp=datetime.utcnow(),
                trade_price=trade_price,
                loan_count=portfolio.loan_count,
                portfolio_yield=portfolio.portfolio_yield,
                settlement_date=datetime.utcnow() + timedelta(days=3),
                status='Executed'
            )
            
            portfolio.status = 'Sold'
            portfolio.sale_date = datetime.utcnow()
            portfolio.buyer_id = buyer_id
            portfolio.final_price = trade_price
            
            db.session.add(trade)
            db.session.commit()
            
            self.ledger.add_transaction(
                'TRADE_EXECUTED',
                trade_id,
                portfolio_id=portfolio_id,
                seller_id=portfolio.seller_id,
                buyer_id=buyer_id,
                amount=trade_price
            )
            
            logger.info(f"Trade {trade_id} executed for portfolio {portfolio_id}")
            
            return {
                'trade_id': trade_id,
                'portfolio_id': portfolio_id,
                'seller_id': portfolio.seller_id,
                'buyer_id': buyer_id,
                'trade_price': trade_price,
                'trade_timestamp': trade.trade_timestamp.isoformat(),
                'status': 'Executed'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error executing trade: {str(e)}")
            raise
    
    def get_portfolio(self, portfolio_id):
        """Retrieve portfolio information"""
        try:
            portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id).first()
            if not portfolio:
                return None
            
            return {
                'portfolio_id': portfolio.portfolio_id,
                'seller_id': portfolio.seller_id,
                'buyer_id': portfolio.buyer_id,
                'loan_count': portfolio.loan_count,
                'total_value': portfolio.total_value,
                'portfolio_price': portfolio.portfolio_price,
                'portfolio_yield': portfolio.portfolio_yield,
                'weighted_credit_score': portfolio.weighted_credit_score,
                'weighted_esg_score': portfolio.weighted_esg_score,
                'avg_carbon_reduction_pct': portfolio.avg_carbon_reduction_pct,
                'status': portfolio.status,
                'creation_date': portfolio.creation_date.isoformat(),
                'sale_date': portfolio.sale_date.isoformat() if portfolio.sale_date else None,
                'final_price': portfolio.final_price
            }
            
        except Exception as e:
            logger.error(f"Error retrieving portfolio: {str(e)}")
            return None
    
    def list_portfolios(self, filters=None):
        """List portfolios with filters"""
        try:
            query = Portfolio.query
            
            if filters:
                if 'status' in filters:
                    query = query.filter(Portfolio.status == filters['status'])
                if 'seller_id' in filters:
                    query = query.filter(Portfolio.seller_id == filters['seller_id'])
            
            portfolios = query.order_by(Portfolio.creation_date.desc()).all()
            
            return [
                {
                    'portfolio_id': p.portfolio_id,
                    'seller_id': p.seller_id,
                    'loan_count': p.loan_count,
                    'total_value': p.total_value,
                    'portfolio_price': p.portfolio_price,
                    'portfolio_yield': p.portfolio_yield,
                    'weighted_esg_score': p.weighted_esg_score,
                    'status': p.status,
                    'creation_date': p.creation_date.isoformat()
                }
                for p in portfolios
            ]
            
        except Exception as e:
            logger.error(f"Error listing portfolios: {str(e)}")
            return []
    
    def list_trades(self, filters=None):
        """List trades with filters"""
        try:
            query = Trade.query
            
            if filters:
                if 'portfolio_id' in filters:
                    query = query.filter(Trade.portfolio_id == filters['portfolio_id'])
                if 'buyer_id' in filters:
                    query = query.filter(Trade.buyer_id == filters['buyer_id'])
            
            trades = query.order_by(Trade.trade_timestamp.desc()).all()
            
            return [
                {
                    'trade_id': t.trade_id,
                    'portfolio_id': t.portfolio_id,
                    'seller_id': t.seller_id,
                    'buyer_id': t.buyer_id,
                    'trade_price': t.trade_price,
                    'loan_count': t.loan_count,
                    'portfolio_yield': t.portfolio_yield,
                    'trade_timestamp': t.trade_timestamp.isoformat(),
                    'status': t.status
                }
                for t in trades
            ]
            
        except Exception as e:
            logger.error(f"Error listing trades: {str(e)}")
            return []
