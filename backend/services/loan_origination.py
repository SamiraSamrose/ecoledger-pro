import uuid
import numpy as np
from datetime import datetime
import logging
from backend.database.models import db, LoanApplication
from backend.models.credit_scoring import CreditScoringModel

logger = logging.getLogger(__name__)

class LoanOriginationService:
    
    def __init__(self):
        self.credit_model = CreditScoringModel()
    
    def calculate_financial_health_score(self, loan_data):
        """Calculate financial health score from borrower data"""
        try:
            credit_score = loan_data.get('credit_score', 650)
            dti_ratio = loan_data.get('debt_to_income_ratio', 0.4)
            annual_revenue = loan_data.get('annual_revenue', 0)
            loan_amount = loan_data.get('loan_amount', 0)
            years_in_business = loan_data.get('years_in_business', 5)
            
            score = 50  # Base score
            
            # Credit score component
            if credit_score >= 800:
                score += 25
            elif credit_score >= 750:
                score += 20
            elif credit_score >= 700:
                score += 15
            elif credit_score >= 650:
                score += 10
            else:
                score += 5
            
            # Debt to income ratio component
            score -= (dti_ratio * 30)
            
            # Revenue coverage component
            if loan_amount > 0 and annual_revenue > 0:
                coverage = annual_revenue / loan_amount
                score += min(coverage * 10, 25)
            
            # Business experience component
            if years_in_business >= 10:
                score += 10
            elif years_in_business >= 5:
                score += 5
            
            return max(0, min(score, 100))
            
        except Exception as e:
            logger.error(f"Error calculating financial health score: {str(e)}")
            return 50
    
    def calculate_esg_composite_score(self, loan_data):
        """Calculate ESG composite score"""
        try:
            carbon_target = loan_data.get('carbon_reduction_target_pct', 0)
            renewable_pct = loan_data.get('renewable_energy_pct', 0)
            energy_rating = loan_data.get('energy_efficiency_rating', 'C')
            certifications = loan_data.get('environmental_certifications', 0)
            social_score = loan_data.get('social_impact_score', 50)
            governance_score = loan_data.get('governance_score', 50)
            
            # Energy rating mapping
            rating_map = {'A': 100, 'B': 80, 'C': 60, 'D': 40, 'E': 20}
            energy_numeric = rating_map.get(energy_rating, 60)
            
            # Calculate composite
            esg_score = (
                (carbon_target / 60 * 25) +
                (renewable_pct / 100 * 25) +
                (energy_numeric / 100 * 20) +
                (certifications / 5 * 10) +
                (social_score / 100 * 10) +
                (governance_score / 100 * 10)
            )
            
            return max(0, min(esg_score, 100))
            
        except Exception as e:
            logger.error(f"Error calculating ESG score: {str(e)}")
            return 50
    
    def create_loan_application(self, loan_data):
        """Create new loan application"""
        try:
            loan_id = f"GL{str(uuid.uuid4())[:8].upper()}"
            
            # Calculate scores
            financial_score = self.calculate_financial_health_score(loan_data)
            esg_score = self.calculate_esg_composite_score(loan_data)
            combined_score = financial_score * 0.6 + esg_score * 0.4
            
            # Determine approval
            approved = (
                combined_score > 60 and
                loan_data.get('credit_score', 0) > 620 and
                loan_data.get('debt_to_income_ratio', 1) < 0.65 and
                esg_score > 40
            )
            
            # Create application
            application = LoanApplication(
                loan_id=loan_id,
                country=loan_data.get('country', 'Unknown'),
                country_code=loan_data.get('country_code'),
                year=loan_data.get('year', datetime.now().year),
                loan_amount=loan_data.get('loan_amount'),
                loan_term_months=loan_data.get('loan_term_months'),
                project_type=loan_data.get('project_type'),
                
                debt_to_income_ratio=loan_data.get('debt_to_income_ratio'),
                credit_score=loan_data.get('credit_score'),
                annual_revenue=loan_data.get('annual_revenue'),
                years_in_business=loan_data.get('years_in_business'),
                existing_debt=loan_data.get('existing_debt'),
                
                carbon_reduction_target_pct=loan_data.get('carbon_reduction_target_pct'),
                renewable_energy_pct=loan_data.get('renewable_energy_pct'),
                energy_efficiency_rating=loan_data.get('energy_efficiency_rating'),
                environmental_certifications=loan_data.get('environmental_certifications'),
                social_impact_score=loan_data.get('social_impact_score'),
                governance_score=loan_data.get('governance_score'),
                
                financial_health_score=financial_score,
                esg_composite_score=esg_score,
                combined_credit_score=combined_score,
                loan_approved=approved,
                processing_status='Approved' if approved else 'Rejected',
                application_date=datetime.utcnow()
            )
            
            db.session.add(application)
            db.session.commit()
            
            logger.info(f"Loan application {loan_id} created - Status: {application.processing_status}")
            
            return {
                'loan_id': loan_id,
                'approved': approved,
                'financial_health_score': financial_score,
                'esg_composite_score': esg_score,
                'combined_credit_score': combined_score,
                'processing_status': application.processing_status
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating loan application: {str(e)}")
            raise
    
    def get_application(self, loan_id):
        """Retrieve loan application"""
        try:
            application = LoanApplication.query.filter_by(loan_id=loan_id).first()
            if not application:
                return None
            
            return {
                'loan_id': application.loan_id,
                'country': application.country,
                'loan_amount': application.loan_amount,
                'loan_term_months': application.loan_term_months,
                'project_type': application.project_type,
                'credit_score': application.credit_score,
                'financial_health_score': application.financial_health_score,
                'esg_composite_score': application.esg_composite_score,
                'combined_credit_score': application.combined_credit_score,
                'loan_approved': application.loan_approved,
                'processing_status': application.processing_status,
                'application_date': application.application_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving application: {str(e)}")
            return None
    
    def list_applications(self, filters=None, limit=100, offset=0):
        """List loan applications with filters"""
        try:
            query = LoanApplication.query
            
            if filters:
                if 'approved' in filters:
                    query = query.filter(LoanApplication.loan_approved == filters['approved'])
                if 'country' in filters:
                    query = query.filter(LoanApplication.country == filters['country'])
                if 'project_type' in filters:
                    query = query.filter(LoanApplication.project_type == filters['project_type'])
            
            total = query.count()
            applications = query.order_by(LoanApplication.application_date.desc()).limit(limit).offset(offset).all()
            
            return {
                'total': total,
                'limit': limit,
                'offset': offset,
                'applications': [
                    {
                        'loan_id': app.loan_id,
                        'country': app.country,
                        'loan_amount': app.loan_amount,
                        'project_type': app.project_type,
                        'combined_credit_score': app.combined_credit_score,
                        'loan_approved': app.loan_approved,
                        'processing_status': app.processing_status,
                        'application_date': app.application_date.isoformat()
                    }
                    for app in applications
                ]
            }
            
        except Exception as e:
            logger.error(f"Error listing applications: {str(e)}")
            return {'total': 0, 'applications': []}
