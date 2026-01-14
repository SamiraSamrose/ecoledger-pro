import numpy as np
from scipy.optimize import minimize
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    
    def __init__(self):
        self.risk_free_rate = 0.03
    
    def calculate_portfolio_metrics(self, loans):
        """Calculate portfolio risk and return metrics"""
        try:
            if not loans:
                return None
            
            total_value = sum(loan['loan_amount'] for loan in loans)
            weights = [loan['loan_amount'] / total_value for loan in loans]
            
            expected_returns = [
                loan.get('portfolio_yield', 0.05) for loan in loans
            ]
            
            portfolio_return = sum(w * r for w, r in zip(weights, expected_returns))
            
            risk_scores = [
                loan.get('risk_score', 0.3) for loan in loans
            ]
            
            portfolio_risk = np.sqrt(sum(w**2 * r**2 for w, r in zip(weights, risk_scores)))
            
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0
            
            diversification_score = len(set(loan.get('project_type', 'Unknown') for loan in loans)) / 8 * 100
            
            return {
                'portfolio_return': portfolio_return,
                'portfolio_risk': portfolio_risk,
                'sharpe_ratio': sharpe_ratio,
                'diversification_score': diversification_score
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return None
    
    def optimize_portfolio(self, available_loans, target_value, constraints=None):
        """Optimize portfolio selection"""
        try:
            if not available_loans or target_value <= 0:
                return None
            
            n_loans = len(available_loans)
            
            def objective(weights):
                returns = [loan.get('portfolio_yield', 0.05) for loan in available_loans]
                risks = [loan.get('risk_score', 0.3) for loan in available_loans]
                
                portfolio_return = sum(w * r for w, r in zip(weights, returns))
                portfolio_risk = np.sqrt(sum(w**2 * r**2 for w, r in zip(weights, risks)))
                
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0
                
                return -sharpe
            
            constraints_list = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}
            ]
            
            bounds = tuple((0, 1) for _ in range(n_loans))
            
            initial_weights = np.array([1.0 / n_loans] * n_loans)
            
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list
            )
            
            if result.success:
                optimal_weights = result.x
                selected_loans = [
                    {
                        'loan_id': loan['loan_id'],
                        'weight': float(weight),
                        'amount': float(weight * target_value)
                    }
                    for loan, weight in zip(available_loans, optimal_weights)
                    if weight > 0.01
                ]
                
                return {
                    'success': True,
                    'selected_loans': selected_loans,
                    'sharpe_ratio': -result.fun
                }
            else:
                return {'success': False, 'message': 'Optimization failed'}
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {str(e)}")
            return {'success': False, 'message': str(e)}
