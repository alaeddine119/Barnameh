"""
PostgreSQL Database Connection and Query Utilities
For Smart Operations Platform
"""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages PostgreSQL connections and provides utility methods
    for common database operations.
    """
    
    def __init__(self, database_url: Optional[str] = None, min_conn: int = 1, max_conn: int = 10):
        """
        Initialize database connection pool.
        
        Args:
            database_url: PostgreSQL connection string
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://barnameh_user:barnameh_password@localhost:5432/barnameh_ops'
        )
        
        try:
            self.pool = ThreadedConnectionPool(
                min_conn,
                max_conn,
                self.database_url
            )
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool.
        Automatically returns connection to pool after use.
        """
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[List[Dict]]:
        """
        Execute a SQL query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            fetch: Whether to fetch and return results
            
        Returns:
            List of dictionaries (rows) if fetch=True, None otherwise
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return [dict(row) for row in cursor.fetchall()]
                return None
    
    def execute_many(self, query: str, data: List[tuple]) -> int:
        """
        Execute a query multiple times with different parameters.
        Useful for bulk inserts.
        
        Args:
            query: SQL query string with placeholders
            data: List of tuples with parameters
            
        Returns:
            Number of rows affected
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, query, data)
                return cursor.rowcount
    
    def close(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")


class OperationalDataQueries:
    """
    Pre-built queries for common operational data access patterns.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    # ==================== DEMAND & FORECASTING ====================
    
    def get_demand_history(
        self,
        organization_id: str,
        product_id: str,
        days: int = 90
    ) -> List[Dict]:
        """Get historical demand data for a product."""
        query = """
            SELECT time, quantity, revenue, channel
            FROM demand_history
            WHERE organization_id = %s
              AND product_id = %s
              AND time >= NOW() - INTERVAL '%s days'
            ORDER BY time ASC
        """
        return self.db.execute_query(query, (organization_id, product_id, days))
    
    def get_demand_forecasts(
        self,
        organization_id: str,
        product_id: str,
        days_ahead: int = 30
    ) -> List[Dict]:
        """Get demand forecasts for a product."""
        query = """
            SELECT forecast_date, predicted_quantity, 
                   confidence_lower, confidence_upper,
                   model_name, accuracy_score
            FROM demand_forecasts
            WHERE organization_id = %s
              AND product_id = %s
              AND forecast_date >= CURRENT_DATE
              AND forecast_date <= CURRENT_DATE + INTERVAL '%s days'
            ORDER BY forecast_date ASC
        """
        return self.db.execute_query(query, (organization_id, product_id, days_ahead))
    
    def insert_demand_forecast(
        self,
        organization_id: str,
        location_id: str,
        product_id: str,
        forecast_date: datetime,
        predicted_quantity: float,
        confidence_lower: float,
        confidence_upper: float,
        model_name: str,
        accuracy_score: float
    ) -> None:
        """Insert a new demand forecast."""
        query = """
            INSERT INTO demand_forecasts (
                organization_id, location_id, product_id, forecast_date,
                predicted_quantity, confidence_lower, confidence_upper,
                model_name, accuracy_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (organization_id, location_id, product_id, forecast_date, model_name)
            DO UPDATE SET
                predicted_quantity = EXCLUDED.predicted_quantity,
                confidence_lower = EXCLUDED.confidence_lower,
                confidence_upper = EXCLUDED.confidence_upper,
                accuracy_score = EXCLUDED.accuracy_score,
                created_at = NOW()
        """
        self.db.execute_query(
            query,
            (organization_id, location_id, product_id, forecast_date,
             predicted_quantity, confidence_lower, confidence_upper,
             model_name, accuracy_score),
            fetch=False
        )
    
    # ==================== RESOURCE MONITORING ====================
    
    def get_resource_metrics(
        self,
        resource_id: str,
        hours: int = 24
    ) -> List[Dict]:
        """Get resource performance metrics."""
        query = """
            SELECT time, utilization_rate, throughput, efficiency_score,
                   downtime_minutes, error_count, energy_consumption
            FROM resource_metrics
            WHERE resource_id = %s
              AND time >= NOW() - INTERVAL '%s hours'
            ORDER BY time DESC
        """
        return self.db.execute_query(query, (resource_id, hours))
    
    def get_resource_utilization_summary(
        self,
        organization_id: str,
        days: int = 7
    ) -> List[Dict]:
        """Get resource utilization summary."""
        query = """
            SELECT r.name, r.type,
                   AVG(rm.utilization_rate) as avg_utilization,
                   AVG(rm.efficiency_score) as avg_efficiency,
                   SUM(rm.downtime_minutes) as total_downtime,
                   SUM(rm.error_count) as total_errors
            FROM resource_metrics rm
            JOIN resources r ON rm.resource_id = r.id
            WHERE r.organization_id = %s
              AND rm.time >= NOW() - INTERVAL '%s days'
            GROUP BY r.id, r.name, r.type
            ORDER BY avg_utilization DESC
        """
        return self.db.execute_query(query, (organization_id, days))
    
    # ==================== EMPLOYEE & SCHEDULING ====================
    
    def get_employee_attendance_rate(
        self,
        organization_id: str,
        days: int = 30
    ) -> List[Dict]:
        """Get employee attendance statistics."""
        query = """
            SELECT e.employee_code, e.first_name, e.last_name,
                   COUNT(*) FILTER (WHERE ea.status = 'present') as present_days,
                   COUNT(*) FILTER (WHERE ea.status = 'absent') as absent_days,
                   COUNT(*) as total_days,
                   ROUND(100.0 * COUNT(*) FILTER (WHERE ea.status = 'present') / COUNT(*), 2) as attendance_rate
            FROM employee_attendance ea
            JOIN employees e ON ea.employee_id = e.id
            WHERE e.organization_id = %s
              AND ea.time >= NOW() - INTERVAL '%s days'
            GROUP BY e.id, e.employee_code, e.first_name, e.last_name
            ORDER BY attendance_rate ASC
        """
        return self.db.execute_query(query, (organization_id, days))
    
    def get_shifts_needing_assignment(
        self,
        organization_id: str,
        days_ahead: int = 7
    ) -> List[Dict]:
        """Get shifts that need employee assignments."""
        query = """
            SELECT s.id, s.shift_date, s.shift_type, s.start_time, s.end_time,
                   s.required_employees, s.required_skills,
                   COUNT(sa.employee_id) as assigned_employees,
                   (s.required_employees - COUNT(sa.employee_id)) as still_needed
            FROM shifts s
            LEFT JOIN shift_assignments sa ON s.id = sa.shift_id
            WHERE s.organization_id = %s
              AND s.shift_date >= CURRENT_DATE
              AND s.shift_date <= CURRENT_DATE + INTERVAL '%s days'
              AND s.status = 'scheduled'
            GROUP BY s.id
            HAVING COUNT(sa.employee_id) < s.required_employees
            ORDER BY s.shift_date, s.start_time
        """
        return self.db.execute_query(query, (organization_id, days_ahead))
    
    # ==================== ANOMALIES & ALERTS ====================
    
    def get_active_anomaly_predictions(
        self,
        organization_id: str,
        hours_ahead: int = 48
    ) -> List[Dict]:
        """Get active anomaly predictions."""
        query = """
            SELECT ap.*, 
                   CASE 
                       WHEN ap.entity_type = 'resource' THEN r.name
                       WHEN ap.entity_type = 'location' THEN l.name
                       ELSE NULL
                   END as entity_name
            FROM anomaly_predictions ap
            LEFT JOIN resources r ON ap.entity_type = 'resource' AND ap.entity_id = r.id
            LEFT JOIN locations l ON ap.entity_type = 'location' AND ap.entity_id = l.id
            WHERE ap.organization_id = %s
              AND ap.status = 'active'
              AND ap.predicted_time <= NOW() + INTERVAL '%s hours'
            ORDER BY ap.severity DESC, ap.probability DESC
        """
        return self.db.execute_query(query, (organization_id, hours_ahead))
    
    def insert_anomaly_prediction(
        self,
        organization_id: str,
        predicted_time: datetime,
        entity_type: str,
        entity_id: str,
        anomaly_type: str,
        severity: str,
        probability: float,
        description: str,
        recommended_actions: List[str],
        model_name: str
    ) -> None:
        """Insert a new anomaly prediction."""
        query = """
            INSERT INTO anomaly_predictions (
                organization_id, predicted_time, entity_type, entity_id,
                anomaly_type, severity, probability, description,
                recommended_actions, model_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        import json
        self.db.execute_query(
            query,
            (organization_id, predicted_time, entity_type, entity_id,
             anomaly_type, severity, probability, description,
             json.dumps(recommended_actions), model_name),
            fetch=False
        )
    
    def get_active_alerts(self, organization_id: str) -> List[Dict]:
        """Get all active alerts."""
        query = """
            SELECT *
            FROM alerts
            WHERE organization_id = %s
              AND status = 'active'
            ORDER BY severity DESC, created_at DESC
        """
        return self.db.execute_query(query, (organization_id,))
    
    # ==================== ANALYTICS & DASHBOARDS ====================
    
    def get_kpi_summary(self, organization_id: str, days: int = 7) -> Dict:
        """Get overall KPI summary for dashboard."""
        queries = {
            'total_production': """
                SELECT COALESCE(SUM(quantity), 0) as value
                FROM operational_events
                WHERE organization_id = %s
                  AND event_type = 'production'
                  AND time >= NOW() - INTERVAL '%s days'
            """,
            'avg_utilization': """
                SELECT ROUND(AVG(rm.utilization_rate), 2) as value
                FROM resource_metrics rm
                JOIN resources r ON rm.resource_id = r.id
                WHERE r.organization_id = %s
                  AND rm.time >= NOW() - INTERVAL '%s days'
            """,
            'total_downtime': """
                SELECT COALESCE(SUM(duration_minutes), 0) as value
                FROM operational_events
                WHERE organization_id = %s
                  AND event_type = 'downtime'
                  AND time >= NOW() - INTERVAL '%s days'
            """,
            'avg_attendance': """
                SELECT ROUND(AVG(CASE WHEN ea.status = 'present' THEN 100.0 ELSE 0 END), 2) as value
                FROM employee_attendance ea
                JOIN employees e ON ea.employee_id = e.id
                WHERE e.organization_id = %s
                  AND ea.time >= NOW() - INTERVAL '%s days'
            """
        }
        
        results = {}
        for key, query in queries.items():
            result = self.db.execute_query(query, (organization_id, days))
            results[key] = result[0]['value'] if result else 0
        
        return results


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Initialize database manager
    db = DatabaseManager()
    queries = OperationalDataQueries(db)
    
    # Example: Get demand history
    org_id = "11111111-1111-1111-1111-111111111111"
    product_id = "PROD-A-001"
    
    print("📊 Demand History:")
    demand = queries.get_demand_history(org_id, product_id, days=30)
    print(f"Found {len(demand)} records")
    
    print("\n🔮 Demand Forecasts:")
    forecasts = queries.get_demand_forecasts(org_id, product_id)
    print(f"Found {len(forecasts)} forecasts")
    
    print("\n⚡ Resource Utilization Summary:")
    utilization = queries.get_resource_utilization_summary(org_id)
    for resource in utilization:
        print(f"  {resource['name']}: {resource['avg_utilization']:.1f}% utilization")
    
    print("\n🚨 Active Anomaly Predictions:")
    anomalies = queries.get_active_anomaly_predictions(org_id)
    for anomaly in anomalies:
        print(f"  [{anomaly['severity'].upper()}] {anomaly['anomaly_type']} - {anomaly['description']}")
    
    print("\n📈 KPI Summary:")
    kpis = queries.get_kpi_summary(org_id)
    for key, value in kpis.items():
        print(f"  {key}: {value}")
    
    # Clean up
    db.close()
    print("\n✅ Database connection closed")
