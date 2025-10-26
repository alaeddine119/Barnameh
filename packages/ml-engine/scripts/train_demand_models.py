"""
Training script for demand forecasting models
Trains Prophet models for all products with historical data
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.append(str(Path(__file__).parent.parent))

from models.demand_forecaster import DemandForecaster
from database.db_manager import DatabaseManager, OperationalQueries
from loguru import logger
import pandas as pd

def main():
    """Train demand forecasting models."""
    
    logger.info("🚀 Starting demand forecaster training...")
    
    # Initialize components
    db = DatabaseManager()
    queries = OperationalQueries(db)
    forecaster = DemandForecaster()
    
    # Configuration
    ORG_ID = "11111111-1111-1111-1111-111111111111"
    PRODUCTS = ["PROD-A-001", "PROD-B-002"]
    TRAINING_DAYS = 90
    
    # Train models for each product
    for product_id in PRODUCTS:
        try:
            logger.info(f"\n📊 Training model for {product_id}...")
            
            # Fetch historical data
            historical_data = queries.get_demand_history(
                ORG_ID,
                product_id,
                days=TRAINING_DAYS
            )
            
            if len(historical_data) < 10:
                logger.warning(f"⚠️ Insufficient data for {product_id}: {len(historical_data)} records")
                continue
            
            logger.info(f"   Loaded {len(historical_data)} records ({TRAINING_DAYS} days)")
            
            # Train model
            metrics = forecaster.train(product_id, historical_data)
            
            logger.info(f"   ✅ Training complete!")
            logger.info(f"   📈 MAE: {metrics['mae']:.2f}")
            logger.info(f"   📈 MAPE: {metrics['mape']:.2f}%")
            logger.info(f"   📈 RMSE: {metrics['rmse']:.2f}")
            
            # Save model
            forecaster.save_model(product_id)
            logger.info(f"   💾 Model saved")
            
            # Generate sample forecast
            forecast = forecaster.predict(product_id, periods=7)
            logger.info(f"\n   🔮 Sample 7-day forecast:")
            logger.info(f"\n{forecast.to_string(index=False)}\n")
            
        except Exception as e:
            logger.error(f"   ❌ Error training {product_id}: {e}")
            continue
    
    # Save all models
    forecaster.save_all_models()
    
    logger.info("\n✨ Training complete! Models saved to ./models/")
    
    # Cleanup
    db.close()


if __name__ == "__main__":
    main()
