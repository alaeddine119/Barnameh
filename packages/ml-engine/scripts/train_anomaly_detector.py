"""
Training script for anomaly detection model
Trains Isolation Forest on resource metrics
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.append(str(Path(__file__).parent.parent))

from models.anomaly_detector import AnomalyDetector
from database.db_manager import DatabaseManager, OperationalQueries
from loguru import logger

def main():
    """Train anomaly detection model."""
    
    logger.info("🚀 Starting anomaly detector training...")
    
    # Initialize components
    db = DatabaseManager()
    queries = OperationalQueries(db)
    detector = AnomalyDetector(contamination=0.05)
    
    # Configuration
    ORG_ID = "11111111-1111-1111-1111-111111111111"
    TRAINING_DAYS = 30
    
    try:
        logger.info(f"\n📊 Fetching {TRAINING_DAYS} days of resource metrics...")
        
        # Fetch historical metrics
        metrics = queries.get_all_resource_metrics(
            ORG_ID,
            days=TRAINING_DAYS
        )
        
        if len(metrics) < 100:
            logger.error(f"❌ Insufficient data: {len(metrics)} records (need at least 100)")
            return
        
        logger.info(f"   Loaded {len(metrics)} records")
        logger.info(f"   Features: {list(metrics.columns)}")
        
        # Train model
        logger.info(f"\n🤖 Training Isolation Forest...")
        stats = detector.train(metrics)
        
        logger.info(f"\n   ✅ Training complete!")
        logger.info(f"   📊 Total samples: {stats['total_samples']}")
        logger.info(f"   ⚠️ Anomalies detected: {stats['anomaly_count']} ({stats['anomaly_rate']:.2%})")
        logger.info(f"   📈 Features used: {stats['features_used']}")
        
        # Test detection on recent data
        logger.info(f"\n🔍 Testing on recent data...")
        test_data = metrics.tail(100)
        results = detector.predict(test_data)
        
        anomalies = results[results['is_anomaly']]
        logger.info(f"   Found {len(anomalies)} anomalies in test set")
        
        if len(anomalies) > 0:
            logger.info(f"\n   Sample anomalies:")
            for idx, row in anomalies.head(3).iterrows():
                logger.info(f"   - Type: {row['anomaly_type']}, Severity: {row.get('severity', 'N/A')}, Score: {row.get('anomaly_score', 0):.3f}")
        
        # Save model
        detector.save_model()
        logger.info(f"\n   💾 Model saved to ./models/")
        
    except Exception as e:
        logger.error(f"   ❌ Error during training: {e}")
        raise
    
    logger.info("\n✨ Training complete!")
    
    # Cleanup
    db.close()


if __name__ == "__main__":
    main()
