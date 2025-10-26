# Database Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Smart Operations Platform                      │
│                      Data Architecture                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Next.js Web    │────▶│   FastAPI       │────▶│   PostgreSQL    │
│   Dashboard     │     │   Backend       │     │  + TimescaleDB  │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                           │
                              │                           │
                              ▼                           ▼
                        ┌─────────────┐           ┌─────────────┐
                        │   Redis     │           │   pgAdmin   │
                        │   Cache     │           │  (Web UI)   │
                        └─────────────┘           └─────────────┘
```

## Database Schema Organization

```
┌────────────────────────────────────────────────────────────────────┐
│                         barnameh_ops                                │
│                      PostgreSQL Database                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  CORE ENTITIES                                                │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  • organizations     (Multi-tenant root)                      │ │
│  │  • locations         (Factories, warehouses, etc.)            │ │
│  │  • resources         (Machines, vehicles, equipment)          │ │
│  │  • employees         (Workers with skills)                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  TIME-SERIES DATA (TimescaleDB Hypertables)                  │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  • operational_events    (Production, errors, downtime)       │ │
│  │  • demand_history        (Sales data for forecasting)         │ │
│  │  • resource_metrics      (Utilization, efficiency, energy)    │ │
│  │  • employee_attendance   (Clock in/out, performance)          │ │
│  │  • external_factors      (Weather, market data)               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  SCHEDULING & PLANNING                                        │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  • shifts                (Shift definitions)                  │ │
│  │  • shift_assignments     (Employee → Shift mapping)           │ │
│  │  • production_plans      (Production schedules)               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  ML PREDICTIONS                                               │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  • demand_forecasts      (ML-predicted demand)                │ │
│  │  • anomaly_predictions   (Bottlenecks, failures)              │ │
│  │  • absence_forecasts     (Employee absence predictions)       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  OPTIMIZATION & ALERTS                                        │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  • optimization_runs     (OR algorithm results)               │ │
│  │  • alerts                (Active notifications)               │ │
│  │  • audit_logs            (Activity tracking)                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow for AI/ML Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE                                │
└─────────────────────────────────────────────────────────────────────┘

HISTORICAL DATA                ML TRAINING               PREDICTIONS
─────────────────             ──────────────            ──────────────

┌─────────────┐              ┌────────────┐            ┌─────────────┐
│  demand_    │─────────────▶│   LSTM     │───────────▶│  demand_    │
│  history    │              │   Model    │            │  forecasts  │
│  (90 days)  │              └────────────┘            │  (30 days)  │
└─────────────┘                                        └─────────────┘
                                                              │
┌─────────────┐              ┌────────────┐                  │
│  resource_  │─────────────▶│ Isolation  │                  ▼
│  metrics    │              │  Forest    │            ┌─────────────┐
│  (7 days)   │              └────────────┘            │  anomaly_   │
└─────────────┘                    │                   │predictions  │
                                   │                   └─────────────┘
┌─────────────┐                    │                         │
│operational_ │────────────────────┘                         │
│  events     │                                              ▼
└─────────────┘                                        ┌─────────────┐
                                                       │   alerts    │
┌─────────────┐              ┌────────────┐           │  (active)   │
│  employee_  │─────────────▶│   Random   │           └─────────────┘
│ attendance  │              │   Forest   │                  │
└─────────────┘              └────────────┘                  │
                                   │                         │
                                   ▼                         ▼
                             ┌─────────────┐          ┌─────────────┐
                             │  absence_   │          │  Dashboard  │
                             │ forecasts   │          │   Alerts    │
                             └─────────────┘          └─────────────┘
```

## Operations Research Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   OPTIMIZATION WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────┘

INPUT DATA                  OR ALGORITHM              OUTPUT
──────────                 ─────────────             ───────

┌─────────────┐            ┌─────────────┐         ┌─────────────┐
│  shifts     │           │   Linear     │         │   shift_    │
│(requirements)│──────────▶│ Programming  │────────▶│ assignments │
└─────────────┘           │              │         └─────────────┘
                          │ (PuLP/       │
┌─────────────┐           │  OR-Tools)   │         ┌─────────────┐
│ employees   │──────────▶│              │────────▶│optimization_│
│(skills/pref)│           └─────────────┘         │   runs      │
└─────────────┘                  │                 └─────────────┘
                                 │
┌─────────────┐                 │                  ┌─────────────┐
│  absence_   │─────────────────┘                  │   Optimal   │
│ forecasts   │                                    │  Schedule   │
└─────────────┘           ┌─────────────┐         └─────────────┘
                          │ Constraint   │
┌─────────────┐           │ Programming  │         ┌─────────────┐
│ production_ │──────────▶│              │────────▶│  production │
│   plans     │           │ (CP-SAT)     │         │   schedule  │
└─────────────┘           └─────────────┘         └─────────────┘
        │
        │                 ┌─────────────┐         ┌─────────────┐
        └────────────────▶│   Genetic   │────────▶│  Resource   │
┌─────────────┐           │  Algorithm  │         │ Allocation  │
│   demand_   │──────────▶│             │         └─────────────┘
│  forecasts  │           └─────────────┘
└─────────────┘
```

## Real-time Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│   Next.js    │◀───────▶│   Convex     │◀───────▶│  PostgreSQL  │
│   Frontend   │  WebSocket│  Real-time  │  Sync   │   (Source)   │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │
       │                        │
       ▼                        ▼
┌──────────────────────────────────────────┐
│         DASHBOARD COMPONENTS              │
├──────────────────────────────────────────┤
│  • KPI Cards (production, efficiency)    │
│  • Time-series Charts (demand, metrics)  │
│  • Prediction Alerts (anomalies)         │
│  • Resource Heatmap (utilization)        │
│  • Schedule Calendar (shifts)            │
│  • What-if Simulator (scenarios)         │
└──────────────────────────────────────────┘
```

## Entity Relationships

```
┌─────────────┐
│organizations│
└──────┬──────┘
       │ 1
       │
       │ N
  ┌────┴────┬────────┬──────────┬──────────┐
  │         │        │          │          │
  ▼         ▼        ▼          ▼          ▼
┌───────┐┌────────┐┌────────┐┌────────┐┌────────┐
│locations││resources││employees││shifts││alerts│
└───┬───┘└────┬───┘└────┬───┘└───┬───┘└────────┘
    │         │         │        │
    │         │         │        │
    ▼         ▼         ▼        ▼
┌────────────────────────────────────────┐
│       TIME-SERIES DATA                  │
│  • operational_events                   │
│  • demand_history                       │
│  • resource_metrics                     │
│  • employee_attendance                  │
└────────────────────────────────────────┘
             │
             │ Used for training
             ▼
┌────────────────────────────────────────┐
│       ML PREDICTIONS                    │
│  • demand_forecasts                     │
│  • anomaly_predictions                  │
│  • absence_forecasts                    │
└────────────────────────────────────────┘
             │
             │ Input for optimization
             ▼
┌────────────────────────────────────────┐
│    OPTIMIZED PLANS                      │
│  • shift_assignments                    │
│  • production_plans                     │
│  • optimization_runs                    │
└────────────────────────────────────────┘
```

## Data Volumes (Sample Data)

```
Table                    Records    Time Range    Purpose
─────────────────────   ─────────  ────────────  ──────────────────
organizations                  2   Current       Multi-tenant root
locations                      3   Current       Facilities
resources                      5   Current       Equipment
employees                      7   Current       Workforce

demand_history               182   90 days       ML training data
operational_events           981   30 days       Production history
resource_metrics           1,344   7 days (hr)   Monitoring
employee_attendance          180   30 days       HR analytics

demand_forecasts              60   +30 days      Predictions
anomaly_predictions            2   +48 hours     Alerts
shifts                        21   +7 days       Scheduling
```

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│                  OPTIMIZATION STRATEGIES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. TimescaleDB Hypertables                                     │
│     • Automatic time-based partitioning                         │
│     • Optimized for time-range queries                          │
│     • Compression for old data                                  │
│                                                                  │
│  2. Indexes                                                      │
│     • organization_id + time (most queries)                     │
│     • entity_id + time (specific resources)                     │
│     • event_type (filtering)                                    │
│                                                                  │
│  3. Connection Pooling (Python)                                 │
│     • ThreadedConnectionPool                                    │
│     • Min: 1, Max: 10 connections                               │
│                                                                  │
│  4. Redis Caching                                               │
│     • ML predictions (TTL: 1 hour)                              │
│     • Frequent queries                                          │
│     • Dashboard KPIs                                            │
│                                                                  │
│  5. Materialized Views (optional)                               │
│     • Pre-computed aggregations                                 │
│     • Daily refresh for dashboards                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
