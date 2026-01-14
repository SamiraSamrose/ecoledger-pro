import uuid
import numpy as np
from datetime import datetime, timedelta
import logging
from backend.database.models import db, MonitoringRecord, LoanApplication
from config.settings import Config

logger = logging.getLogger(__name__)

class CovenantMonitor:
    
    def __init__(self):
        self.thresholds = Config.COVENANT_THRESHOLDS
    
    def generate_monitoring_data(self, loan_id, months=12):
        """Generate monitoring data for loan"""
        try:
            loan = LoanApplication.query.filter_by(loan_id=loan_id).first()
            if not loan:
                raise ValueError("Loan not found")
            
            baseline_energy = 100
            baseline_emissions = 10.0
            
            records = []
            
            for month in range(1, months + 1):
                performance_factor = np.random.normal(1.0, 0.1)
                
                target_savings = loan.carbon_reduction_target_pct / 100
                actual_savings = target_savings * performance_factor * (1 +month / 24)
                actual_savings = max(0, min(actual_savings, 0.8))
                
                energy_consumption = baseline_energy * (1 - actual_savings)
                energy_savings_pct = actual_savings * 100
                
                carbon_reduction_pct = actual_savings * 100 * 0.9
                current_emissions = baseline_emissions * (1 - carbon_reduction_pct / 100)
                
                renewable_pct = loan.renewable_energy_pct + (month * 0.5)
                renewable_pct = min(renewable_pct, 95)
                
                esg_adjustment = (actual_savings - target_savings) * 50
                current_esg = loan.esg_composite_score + esg_adjustment
                current_esg = max(30, min(current_esg, 100))
                
                in_compliance = (
                    energy_savings_pct >= self.thresholds['min_energy_savings_pct'] and
                    carbon_reduction_pct >= self.thresholds['min_carbon_reduction_pct'] and
                    renewable_pct >= self.thresholds['min_renewable_energy_pct'] and
                    current_esg >= self.thresholds['min_esg_score']
                )
                
                record = MonitoringRecord(
                    loan_id=loan_id,
                    month=month,
                    monitoring_date=datetime.utcnow() - timedelta(days=30*(months-month)),
                    energy_consumption_index=energy_consumption,
                    energy_savings_pct=energy_savings_pct,
                    carbon_emissions_tons=current_emissions,
                    carbon_reduction_pct=carbon_reduction_pct,
                    renewable_energy_pct=renewable_pct,
                    esg_score=current_esg,
                    in_compliance=in_compliance,
                    project_status='Compliant' if in_compliance else 'At Risk',
                    data_source=np.random.choice(['IoT Sensors', 'Utility Reports', 'Third-Party Audit'])
                )
                
                records.append(record)
            
            db.session.bulk_save_objects(records)
            db.session.commit()
            
            logger.info(f"Generated {months} months of monitoring data for loan {loan_id}")
            
            return {
                'loan_id': loan_id,
                'months_monitored': months,
                'records_created': len(records)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error generating monitoring data: {str(e)}")
            raise
    
    def get_monitoring_status(self, loan_id):
        """Get current monitoring status for loan"""
        try:
            latest_record = MonitoringRecord.query.filter_by(
                loan_id=loan_id
            ).order_by(MonitoringRecord.monitoring_date.desc()).first()
            
            if not latest_record:
                return None
            
            return {
                'loan_id': loan_id,
                'monitoring_date': latest_record.monitoring_date.isoformat(),
                'month': latest_record.month,
                'energy_savings_pct': latest_record.energy_savings_pct,
                'carbon_reduction_pct': latest_record.carbon_reduction_pct,
                'renewable_energy_pct': latest_record.renewable_energy_pct,
                'esg_score': latest_record.esg_score,
                'in_compliance': latest_record.in_compliance,
                'project_status': latest_record.project_status,
                'data_source': latest_record.data_source
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {str(e)}")
            return None
    
    def get_monitoring_history(self, loan_id):
        """Get full monitoring history for loan"""
        try:
            records = MonitoringRecord.query.filter_by(
                loan_id=loan_id
            ).order_by(MonitoringRecord.month).all()
            
            return [
                {
                    'month': r.month,
                    'monitoring_date': r.monitoring_date.isoformat(),
                    'energy_savings_pct': r.energy_savings_pct,
                    'carbon_reduction_pct': r.carbon_reduction_pct,
                    'renewable_energy_pct': r.renewable_energy_pct,
                    'esg_score': r.esg_score,
                    'in_compliance': r.in_compliance,
                    'project_status': r.project_status
                }
                for r in records
            ]
            
        except Exception as e:
            logger.error(f"Error getting monitoring history: {str(e)}")
            return []
    
    def get_compliance_alerts(self):
        """Get all non-compliant loans"""
        try:
            latest_records = db.session.query(
                MonitoringRecord
            ).join(
                db.session.query(
                    MonitoringRecord.loan_id,
                    db.func.max(MonitoringRecord.monitoring_date).label('max_date')
                ).group_by(MonitoringRecord.loan_id).subquery(),
                db.and_(
                    MonitoringRecord.loan_id == db.text('anon_1.loan_id'),
                    MonitoringRecord.monitoring_date == db.text('anon_1.max_date')
                )
            ).filter(
                MonitoringRecord.in_compliance == False
            ).all()
            
            alerts = []
            for record in latest_records:
                violation_reasons = []
                
                if record.energy_savings_pct < self.thresholds['min_energy_savings_pct']:
                    violation_reasons.append(f"Energy savings below threshold: {record.energy_savings_pct:.1f}%")
                
                if record.carbon_reduction_pct < self.thresholds['min_carbon_reduction_pct']:
                    violation_reasons.append(f"Carbon reduction below threshold: {record.carbon_reduction_pct:.1f}%")
                
                if record.renewable_energy_pct < self.thresholds['min_renewable_energy_pct']:
                    violation_reasons.append(f"Renewable energy below threshold: {record.renewable_energy_pct:.1f}%")
                
                if record.esg_score < self.thresholds['min_esg_score']:
                    violation_reasons.append(f"ESG score below threshold: {record.esg_score:.1f}")
                
                alerts.append({
                    'loan_id': record.loan_id,
                    'monitoring_date': record.monitoring_date.isoformat(),
                    'severity': 'High' if len(violation_reasons) > 2 else 'Medium',
                    'violation_reasons': violation_reasons,
                    'recommended_action': 'Schedule borrower review and remediation plan'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting compliance alerts: {str(e)}")
            return []
