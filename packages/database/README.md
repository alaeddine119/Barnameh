# Smart Operations Platform - Database Layer

## Overview

This package contains the **Data Layer** for the AI-powered Operations Platform, designed for the Crédit Agricole hackathon challenge. It provides a comprehensive database schema for storing historical, real-time, and external operational data.

## Architecture

### Database Stack

- **PostgreSQL 16**: Primary relational database
- **TimescaleDB**: Extension for optimized time-series data handling
- **Redis**: Caching layer for ML predictions
- **pgAdmin**: Web-based database management UI

### Schema Design

The database is organized into several key domains:

#### 1. **Core Operational Entities**
- Organizations (multi-tenant)
- Locations/Facilities
- Resources (machines, vehicles, equipment)
- Employees/Workers

#### 2. **Time-Series Operational Data** (TimescaleDB Hypertables)
- `operational_events`: Production events, maintenance, shifts, errors
- `demand_history`: Sales/demand data for forecasting
- `resource_metrics`: Utilization, efficiency, downtime metrics
- `employee_attendance`: Attendance tracking and performance

#### 3. **Scheduling & Planning**
- `shifts`: Shift schedules
- `shift_assignments`: Employee-to-shift assignments
- `production_plans`: Production scheduling

#### 4. **ML Predictions & Forecasts**
- `demand_forecasts`: ML-generated demand predictions
- `anomaly_predictions`: Bottleneck/failure predictions
- `absence_forecasts`: Employee absence predictions

#### 5. **External Data**
- `external_factors`: Weather, holidays, market data

#### 6. **Optimization Results**
- `optimization_runs`: Results from OR algorithms

#### 7. **Alerts & Notifications**
- `alerts`: System alerts and notifications

## Quick Start

### 1. Start the Database

```bash
cd packages/database

# Copy environment file
cp .env.example .env

# Start PostgreSQL, TimescaleDB, Redis, and pgAdmin
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Verify Installation

The database will automatically initialize with:
- ✅ Schema creation (schema.sql)
- ✅ Sample data (seed_data.sql)

Access pgAdmin:
- URL: http://localhost:5050
- Email: admin@barnameh.local
- Password: admin

Add server in pgAdmin:
- Host: postgres
- Port: 5432
- Database: barnameh_ops
- Username: barnameh_user
- Password: barnameh_password

### 3. Test Python Connection

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run test queries
python db_utils.py
```

## Database Schema Highlights

### Time-Series Optimization

Using **TimescaleDB hypertables** for optimal time-series query performance:

```sql
-- Example: Get hourly production rate for last 7 days
SELECT 
    time_bucket('1 hour', time) as hour,
    AVG(quantity) as avg_production,
    resource_id
FROM operational_events
WHERE event_type = 'production'
  AND time >= NOW() - INTERVAL '7 days'
GROUP BY hour, resource_id
ORDER BY hour DESC;
```

### Multi-Tenant Architecture

All tables support multiple organizations:

```sql
-- Query specific organization's data
SELECT * FROM demand_history
WHERE organization_id = '11111111-1111-1111-1111-111111111111';
```

### Flexible Metadata

JSONB fields for extensible attributes:

```sql
-- Resources can store custom metadata
{
  "max_speed": 100,
  "maintenance_interval_hours": 168,
  "sensors": ["temperature", "vibration"]
}
```

## Python Utilities

### DatabaseManager

Connection pooling and query execution:

```python
from db_utils import DatabaseManager

db = DatabaseManager()

# Execute query
results = db.execute_query(
    "SELECT * FROM resources WHERE organization_id = %s",
    (org_id,)
)

# Bulk insert
data = [(val1, val2), (val3, val4)]
db.execute_many(
    "INSERT INTO table (col1, col2) VALUES %s",
    data
)
```

### OperationalDataQueries

Pre-built queries for common operations:

```python
from db_utils import DatabaseManager, OperationalDataQueries

db = DatabaseManager()
queries = OperationalDataQueries(db)

# Get demand history
demand = queries.get_demand_history(org_id, product_id, days=90)

# Get resource utilization
utilization = queries.get_resource_utilization_summary(org_id)

# Get active anomalies
anomalies = queries.get_active_anomaly_predictions(org_id)

# Get KPI summary
kpis = queries.get_kpi_summary(org_id, days=7)
```

## Sample Data

The seed data includes:

- **2 Organizations**: Manufacturing and Logistics companies
- **3 Locations**: Factories, warehouses, distribution centers
- **5+ Resources**: Assembly lines, CNC machines, vehicles
- **7 Employees**: Various roles and skills
- **90 days** of historical demand data
- **30 days** of operational events
- **7 days** of resource metrics
- **30 days** of employee attendance
- **Forecasts** for next 30 days
- **Sample anomaly predictions**

## Key Features for Hackathon

### 1. **Historical Data Analysis**
- 90 days of demand history with seasonal patterns
- Production events with quality scores
- Resource utilization metrics
- Employee attendance patterns

### 2. **Predictive Analytics Ready**
- Structured time-series data for ML training
- Forecasting tables for storing predictions
- Anomaly detection results storage

### 3. **Optimization Support**
- Shift scheduling data
- Production planning tables
- Resource allocation tracking

### 4. **Real-time Monitoring**
- Resource metrics with minute-level granularity
- Active alerts and notifications
- Live operational events

### 5. **Dashboard Integration**
- Pre-built views for common analytics
- KPI calculation functions
- Efficient queries for visualizations

## Common Queries

### Get Recent Bottlenecks

```sql
SELECT * FROM anomaly_predictions
WHERE anomaly_type = 'bottleneck'
  AND status = 'active'
  AND severity IN ('high', 'critical')
ORDER BY probability DESC;
```

### Calculate Production Efficiency

```sql
SELECT 
    location_id,
    DATE(plan_date) as date,
    SUM(planned_quantity) as planned,
    SUM(actual_quantity) as actual,
    ROUND(100.0 * SUM(actual_quantity) / SUM(planned_quantity), 2) as efficiency
FROM production_plans
WHERE status = 'completed'
GROUP BY location_id, DATE(plan_date);
```

### Find Employees with Low Attendance

```sql
SELECT employee_id, attendance_rate
FROM employee_attendance_rate
WHERE month = DATE_TRUNC('month', CURRENT_DATE)
  AND attendance_rate < 90
ORDER BY attendance_rate ASC;
```

## Database Management

### Backup

```bash
docker exec barnameh_postgres pg_dump -U barnameh_user barnameh_ops > backup.sql
```

### Restore

```bash
docker exec -i barnameh_postgres psql -U barnameh_user barnameh_ops < backup.sql
```

### Stop Services

```bash
docker-compose down

# Remove volumes (deletes all data!)
docker-compose down -v
```

## Next Steps

1. **ML Model Integration**: Connect Python ML models to read training data and write predictions
2. **Real-time Sync**: Integrate with Convex for real-time dashboard updates
3. **API Layer**: Build FastAPI endpoints for data access
4. **External Data**: Add connectors for weather, market data APIs
5. **Optimization Engine**: Implement OR algorithms using the planning tables

## Connection Details

- **PostgreSQL**: `localhost:5432`
- **Database**: `barnameh_ops`
- **Username**: `barnameh_user`
- **Password**: `barnameh_password`
- **pgAdmin**: `http://localhost:5050`
- **Redis**: `localhost:6379`

## Troubleshooting

### Connection Issues

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Reset Database

```bash
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d
```

## License

MIT License - Hackathon Project
