import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from backend.models.credit_scoring import CreditScoringModel
from backend.services.data_fetcher import DataFetcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_training_data(n_samples=5000):
    """Generate training data for models"""
    logger.info(f"Generating {n_samples} training samples...")
    
    np.random.seed(42)
    
    # Generate features
    data = {
        'loan_amount': np.random.uniform(50000, 5000000, n_samples),
        'loan_term_months': np.random.choice([12, 24, 36, 48, 60, 84, 120], n_samples),
        'debt_to_income_ratio': np.random.uniform(0.2, 0.8, n_samples),
        'credit_score': np.random.randint(550, 850, n_samples),
        'annual_revenue': np.random.uniform(100000, 10000000, n_samples),
        'years_in_business': np.random.randint(1, 30, n_samples),
        'existing_debt': np.random.uniform(10000, 2000000, n_samples),
        'carbon_reduction_target_pct': np.random.uniform(10, 60, n_samples),
        'renewable_energy_pct': np.random.uniform(10, 90, n_samples),
        'environmental_certifications': np.random.randint(0, 5, n_samples),
        'social_impact_score': np.random.uniform(40, 100, n_samples),
        'governance_score': np.random.uniform(50, 100, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variable
    df['financial_score'] = (
        ((850 - df['credit_score']) / 300) * -25 +
        (df['debt_to_income_ratio'] * -30) +
        ((df['annual_revenue'] / df['loan_amount']) * 10).clip(0, 25) +
        50
    ).clip(0, 100)
    
    df['esg_score'] = (
        (df['carbon_reduction_target_pct'] / 60 * 25) +
        (df['renewable_energy_pct'] / 100 * 25) +
        (df['environmental_certifications'] / 5 * 10) +
        (df['social_impact_score'] / 100 * 20) +
        (df['governance_score'] / 100 * 20)
    ).clip(0, 100)
    
    df['combined_score'] = df['financial_score'] * 0.6 + df['esg_score'] * 0.4
    
    df['approved'] = (
        (df['combined_score'] > 60) &
        (df['credit_score'] > 620) &
        (df['debt_to_income_ratio'] < 0.65) &
        (df['esg_score'] > 40)
    ).astype(int)
    
    return df

def train_models():
    """Train all ML models"""
    logger.info("Starting model training...")
    
    # Generate training data
    df = generate_training_data()
    
    # Prepare features and target
    feature_cols = [
        'loan_amount', 'loan_term_months', 'debt_to_income_ratio',
        'credit_score', 'annual_revenue', 'years_in_business',
        'existing_debt', 'carbon_reduction_target_pct',
        'renewable_energy_pct', 'environmental_certifications',
        'social_impact_score', 'governance_score'
    ]
    
    X = df[feature_cols].values
    y = df['approved'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set size: {len(X_train)}")
    logger.info(f"Test set size: {len(X_test)}")
    
    # Train models
    model = CreditScoringModel()
    model.train_models(X_train, y_train)
    
    # Evaluate models
    logger.info("\nEvaluating models on test set...")
    for model_name in ['random_forest', 'xgboost', 'lightgbm', 'gradient_boosting']:
        predictions = model.predict(X_test[0], model_name)
        logger.info(f"{model_name}: {predictions}")
    
    # Save models
    logger.info("\nSaving models...")
    model.save_models()
    
    logger.info("Model training completed successfully")

if __name__ == '__main__':
    train_models()