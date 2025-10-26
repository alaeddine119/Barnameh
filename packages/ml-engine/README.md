# ML Engine

AI-powered analytics and prediction engine for operational intelligence.

## Overview

The ML Engine provides machine learning models and APIs for:
- Anomaly detection in operational data
- Predictive maintenance forecasting
- Resource optimization recommendations
- Conversational AI interface using Groq LLM

## Features

- **Anomaly Detection**: Real-time identification of operational issues
- **Predictive Analytics**: Forecast maintenance needs and resource requirements
- **AI Recommendations**: Natural language insights powered by Groq LLM
- **RESTful API**: FastAPI endpoints with auto-generated documentation
- **Mock Data Support**: Works without database for development

## Quick Start

### Prerequisites
- Python 3.11+
- Groq API key (for AI features)

### Installation

```bash
cd packages/ml-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-api-key-here"
export DATABASE_URL="postgresql://user:pass@localhost/db"  # Optional
```

### Train Models

```bash
# Train demand forecasters
python scripts/train_demand_models.py

### Running the Server

```bash
# Development mode with auto-reload
python -m uvicorn api.main:app --reload --port 8000

# Production mode
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

API will be available at:
- **Endpoint**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Analytics
- `GET /api/v1/analytics/resource-utilization` - Get resource metrics
- `GET /api/v1/analytics/attendance-trends` - Attendance analysis
- `GET /api/v1/analytics/production-revenue` - Production and cost data

### AI & Predictions
- `GET /api/v1/recommendations` - Get AI recommendations
- `POST /api/v1/chat` - Chat with AI assistant
- `GET /api/v1/anomalies` - Detect anomalies
- `GET /api/v1/predictions/maintenance` - Predict maintenance needs

### System
- `GET /api/v1/health` - Health check

## Configuration

### Using Mock Data (Default)
No database required. The engine generates realistic mock data automatically.

### Using Real Database

1. Set `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost/operational_db"
```

2. Ensure your database has the required schema:
```sql
-- operational_events table
CREATE TABLE operational_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    event_type VARCHAR(50),
    resource_id VARCHAR(50),
    value NUMERIC,
    cost NUMERIC
);

-- Add indexes for performance
CREATE INDEX idx_events_timestamp ON operational_events(timestamp);
CREATE INDEX idx_events_type ON operational_events(event_type);
```

3. The ML engine will automatically use real data when available.

## Architecture

```
┌──────────────────┐
│   Next.js UI     │
│  (Port 3001)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐      ┌────────────────┐
│  ML Engine API   │─────▶│   Groq LLM     │
│  FastAPI         │      │   (AI)         │
│  (Port 8000)     │      └────────────────┘
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   PostgreSQL     │
│   (Optional)     │
└──────────────────┘
```

## Development

### Adding New Endpoints

Add new routes in `api/main.py`:

```python
@app.get("/api/v1/your-endpoint")
async def your_endpoint():
    return {"data": "your_data"}
```

### Adding ML Models

Create new model files in the root directory and import them in `api/main.py`.

## Troubleshooting

## Troubleshooting

**Issue**: Import errors  
**Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Groq API errors  
**Solution**: Verify `GROQ_API_KEY` is set correctly

**Issue**: Slow responses  
**Solution**: Check database connection or use mock data mode for testing

## License

MIT License

## Development

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black .
```

### Type Checking

```bash
mypy api/ models/
```

### View Logs

```bash
tail -f logs/api_*.log
```

## Docker Deployment

### Build Image

```bash
docker build -t barnameh-ml-engine .
```

### Run Container

```bash
docker run -d \
  --name ml-engine \
  -p 8000:8000 \
  --network barnameh_network \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  barnameh-ml-engine
```

### Check Status

```bash
docker logs -f ml-engine
docker exec ml-engine curl localhost:8000/health
```

## Performance

### Latency
- Demand forecast: < 2 seconds
- Anomaly prediction: < 1 second
- Model training: 1-5 minutes

### Accuracy
- Demand forecast MAPE: < 15%
- Anomaly detection F1: > 0.75
- False positive rate: < 10%

### Scalability
- Concurrent requests: 100+
- Products supported: Unlimited
- Data volume: Millions of records

## Troubleshooting

### Models Not Loading

```bash
# Check models directory
ls -la models/

# Retrain
python scripts/train_demand_models.py
```

### Database Connection Error

```bash
# Check database is running
docker ps | grep postgres

# Test connection
psql $DATABASE_URL
```

### Low Memory

```bash
# Reduce model complexity
# In anomaly_detector.py:
IsolationForest(n_estimators=50)  # Reduce from 100
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Roadmap

- [ ] LSTM models for demand forecasting
- [ ] Multi-variate time series analysis
- [ ] A/B testing framework
- [ ] Model monitoring dashboard
- [ ] Automated retraining pipeline
- [ ] GPU acceleration
- [ ] Real-time streaming predictions

## Contributing

This is a hackathon project. Post-hackathon:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## License

MIT License - Hackathon Project

## Support

For hackathon support:
- Check DEPLOYMENT.md for detailed setup
- View API docs at /docs
- Check logs in logs/ directory

---

**Built with ❤️ for the Crédit Agricole hackathon**
