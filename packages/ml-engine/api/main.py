"""
FastAPI Backend for ML Prediction Engine
Serves demand forecasts and anomaly predictions via REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import sys
from pathlib import Path
import os
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Allow importing the optimization engine (sibling package)
sys.path.append(str(Path(__file__).parent.parent.parent / 'optimization-engine'))
try:
    from recommendation_engine import RecommendationEngine, MLPrediction, OptimizationResult as OptResult
    OPT_ENGINE_AVAILABLE = True
except Exception:
    OPT_ENGINE_AVAILABLE = False

from models.demand_forecaster import DemandForecaster
from models.anomaly_detector import AnomalyDetector
from database.db_manager import DatabaseManager, OperationalQueries

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logger.add("logs/api_{time}.log", rotation="1 day", retention="7 days")

# Initialize FastAPI
app = FastAPI(
    title="Smart Operations ML API",
    description="AI-powered operational efficiency prediction engine",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
demand_forecaster = DemandForecaster()
anomaly_detector = AnomalyDetector()

# Load pre-trained models (if available)
try:
    demand_forecaster.load_model('PROD-A-001')
    demand_forecaster.load_model('PROD-B-002')
    logger.info("Loaded pre-trained demand models")
except:
    logger.warning("No pre-trained demand models found")

try:
    anomaly_detector.load_model()
    logger.info("Loaded pre-trained anomaly detector")
except:
    logger.warning("No pre-trained anomaly detector found")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ForecastRequest(BaseModel):
    organization_id: str = Field(..., description="Organization UUID")
    product_id: str = Field(..., description="Product SKU")
    periods: int = Field(30, description="Number of days to forecast", ge=1, le=90)
    
class ForecastResponse(BaseModel):
    product_id: str
    forecast_date: date
    predicted_quantity: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95
    model_name: str = "Prophet"

class AnomalyRequest(BaseModel):
    organization_id: str
    resource_id: Optional[str] = None
    hours_ahead: int = Field(48, ge=1, le=168)

class AnomalyPrediction(BaseModel):
    predicted_time: datetime
    entity_type: str
    entity_id: str
    anomaly_type: str
    severity: str
    probability: float
    description: str
    recommendations: List[str]

class TrainingRequest(BaseModel):
    organization_id: str
    model_type: str  # 'demand' or 'anomaly'
    product_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    models_loaded: Dict[str, bool]
    database_connected: bool

class KPISummary(BaseModel):
    total_production: float
    avg_utilization: float
    total_downtime: float
    avg_attendance: float
    period_days: int


class RecommendationRequest(BaseModel):
    organization_id: str
    question: Optional[str] = "How do I optimize operations for the next month?"
    product_id: Optional[str] = None


class RecommendationResponse(BaseModel):
    summary: str
    priority: str
    actions: List[str]
    rationale: str
    estimated_impact: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "Smart Operations ML API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns status of models and database connection.
    """
    try:
        db_connected = db_manager.check_connection()
    except:
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        timestamp=datetime.now(),
        models_loaded={
            "demand_forecaster": len(demand_forecaster.models) > 0,
            "anomaly_detector": anomaly_detector.model is not None
        },
        database_connected=db_connected
    )


@app.post("/api/v1/forecast/demand", response_model=List[ForecastResponse], tags=["Forecasting"])
async def forecast_demand(request: ForecastRequest):
    """
    Generate demand forecast for a product.
    
    Returns predictions for the specified number of periods with confidence intervals.
    """
    try:
        logger.info(f"Forecasting demand for {request.product_id}")
        
        # Check if model exists, otherwise train
        if request.product_id not in demand_forecaster.models:
            logger.info(f"Model not found for {request.product_id}, training...")
            
            # Fetch historical data
            queries = OperationalQueries(db_manager)
            historical_data = queries.get_demand_history(
                request.organization_id,
                request.product_id,
                days=90
            )
            
            if len(historical_data) < 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient historical data for {request.product_id}"
                )
            
            # Train model
            demand_forecaster.train(request.product_id, historical_data)
            demand_forecaster.save_model(request.product_id)
        
        # Generate forecast
        forecast_df = demand_forecaster.predict(request.product_id, periods=request.periods)
        
        # Convert to response format
        forecasts = []
        for _, row in forecast_df.iterrows():
            forecasts.append(ForecastResponse(
                product_id=request.product_id,
                forecast_date=row['date'].date(),
                predicted_quantity=float(row['predicted_quantity']),
                lower_bound=float(row['lower_bound']),
                upper_bound=float(row['upper_bound'])
            ))
        
        # Store forecasts in database
        queries = OperationalQueries(db_manager)
        for forecast in forecasts:
            queries.insert_demand_forecast(
                organization_id=request.organization_id,
                product_id=request.product_id,
                forecast_date=forecast.forecast_date,
                predicted_quantity=forecast.predicted_quantity,
                confidence_lower=forecast.lower_bound,
                confidence_upper=forecast.upper_bound,
                model_name="Prophet",
                accuracy_score=0.92  # Use actual validation score
            )
        
        logger.info(f"Generated {len(forecasts)} forecasts for {request.product_id}")
        
        return forecasts
        
    except Exception as e:
        logger.error(f"Error forecasting demand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/anomalies", response_model=List[AnomalyPrediction], tags=["Anomaly Detection"])
async def predict_anomalies(request: AnomalyRequest):
    """
    Predict potential anomalies (bottlenecks, failures) in the near future.
    
    Analyzes recent trends and forecasted metrics to identify risks.
    """
    try:
        logger.info(f"Predicting anomalies for org {request.organization_id}")
        
        # Check if model is trained
        if anomaly_detector.model is None:
            logger.info("Anomaly detector not trained, training now...")
            
            # Fetch historical metrics
            queries = OperationalQueries(db_manager)
            metrics = queries.get_all_resource_metrics(
                request.organization_id,
                days=30
            )
            
            if len(metrics) < 100:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient historical data for anomaly detection"
                )
            
            # Train detector
            anomaly_detector.train(metrics)
            anomaly_detector.save_model()
        
        # Get recent metrics and forecast
        queries = OperationalQueries(db_manager)
        recent_metrics = queries.get_all_resource_metrics(
            request.organization_id,
            days=7
        )
        
        # Detect anomalies in recent data
        results = anomaly_detector.predict(recent_metrics)
        
        # Simulate future predictions (in production, use forecasted metrics)
        future_anomalies = anomaly_detector.predict_future_anomalies(
            recent_metrics,
            recent_metrics.tail(request.hours_ahead),  # Simplified for demo
            hours_ahead=request.hours_ahead
        )
        
        # Convert to response format
        predictions = []
        for _, row in future_anomalies.iterrows():
            predictions.append(AnomalyPrediction(
                predicted_time=row['predicted_time'],
                entity_type='resource',
                entity_id=row.get('resource_id', 'unknown'),
                anomaly_type=row['anomaly_type'],
                severity=row.get('severity', 'medium'),
                probability=float(row['anomaly_score']),
                description=f"{row['anomaly_type'].replace('_', ' ').title()} predicted",
                recommendations=row['recommendations']
            ))
        
        # Store predictions in database
        for pred in predictions:
            queries.insert_anomaly_prediction(
                organization_id=request.organization_id,
                predicted_time=pred.predicted_time,
                entity_type=pred.entity_type,
                entity_id=pred.entity_id,
                anomaly_type=pred.anomaly_type,
                severity=pred.severity,
                probability=pred.probability,
                description=pred.description,
                recommended_actions=pred.recommendations,
                model_name="IsolationForest"
            )
        
        logger.info(f"Predicted {len(predictions)} anomalies")
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error predicting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/kpi/summary", response_model=KPISummary, tags=["Analytics"])
async def get_kpi_summary(
    organization_id: str,
    days: int = 7
):
    """
    Get KPI summary for the organization.
    
    Returns key metrics for dashboard display.
    """
    try:
        queries = OperationalQueries(db_manager)
        kpis = queries.get_kpi_summary(organization_id, days=days)
        
        return KPISummary(
            total_production=kpis.get('total_production', 0),
            avg_utilization=kpis.get('avg_utilization', 0),
            total_downtime=kpis.get('total_downtime', 0),
            avg_attendance=kpis.get('avg_attendance', 0),
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recommendations", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendation(request: RecommendationRequest):
    """Generate an intelligent recommendation combining ML + OR + LLM"""
    if not OPT_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Optimization/recommendation engine not available")

    try:
        queries = OperationalQueries(db_manager)

        # Fetch KPIs
        kpis = queries.get_kpi_summary(request.organization_id, days=30)

        # Fetch recent metrics for anomaly detection and utilization
        recent_metrics = queries.get_all_resource_metrics(request.organization_id, days=14)

        # Build a simple demand forecast summary
        if request.product_id:
            try:
                # If model exists, use it; otherwise, use simple heuristic
                if request.product_id in demand_forecaster.models:
                    df = demand_forecaster.predict(request.product_id, periods=30)
                    avg_q = float(df['predicted_quantity'].mean())
                    peak_q = float(df['predicted_quantity'].max())
                    trend = 'growing' if df['predicted_quantity'].iloc[-1] > df['predicted_quantity'].iloc[0] else 'stable'
                else:
                    # Fallback: average daily production scaled
                    avg_q = kpis.get('total_production', 0) / max(1, 30)
                    peak_q = avg_q * 1.35
                    trend = 'unknown'
            except Exception:
                avg_q = kpis.get('total_production', 0) / max(1, 30)
                peak_q = avg_q * 1.35
                trend = 'unknown'
        else:
            avg_q = float(kpis.get('total_production', 0)) / max(1, 30)
            peak_q = avg_q * 1.35
            trend = 'stable'

        demand_forecast = {
            'avg_quantity': float(avg_q),
            'peak_quantity': float(peak_q),
            'trend': trend,
            'confidence': 90
        }

        # Anomalies: attempt to use anomaly detector if available
        anomalies_list = []
        try:
            if anomaly_detector.model is not None:
                recent = recent_metrics
                preds = anomaly_detector.predict(recent)
                # quick map to expected structure
                for _, row in preds.head(5).iterrows():
                    anomalies_list.append({
                        'type': row.get('anomaly_type', 'unknown'),
                        'severity': row.get('severity', 'medium'),
                        'time': str(row.get('predicted_time', 'soon')),
                        'probability': float(row.get('anomaly_score', 0)),
                        'description': row.get('description', '')
                    })
        except Exception:
            anomalies_list = []

        # Build ml_predictions dataclass for recommendation engine
        ml_pred = MLPrediction(
            demand_forecast=demand_forecast,
            anomalies=anomalies_list,
            kpis={
                'total_production': float(kpis.get('total_production', 0)),
                'avg_utilization': float(kpis.get('avg_utilization', 0)),
                'total_downtime': float(kpis.get('total_downtime', 0)),
                'avg_attendance': float(kpis.get('avg_attendance', 0))
            }
        )

        # Build optimization result placeholders using recent metrics
        utilization = {}
        try:
            if not recent_metrics.empty:
                grouped = recent_metrics.groupby('resource_id').utilization_rate.mean()
                for rid, val in grouped.items():
                    utilization[rid] = float(val)
        except Exception:
            utilization = {}

        opt_res = OptResult(
            resource_allocation={
                'assignments': [],
                'avg_utilization': float(ml_pred.kpis.get('avg_utilization', 0)),
                'total_cost': 0,
                'utilization': utilization
            },
            schedule={
                'total_shifts': 0,
                'coverage_rate': 0,
                'total_cost': 0
            },
            capacity_plan={
                'current_capacity': float(kpis.get('total_production', 0)),
                'required_capacity': max(float(kpis.get('total_production', 0)), float(demand_forecast['peak_quantity'])),
                'capacity_gap': max(0, float(demand_forecast['peak_quantity']) - float(kpis.get('total_production', 0))),
                'investment': 0,
                'roi_months': 0
            }
        )

        # Initialize recommendation engine and call
        engine = RecommendationEngine(api_key=os.getenv('GROQ_API_KEY'))
        rec = engine.generate_recommendation(request.question or "How do I optimize operations?", ml_pred, opt_res, context={
            'organization_id': request.organization_id,
            'time_period': 'Next 30 days',
            'current_date': datetime.now().strftime('%Y-%m-%d')
        })

        return RecommendationResponse(
            summary=rec.summary,
            priority=rec.priority,
            actions=rec.actions,
            rationale=rec.rationale,
            estimated_impact=rec.estimated_impact
        )

    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/train/{model_type}", tags=["Training"])
async def train_model(
    model_type: str,
    request: TrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    Train or retrain a model.
    
    This is done in the background to avoid blocking the API.
    """
    if model_type not in ['demand', 'anomaly']:
        raise HTTPException(
            status_code=400,
            detail="model_type must be 'demand' or 'anomaly'"
        )
    
    def train_demand_model():
        try:
            queries = OperationalQueries(db_manager)
            historical_data = queries.get_demand_history(
                request.organization_id,
                request.product_id,
                days=90
            )
            
            demand_forecaster.train(request.product_id, historical_data)
            demand_forecaster.save_model(request.product_id)
            logger.info(f"Trained demand model for {request.product_id}")
            
        except Exception as e:
            logger.error(f"Error training demand model: {e}")
    
    def train_anomaly_model():
        try:
            queries = OperationalQueries(db_manager)
            metrics = queries.get_all_resource_metrics(
                request.organization_id,
                days=30
            )
            
            anomaly_detector.train(metrics)
            anomaly_detector.save_model()
            logger.info("Trained anomaly detector")
            
        except Exception as e:
            logger.error(f"Error training anomaly model: {e}")
    
    if model_type == 'demand':
        background_tasks.add_task(train_demand_model)
    else:
        background_tasks.add_task(train_anomaly_model)
    
    return {
        "message": f"Training {model_type} model in background",
        "status": "initiated"
    }


@app.get("/api/v1/models/status", tags=["Models"])
async def get_models_status():
    """Get status of all loaded models."""
    return {
        "demand_forecaster": {
            "loaded": len(demand_forecaster.models) > 0,
            "products": demand_forecaster.product_ids
        },
        "anomaly_detector": {
            "loaded": anomaly_detector.model is not None,
            "contamination": anomaly_detector.contamination if anomaly_detector.model else None
        }
    }


@app.get("/api/v1/analytics/resource-utilization", tags=["Analytics"])
async def get_resource_utilization(
    organization_id: str,
    days: int = 7
):
    """Get resource utilization data for visualization."""
    try:
        queries = OperationalQueries(db_manager)
        utilization_data = queries.get_resource_utilization_summary(organization_id, days=days)
        
        return {
            "resources": [
                {
                    "name": r['name'],
                    "type": r['type'],
                    "avg_utilization": float(r['avg_utilization']) if r['avg_utilization'] else 0.0,
                    "avg_efficiency": float(r['avg_efficiency']) if r['avg_efficiency'] else 0.0,
                    "total_downtime": float(r['total_downtime']) if r['total_downtime'] else 0.0,
                    "total_errors": int(r['total_errors']) if r['total_errors'] else 0
                }
                for r in utilization_data
            ],
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error getting resource utilization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/attendance-trends", tags=["Analytics"])
async def get_attendance_trends(
    organization_id: str,
    days: int = 30
):
    """Get employee attendance trends over time."""
    try:
        query = """
            SELECT DATE(ea.time) as date,
                   COUNT(*) FILTER (WHERE ea.status = 'present') as present_count,
                   COUNT(*) FILTER (WHERE ea.status = 'absent') as absent_count,
                   COUNT(*) as total_count,
                   ROUND(100.0 * COUNT(*) FILTER (WHERE ea.status = 'present') / COUNT(*), 2) as attendance_rate
            FROM employee_attendance ea
            JOIN employees e ON ea.employee_id = e.id
            WHERE e.organization_id = %s
              AND ea.time >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(ea.time)
            ORDER BY date ASC
        """
        
        results = db_manager.execute_query(query, (organization_id, days))
        
        return {
            "trends": [
                {
                    "date": str(r['date']),
                    "present_count": int(r['present_count']) if r['present_count'] else 0,
                    "absent_count": int(r['absent_count']) if r['absent_count'] else 0,
                    "total_count": int(r['total_count']) if r['total_count'] else 0,
                    "attendance_rate": float(r['attendance_rate']) if r['attendance_rate'] else 0.0
                }
                for r in results
            ],
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error getting attendance trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/production-revenue", tags=["Analytics"])
async def get_production_revenue(
    organization_id: str,
    days: int = 30
):
    """Get production and revenue trends over time."""
    try:
        query = """
            SELECT DATE(time) as date,
                   SUM(CASE WHEN event_type = 'production' THEN quantity ELSE 0 END) as production,
                   SUM(CASE WHEN event_type = 'production' THEN cost ELSE 0 END) as revenue,
                   SUM(CASE WHEN event_type = 'downtime' THEN duration_minutes ELSE 0 END) as downtime
            FROM operational_events
            WHERE organization_id = %s
              AND time >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(time)
            ORDER BY date ASC
        """
        
        results = db_manager.execute_query(query, (organization_id, days))
        
        return {
            "trends": [
                {
                    "date": str(r['date']),
                    "production": float(r['production']) if r['production'] else 0.0,
                    "revenue": float(r['revenue']) if r['revenue'] else 0.0,
                    "downtime": float(r['downtime']) if r['downtime'] else 0.0
                }
                for r in results
            ],
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error getting production/revenue trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 Starting ML API server...")
    logger.info(f"Database: {os.getenv('DATABASE_URL', 'Not configured')}")
    
    # Test database connection
    try:
        db_manager.check_connection()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down ML API server...")
    db_manager.close()


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
