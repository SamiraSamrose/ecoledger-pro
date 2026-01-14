import logging
from datetime import datetime
from backend.database.models import db, RateAdjustment, LoanApplication, MonitoringRecord
from config.settings import Config

logger = logging.getLogger(__name__)

class RateEngine:
    
    def __init__(self):
        self.milestone_tiers = Config.MILESTONE_TIERS
    
    def calculate_base_rate(self, loan):
        """Calculate base interest rate for loan"""
        base_rate = 5.0
        
        credit_score = loan.credit_score if loan.credit_score else 650
        
        if credit_score >= 800:
            credit_adjustment = -1.0
        elif credit_score >= 750:
            credit_adjustment = -0.5
        elif credit_score >= 700:
            credit_adjustment = 0.0
        elif credit_score >= 650:
            credit_adjustment = 0.5
        else:
            credit_adjustment = 1.5
        
        term_adjustment = (loan.loan_term_months / 120) * 0.5
        
        esg_adjustment = -((loan.esg_composite_score / 100) * 0.5)
        
        initial_rate = base_rate + credit_adjustment + term_adjustment + esg_adjustment
        initial_rate = max(2.5, min(initial_rate, 12.0))
        
        return initial_rate
    
    def determine_milestone_tier(self, carbon_reduction_pct):
        """Determine milestone tier achieved"""
        achieved_tier = None
        max_discount = 0.0
        
        for tier, criteria in self.milestone_tiers.items():
            if carbon_reduction_pct >= criteria['carbon_reduction_min']:
                if criteria['rate_discount'] > max_discount:
                    achieved_tier = tier
                    max_discount = criteria['rate_discount']
        
        return achieved_tier, max_discount
    
    def calculate_adjusted_rate(self, loan_id):
        """Calculate adjusted rate based on performance"""
        try:
            loan = LoanApplication.query.filter_by(loan_id=loan_id).first()
            if not loan:
                raise ValueError("Loan not found")
            
            monitoring_record = MonitoringRecord.query.filter_by(
                loan_id=loan_id
            ).order_by(MonitoringRecord.monitoring_date.desc()).first()
            
            if not monitoring_record:
                raise ValueError("No monitoring data available")
            
            base_rate = self.calculate_base_rate(loan)
            
            carbon_reduction = monitoring_record.carbon_reduction_pct
            tier, discount = self.determine_milestone_tier(carbon_reduction)
            
            energy_bonus = 0.0
            if monitoring_record.energy_savings_pct > 40:
                energy_bonus = 0.15
            elif monitoring_record.energy_savings_pct > 30:
                energy_bonus = 0.10
            elif monitoring_record.energy_savings_pct > 20:
                energy_bonus = 0.05
            
            renewable_bonus = 0.0
            if monitoring_record.renewable_energy_pct > 60:
                renewable_bonus = 0.15
            elif monitoring_record.renewable_energy_pct > 40:
                renewable_bonus = 0.10
            
            total_discount = discount + energy_bonus + renewable_bonus
            adjusted_rate = base_rate - total_discount
            adjusted_rate = max(1.5, adjusted_rate)
            
            rate_adjustment = RateAdjustment(
                loan_id=loan_id,
                month=monitoring_record.month,
                adjustment_date=datetime.utcnow(),
                base_rate=base_rate,
                milestone_tier=tier if tier else 'None',
                milestone_discount=discount,
                energy_bonus=energy_bonus,
                renewable_bonus=renewable_bonus,
                total_discount=total_discount,
                adjusted_rate=adjusted_rate,
                carbon_reduction_pct=carbon_reduction,
                energy_savings_pct=monitoring_record.energy_savings_pct,
                renewable_energy_pct=monitoring_record.renewable_energy_pct
            )
            
            db.session.add(rate_adjustment)
            db.session.commit()
            
            logger.info(f"Rate adjustment calculated for loan {loan_id}: {base_rate:.2f}% -> {adjusted_rate:.2f}%")
            
            return {
                'loan_id': loan_id,
                'base_rate': base_rate,
                'adjusted_rate': adjusted_rate,
                'milestone_tier': tier if tier else 'None',
                'total_discount': total_discount,
                'rate_change_pct': ((adjusted_rate - base_rate) / base_rate) * 100
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error calculating adjusted rate: {str(e)}")
            raise
    
    def get_rate_history(self, loan_id):
        """Get rate adjustment history for loan"""
        try:
            adjustments = RateAdjustment.query.filter_by(
                loan_id=loan_id
            ).order_by(RateAdjustment.month).all()
            
            return [
                {
                    'month': adj.month,
                    'adjustment_date': adj.adjustment_date.isoformat(),
                    'base_rate': adj.base_rate,
                    'adjusted_rate': adj.adjusted_rate,
                    'milestone_tier': adj.milestone_tier,
                    'total_discount': adj.total_discount,
                    'carbon_reduction_pct': adj.carbon_reduction_pct
                }
                for adj in adjustments
            ]
            
        except Exception as e:
            logger.error(f"Error getting rate history: {str(e)}")
            return []
    
    def calculate_borrower_savings(self, loan_id):
        """Calculate total savings from rate adjustments"""
        try:
            loan = LoanApplication.query.filter_by(loan_id=loan_id).first()
            if not loan:
                return None
            
            latest_adjustment = RateAdjustment.query.filter_by(
                loan_id=loan_id
            ).order_by(RateAdjustment.adjustment_date.desc()).first()
            
            if not latest_adjustment:
                return None
            
            base_interest = loan.loan_amount * (latest_adjustment.base_rate / 100) * (loan.loan_term_months / 12)
            adjusted_interest = loan.loan_amount * (latest_adjustment.adjusted_rate / 100) * (loan.loan_term_months / 12)
            savings = base_interest - adjusted_interest
            
            return {
                'loan_id': loan_id,
                'loan_amount': loan.loan_amount,
                'base_interest': base_interest,
                'adjusted_interest': adjusted_interest,
                'total_savings': savings,
                'savings_pct': (savings / base_interest * 100) if base_interest > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating borrower savings: {str(e)}")
            return None
