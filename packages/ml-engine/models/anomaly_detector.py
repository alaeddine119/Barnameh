"""
Anomaly Detection Model
Uses Isolation Forest for detecting bottlenecks and failures
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import joblib
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta


class AnomalyDetector:
    """
    Anomaly detection for operational metrics.
    Detects bottlenecks, failures, and unusual patterns.
    """
    
    def __init__(
        self,
        contamination: float = 0.1,
        model_path: Optional[Path] = None
    ):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies (0.0 to 0.5)
            model_path: Path to save/load models
        """
        self.contamination = contamination
        self.model_path = model_path or Path("./models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.thresholds: Dict[str, float] = {}
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for anomaly detection from operational metrics.
        
        Args:
            df: DataFrame with operational metrics
            
        Returns:
            DataFrame with engineered features
        """
        features = pd.DataFrame()
        
        # Basic metrics
        if 'utilization_rate' in df.columns:
            features['utilization_rate'] = df['utilization_rate']
        
        if 'throughput' in df.columns:
            features['throughput'] = df['throughput']
            
        if 'efficiency_score' in df.columns:
            features['efficiency_score'] = df['efficiency_score']
        
        if 'downtime_minutes' in df.columns:
            features['downtime_minutes'] = df['downtime_minutes']
        
        if 'error_count' in df.columns:
            features['error_count'] = df['error_count']
        
        if 'energy_consumption' in df.columns:
            features['energy_consumption'] = df['energy_consumption']
        
        # Time-based features (if time column exists)
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            features['hour'] = df['time'].dt.hour
            features['day_of_week'] = df['time'].dt.dayofweek
            features['is_weekend'] = (df['time'].dt.dayofweek >= 5).astype(int)
        
        # Derived features
        if 'utilization_rate' in features.columns and 'efficiency_score' in features.columns:
            features['util_efficiency_ratio'] = features['utilization_rate'] / (features['efficiency_score'] + 1e-6)
        
        if 'throughput' in features.columns:
            # Rate of change in throughput (requires sorting by time)
            if 'time' in df.columns:
                features['throughput_change'] = features['throughput'].diff().fillna(0)
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
    
    def train(
        self,
        training_data: pd.DataFrame,
        feature_columns: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Train Isolation Forest on normal operational data.
        
        Args:
            training_data: Historical operational metrics
            feature_columns: Specific columns to use (None = auto-detect)
            
        Returns:
            Training statistics
        """
        logger.info("Training anomaly detector...")
        
        # Prepare features
        features_df = self.prepare_features(training_data)
        
        if feature_columns:
            features_df = features_df[feature_columns]
        
        self.feature_names = features_df.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features_df)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            max_features=1.0,
            bootstrap=False
        )
        
        self.model.fit(X_scaled)
        
        # Calculate thresholds for each feature
        for col in features_df.columns:
            self.thresholds[col] = {
                'mean': float(features_df[col].mean()),
                'std': float(features_df[col].std()),
                'q95': float(features_df[col].quantile(0.95)),
                'q99': float(features_df[col].quantile(0.99))
            }
        
        # Evaluate on training data
        predictions = self.model.predict(X_scaled)
        anomaly_count = np.sum(predictions == -1)
        anomaly_rate = anomaly_count / len(predictions)
        
        logger.info(f"Training complete. Detected {anomaly_count} anomalies ({anomaly_rate:.2%})")
        
        return {
            'total_samples': len(training_data),
            'anomaly_count': int(anomaly_count),
            'anomaly_rate': float(anomaly_rate),
            'features_used': len(self.feature_names)
        }
    
    def predict(
        self,
        data: pd.DataFrame,
        return_scores: bool = True
    ) -> pd.DataFrame:
        """
        Detect anomalies in operational data.
        
        Args:
            data: Operational metrics to analyze
            return_scores: Include anomaly scores
            
        Returns:
            DataFrame with anomaly predictions and scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Prepare features
        features_df = self.prepare_features(data)
        features_df = features_df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(features_df)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        
        # Prepare results
        results = pd.DataFrame({
            'is_anomaly': predictions == -1
        })
        
        if return_scores:
            # Get anomaly scores (lower = more anomalous)
            scores = self.model.score_samples(X_scaled)
            # Convert to 0-1 probability scale (higher = more anomalous)
            results['anomaly_score'] = 1 / (1 + np.exp(scores))
            results['anomaly_score'] = results['anomaly_score'].clip(0, 1)
        
        # Classify anomaly type
        results['anomaly_type'] = self._classify_anomaly_type(features_df, results['is_anomaly'])
        
        # Severity
        if return_scores:
            results['severity'] = results['anomaly_score'].apply(self._score_to_severity)
        
        return results
    
    def predict_future_anomalies(
        self,
        historical_data: pd.DataFrame,
        forecast_data: pd.DataFrame,
        hours_ahead: int = 24
    ) -> pd.DataFrame:
        """
        Predict potential anomalies based on forecasted metrics.
        
        Args:
            historical_data: Historical operational metrics
            forecast_data: Forecasted metrics (e.g., predicted utilization)
            hours_ahead: How far to look ahead
            
        Returns:
            DataFrame with predicted anomalies and recommendations
        """
        # Detect anomalies in forecast
        anomaly_results = self.predict(forecast_data)
        
        # Add context
        anomaly_results['predicted_time'] = pd.date_range(
            start=datetime.now(),
            periods=len(anomaly_results),
            freq='h'
        )
        
        # Filter to only anomalies
        anomalies = anomaly_results[anomaly_results['is_anomaly']].copy()
        
        # Add recommendations
        anomalies['recommendations'] = anomalies.apply(
            lambda row: self._generate_recommendations(row['anomaly_type'], row.get('severity', 'medium')),
            axis=1
        )
        
        return anomalies
    
    def _classify_anomaly_type(
        self,
        features: pd.DataFrame,
        is_anomaly: pd.Series
    ) -> List[str]:
        """
        Classify the type of anomaly based on feature values.
        """
        anomaly_types = []
        
        for idx, row in features.iterrows():
            if not is_anomaly.iloc[idx]:
                anomaly_types.append('normal')
                continue
            
            # Bottleneck: High utilization + Low efficiency
            if 'utilization_rate' in row and 'efficiency_score' in row:
                if row['utilization_rate'] > self.thresholds.get('utilization_rate', {}).get('q95', 90):
                    if row['efficiency_score'] < self.thresholds.get('efficiency_score', {}).get('mean', 80):
                        anomaly_types.append('bottleneck')
                        continue
            
            # Failure: High downtime or errors
            if 'downtime_minutes' in row:
                if row['downtime_minutes'] > self.thresholds.get('downtime_minutes', {}).get('q95', 30):
                    anomaly_types.append('failure')
                    continue
            
            if 'error_count' in row:
                if row['error_count'] > self.thresholds.get('error_count', {}).get('q95', 5):
                    anomaly_types.append('failure')
                    continue
            
            # Performance degradation: Low efficiency
            if 'efficiency_score' in row:
                if row['efficiency_score'] < self.thresholds.get('efficiency_score', {}).get('mean', 80) * 0.8:
                    anomaly_types.append('performance_degradation')
                    continue
            
            # Default
            anomaly_types.append('unknown')
        
        return anomaly_types
    
    def _score_to_severity(self, score: float) -> str:
        """Convert anomaly score to severity level."""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, anomaly_type: str, severity: str) -> List[str]:
        """Generate action recommendations based on anomaly type."""
        recommendations = {
            'bottleneck': [
                "Consider reassigning resources to this operation",
                "Review current workload distribution",
                "Check for upstream delays",
                "Schedule overtime if critical"
            ],
            'failure': [
                "Schedule immediate maintenance check",
                "Verify all systems are operational",
                "Prepare backup equipment",
                "Alert maintenance team"
            ],
            'performance_degradation': [
                "Review recent configuration changes",
                "Check for resource constraints",
                "Monitor for gradual deterioration",
                "Consider preventive maintenance"
            ],
            'unknown': [
                "Investigate anomaly pattern",
                "Review operational logs",
                "Consult with operations team"
            ]
        }
        
        return recommendations.get(anomaly_type, recommendations['unknown'])
    
    def save_model(self, filename: str = "anomaly_detector.pkl"):
        """Save trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train first.")
        
        filepath = self.model_path / filename
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'thresholds': self.thresholds,
            'contamination': self.contamination
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = "anomaly_detector.pkl"):
        """Load trained model from disk."""
        filepath = self.model_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.thresholds = model_data['thresholds']
        self.contamination = model_data['contamination']
        
        logger.info(f"Model loaded from {filepath}")


# Example usage for hackathon demo
if __name__ == "__main__":
    # Sample operational data
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'time': pd.date_range(start='2024-01-01', periods=n_samples, freq='h'),
        'utilization_rate': np.random.normal(75, 10, n_samples).clip(0, 100),
        'throughput': np.random.normal(50, 8, n_samples).clip(0, None),
        'efficiency_score': np.random.normal(85, 5, n_samples).clip(0, 100),
        'downtime_minutes': np.random.exponential(5, n_samples),
        'error_count': np.random.poisson(1, n_samples),
        'energy_consumption': np.random.normal(20, 3, n_samples).clip(0, None)
    })
    
    # Add some anomalies
    anomaly_indices = np.random.choice(n_samples, size=50, replace=False)
    sample_data.loc[anomaly_indices, 'utilization_rate'] = 95
    sample_data.loc[anomaly_indices, 'efficiency_score'] = 60
    sample_data.loc[anomaly_indices[::2], 'downtime_minutes'] = 45
    
    # Train detector
    detector = AnomalyDetector(contamination=0.05)
    
    print("Training anomaly detector...")
    stats = detector.train(sample_data)
    print(f"Training complete: {stats}")
    
    # Test detection
    print("\nDetecting anomalies...")
    results = detector.predict(sample_data.tail(100))
    
    anomalies = results[results['is_anomaly']]
    print(f"\nFound {len(anomalies)} anomalies")
    print("\nSample anomalies:")
    print(anomalies.head())
    
    # Save model
    detector.save_model()
    print("\nModel saved successfully!")
