"""
Demand Forecasting Model
Uses Prophet for time-series forecasting with seasonality
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, List, Tuple, Optional
import joblib
from pathlib import Path
from loguru import logger
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """
    Demand forecasting using Facebook Prophet.
    Handles seasonal patterns, trends, and holidays.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize demand forecaster.
        
        Args:
            model_path: Path to save/load models
        """
        self.model_path = model_path or Path("./models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Prophet] = {}
        self.product_ids: List[str] = []
        
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for Prophet (requires 'ds' and 'y' columns).
        
        Args:
            df: DataFrame with 'time' and 'quantity' columns
            
        Returns:
            DataFrame formatted for Prophet
        """
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df['time']),
            'y': df['quantity'].astype(float)
        })
        
        # Remove any duplicates and sort
        prophet_df = prophet_df.drop_duplicates(subset=['ds']).sort_values('ds')
        
        return prophet_df
    
    def train(
        self,
        product_id: str,
        historical_data: pd.DataFrame,
        seasonality_mode: str = 'multiplicative',
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False
    ) -> Dict[str, float]:
        """
        Train Prophet model for a specific product.
        
        Args:
            product_id: Product identifier
            historical_data: Historical demand data
            seasonality_mode: 'additive' or 'multiplicative'
            yearly_seasonality: Include yearly patterns
            weekly_seasonality: Include weekly patterns
            daily_seasonality: Include daily patterns
            
        Returns:
            Training metrics (MAE, MAPE, etc.)
        """
        logger.info(f"Training demand forecaster for product: {product_id}")
        
        # Prepare data
        df = self.prepare_data(historical_data)
        
        if len(df) < 10:
            raise ValueError(f"Insufficient data for product {product_id}: {len(df)} records")
        
        # Initialize Prophet model
        model = Prophet(
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            interval_width=0.95,  # 95% confidence intervals
            changepoint_prior_scale=0.05  # Flexibility of trend
        )
        
        # Fit model
        model.fit(df)
        
        # Store model
        self.models[product_id] = model
        self.product_ids.append(product_id)
        
        # Evaluate on training data (last 20% for validation)
        split_point = int(len(df) * 0.8)
        train_df = df[:split_point]
        test_df = df[split_point:]
        
        if len(test_df) > 0:
            forecast = model.predict(test_df[['ds']])
            metrics = self._calculate_metrics(test_df['y'], forecast['yhat'])
            logger.info(f"Training metrics for {product_id}: MAE={metrics['mae']:.2f}, MAPE={metrics['mape']:.2f}%")
        else:
            metrics = {'mae': 0, 'mape': 0, 'rmse': 0}
        
        return metrics
    
    def predict(
        self,
        product_id: str,
        periods: int = 30,
        freq: str = 'D'
    ) -> pd.DataFrame:
        """
        Generate demand forecast for a product.
        
        Args:
            product_id: Product identifier
            periods: Number of periods to forecast
            freq: Frequency ('D' for daily, 'W' for weekly)
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if product_id not in self.models:
            raise ValueError(f"No trained model found for product: {product_id}")
        
        model = self.models[product_id]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq=freq)
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Extract relevant columns
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        result.columns = ['date', 'predicted_quantity', 'lower_bound', 'upper_bound']
        
        # Ensure non-negative predictions
        result['predicted_quantity'] = result['predicted_quantity'].clip(lower=0)
        result['lower_bound'] = result['lower_bound'].clip(lower=0)
        result['upper_bound'] = result['upper_bound'].clip(lower=0)
        
        logger.info(f"Generated {periods}-period forecast for {product_id}")
        
        return result
    
    def predict_multiple(
        self,
        product_ids: List[str],
        periods: int = 30,
        freq: str = 'D'
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate forecasts for multiple products.
        
        Args:
            product_ids: List of product identifiers
            periods: Number of periods to forecast
            freq: Frequency
            
        Returns:
            Dictionary mapping product_id to forecast DataFrame
        """
        forecasts = {}
        
        for product_id in product_ids:
            try:
                forecasts[product_id] = self.predict(product_id, periods, freq)
            except Exception as e:
                logger.error(f"Error forecasting for {product_id}: {e}")
                
        return forecasts
    
    def _calculate_metrics(self, actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
        """Calculate forecast accuracy metrics."""
        mae = np.mean(np.abs(actual - predicted))
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        return {
            'mae': float(mae),
            'mape': float(mape),
            'rmse': float(rmse)
        }
    
    def save_model(self, product_id: str, filename: Optional[str] = None):
        """Save trained model to disk."""
        if product_id not in self.models:
            raise ValueError(f"No model found for product: {product_id}")
        
        filename = filename or f"demand_forecaster_{product_id}.pkl"
        filepath = self.model_path / filename
        
        joblib.dump(self.models[product_id], filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, product_id: str, filename: Optional[str] = None):
        """Load trained model from disk."""
        filename = filename or f"demand_forecaster_{product_id}.pkl"
        filepath = self.model_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        self.models[product_id] = joblib.load(filepath)
        if product_id not in self.product_ids:
            self.product_ids.append(product_id)
        
        logger.info(f"Model loaded from {filepath}")
    
    def save_all_models(self):
        """Save all trained models."""
        for product_id in self.models.keys():
            self.save_model(product_id)
    
    def get_feature_importance(self, product_id: str) -> pd.DataFrame:
        """
        Get seasonality components for a product.
        
        Returns:
            DataFrame with seasonality strengths
        """
        if product_id not in self.models:
            raise ValueError(f"No model found for product: {product_id}")
        
        model = self.models[product_id]
        
        # Get seasonality information
        seasonalities = []
        
        if model.yearly_seasonality:
            seasonalities.append({'component': 'yearly', 'enabled': True})
        if model.weekly_seasonality:
            seasonalities.append({'component': 'weekly', 'enabled': True})
        if model.daily_seasonality:
            seasonalities.append({'component': 'daily', 'enabled': True})
            
        return pd.DataFrame(seasonalities)


# Example usage for hackathon demo
if __name__ == "__main__":
    # This would be run during model training phase
    
    # Sample data structure (replace with actual DB query)
    sample_data = pd.DataFrame({
        'time': pd.date_range(start='2024-01-01', periods=90, freq='D'),
        'quantity': np.random.randint(100, 200, 90) + 
                   10 * np.sin(np.linspace(0, 4*np.pi, 90))  # Seasonal pattern
    })
    
    # Initialize and train
    forecaster = DemandForecaster()
    
    print("Training demand forecaster...")
    metrics = forecaster.train('PROD-A-001', sample_data)
    print(f"Training complete. Metrics: {metrics}")
    
    # Generate forecast
    print("\nGenerating 30-day forecast...")
    forecast = forecaster.predict('PROD-A-001', periods=30)
    print(forecast.head())
    
    # Save model
    forecaster.save_model('PROD-A-001')
    print("\nModel saved successfully!")
