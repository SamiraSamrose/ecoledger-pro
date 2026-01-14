import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
import logging
from config.settings import Config

logger = logging.getLogger(__name__)

class CreditScoringModel:
    
    def __init__(self):
        self.model_path = Config.MODEL_PATH
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = [
            'loan_amount', 'loan_term_months', 'debt_to_income_ratio', 
            'credit_score', 'annual_revenue', 'years_in_business', 
            'existing_debt', 'carbon_reduction_target_pct', 
            'renewable_energy_pct', 'environmental_certifications',
            'social_impact_score', 'governance_score'
        ]
    
    def train_models(self, X_train, y_train):
        """Train multiple ML models"""
        try:
            logger.info("Training credit scoring models")
            
            # Random Forest
            rf_model = RandomForestClassifier(
                n_estimators=100, 
                random_state=42, 
                n_jobs=-1,
                max_depth=10,
                min_samples_split=10
            )
            rf_model.fit(X_train, y_train)
            self.models['random_forest'] = rf_model
            
            # XGBoost
            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                random_state=42,
                eval_metric='logloss',
                max_depth=6,
                learning_rate=0.1
            )
            xgb_model.fit(X_train, y_train)
            self.models['xgboost'] = xgb_model
            
            # LightGBM
            lgb_model = lgb.LGBMClassifier(
                n_estimators=100,
                random_state=42,
                verbose=-1,
                max_depth=6,
                learning_rate=0.1
            )
            lgb_model.fit(X_train, y_train)
            self.models['lightgbm'] = lgb_model
            
            # Gradient Boosting
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=6,
                learning_rate=0.1
            )
            gb_model.fit(X_train, y_train)
            self.models['gradient_boosting'] = gb_model
            
            # Fit scaler
            self.scaler.fit(X_train)
            
            logger.info("All models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise
    
    def predict(self, features, model_name='xgboost'):
        """Make prediction using specified model"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            prediction = model.predict([features])[0]
            probability = model.predict_proba([features])[0]
            
            return {
                'prediction': int(prediction),
                'probability_approved': float(probability[1]),
                'probability_rejected': float(probability[0]),
                'model_used': model_name
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_feature_importance(self, model_name='xgboost'):
        """Get feature importance from model"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            importances = model.feature_importances_
            
            feature_importance = [
                {
                    'feature': name,
                    'importance': float(importance)
                }
                for name, importance in zip(self.feature_names, importances)
            ]
            
            return sorted(feature_importance, key=lambda x: x['importance'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return []
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            os.makedirs(self.model_path, exist_ok=True)
            
            for name, model in self.models.items():
                filepath = os.path.join(self.model_path, f'{name}_model.pkl')
                with open(filepath, 'wb') as f:
                    pickle.dump(model, f)
            
            scaler_path = os.path.join(self.model_path, 'scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info(f"Models saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            model_files = {
                'random_forest': 'random_forest_model.pkl',
                'xgboost': 'xgboost_model.pkl',
                'lightgbm': 'lightgbm_model.pkl',
                'gradient_boosting': 'gradient_boosting_model.pkl'
            }
            
            for name, filename in model_files.items():
                filepath = os.path.join(self.model_path, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        self.models[name] = pickle.load(f)
            
            scaler_path = os.path.join(self.model_path, 'scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            logger.info(f"Models loaded from {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
