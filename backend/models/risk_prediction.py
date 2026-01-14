import numpy as np
from sklearn.ensemble import RandomForestRegressor
import logging

logger = logging.getLogger(__name__)

class RiskPredictionModel:
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
            max_depth=10
        )
        self.feature_names = [
            'credit_score', 'debt_to_income_ratio', 'years_in_business',
            'esg_composite_score', 'loan_amount', 'loan_term_months'
        ]
    
    def calculate_risk_score(self, loan_data):
        """Calculate default risk score"""
        try:
            credit_score = loan_data.get('credit_score', 650)
            dti_ratio = loan_data.get('debt_to_income_ratio', 0.4)
            esg_score = loan_data.get('esg_composite_score', 50)
            
            risk_score = (
                (100 - (credit_score - 550) / 300 * 100) / 100 * 0.4 +
                dti_ratio * 0.3 +
                (100 - esg_score) / 100 * 0.2 +
                np.random.uniform(0, 0.1)
            )
            
            risk_score = max(0, min(risk_score, 1))
            
            if risk_score < 0.2:
                risk_category = 'Low Risk'
            elif risk_score < 0.4:
                risk_category = 'Medium Risk'
            elif risk_score < 0.6:
                risk_category = 'High Risk'
            else:
                risk_category = 'Very High Risk'
            
            return {
                'risk_score': risk_score,
                'risk_category': risk_category,
                'default_probability': risk_score
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return {
                'risk_score': 0.5,
                'risk_category': 'Unknown',
                'default_probability': 0.5
            }
    
    def train(self, X_train, y_train):
        """Train risk prediction model"""
        try:
            self.model.fit(X_train, y_train)
            logger.info("Risk prediction model trained successfully")
        except Exception as e:
            logger.error(f"Error training risk model: {str(e)}")
            raise
    
    def predict(self, features):
        """Predict default risk"""
        try:
            prediction = self.model.predict([features])[0]
            return max(0, min(prediction, 1))
        except Exception as e:
            logger.error(f"Error predicting risk: {str(e)}")
            return 0.5
