"""
Database manager for ML Engine
Connects to PostgreSQL and provides query methods
"""

import sys
from pathlib import Path
import pandas as pd

# Add database package to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'database'))

from db_utils import DatabaseManager as BaseDBManager, OperationalDataQueries


class DatabaseManager(BaseDBManager):
    """Extended database manager for ML engine."""
    
    def check_connection(self) -> bool:
        """Test database connection."""
        try:
            result = self.execute_query("SELECT 1", fetch=True)
            return result is not None
        except:
            return False


class OperationalQueries(OperationalDataQueries):
    """Extended operational queries for ML engine."""
    
    def get_all_resource_metrics(
        self,
        organization_id: str,
        days: int = 30
    ) -> pd.DataFrame:
        """Get all resource metrics for anomaly detection training."""
        query = """
            SELECT 
                rm.time,
                rm.resource_id,
                rm.utilization_rate,
                rm.throughput,
                rm.efficiency_score,
                rm.downtime_minutes,
                rm.error_count,
                rm.energy_consumption
            FROM resource_metrics rm
            JOIN resources r ON rm.resource_id = r.id
            WHERE r.organization_id = %s
              AND rm.time >= NOW() - INTERVAL '%s days'
            ORDER BY rm.time ASC
        """
        result = self.db.execute_query(query, (organization_id, days))
        return pd.DataFrame(result) if result else pd.DataFrame()
    
    def insert_demand_forecast(
        self,
        organization_id: str,
        product_id: str,
        forecast_date,
        predicted_quantity: float,
        confidence_lower: float,
        confidence_upper: float,
        model_name: str,
        accuracy_score: float
    ):
        """Insert demand forecast into database."""
        query = """
            INSERT INTO demand_forecasts (
                organization_id, product_id, forecast_date,
                predicted_quantity, confidence_lower, confidence_upper,
                model_name, accuracy_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (organization_id, product_id, forecast_date, model_name)
            DO UPDATE SET
                predicted_quantity = EXCLUDED.predicted_quantity,
                confidence_lower = EXCLUDED.confidence_lower,
                confidence_upper = EXCLUDED.confidence_upper,
                accuracy_score = EXCLUDED.accuracy_score,
                created_at = NOW()
        """
        self.db.execute_query(
            query,
            (organization_id, product_id, forecast_date,
             predicted_quantity, confidence_lower, confidence_upper,
             model_name, accuracy_score),
            fetch=False
        )
    
    def insert_anomaly_prediction(
        self,
        organization_id: str,
        predicted_time,
        entity_type: str,
        entity_id: str,
        anomaly_type: str,
        severity: str,
        probability: float,
        description: str,
        recommended_actions: list,
        model_name: str
    ):
        """Insert anomaly prediction into database."""
        import json
        
        query = """
            INSERT INTO anomaly_predictions (
                organization_id, predicted_time, entity_type, entity_id,
                anomaly_type, severity, probability, description,
                recommended_actions, model_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute_query(
            query,
            (organization_id, predicted_time, entity_type, entity_id,
             anomaly_type, severity, probability, description,
             json.dumps(recommended_actions), model_name),
            fetch=False
        )
