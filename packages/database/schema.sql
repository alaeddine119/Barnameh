-- ================================================
-- Smart Operations Platform - Database Schema
-- PostgreSQL + TimescaleDB for Time-Series Data
-- ================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ================================================
-- 1. CORE OPERATIONAL ENTITIES
-- ================================================

-- Organizations (multi-tenant support)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100), -- manufacturing, logistics, retail, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb
);

-- Locations/Facilities
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- warehouse, factory, office, distribution_center
    address TEXT,
    coordinates POINT, -- for logistics optimization
    capacity INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Resources (machines, vehicles, equipment)
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100), -- machine, vehicle, workstation, etc.
    status VARCHAR(50) DEFAULT 'active', -- active, maintenance, inactive
    capacity DECIMAL(10,2),
    cost_per_hour DECIMAL(10,2),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Employees/Workers
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    role VARCHAR(100), -- operator, supervisor, manager, technician
    skills JSONB DEFAULT '[]'::jsonb, -- array of skill names
    hourly_rate DECIMAL(10,2),
    max_hours_per_week INTEGER DEFAULT 40,
    preferences JSONB DEFAULT '{}'::jsonb, -- shift preferences, days off, etc.
    status VARCHAR(50) DEFAULT 'active',
    hired_at DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================
-- 2. TIME-SERIES OPERATIONAL DATA (Historical)
-- ================================================

-- Production/Operations Events (TimescaleDB hypertable)
CREATE TABLE operational_events (
    time TIMESTAMPTZ NOT NULL,
    organization_id UUID NOT NULL,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES resources(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL, -- production, maintenance, shift_start, shift_end, error, downtime
    event_subtype VARCHAR(100), -- specific error codes, maintenance types
    quantity DECIMAL(10,2), -- units produced, hours worked, etc.
    duration_minutes INTEGER, -- event duration
    quality_score DECIMAL(5,2), -- 0-100
    cost DECIMAL(10,2),
    metadata JSONB DEFAULT '{}'::jsonb, -- flexible attributes
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('operational_events', 'time');

-- Create indexes for common queries
CREATE INDEX idx_operational_events_org_time ON operational_events (organization_id, time DESC);
CREATE INDEX idx_operational_events_location_time ON operational_events (location_id, time DESC);
CREATE INDEX idx_operational_events_resource_time ON operational_events (resource_id, time DESC);
CREATE INDEX idx_operational_events_type ON operational_events (event_type, time DESC);

-- Demand/Sales Data (TimescaleDB hypertable)
CREATE TABLE demand_history (
    time TIMESTAMPTZ NOT NULL,
    organization_id UUID NOT NULL,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    product_id VARCHAR(100) NOT NULL, -- SKU or product identifier
    product_name VARCHAR(255),
    category VARCHAR(100),
    quantity DECIMAL(10,2) NOT NULL,
    revenue DECIMAL(10,2),
    channel VARCHAR(50), -- online, retail, wholesale
    metadata JSONB DEFAULT '{}'::jsonb
);

SELECT create_hypertable('demand_history', 'time');
CREATE INDEX idx_demand_org_product_time ON demand_history (organization_id, product_id, time DESC);

-- Resource Utilization Metrics (TimescaleDB hypertable)
CREATE TABLE resource_metrics (
    time TIMESTAMPTZ NOT NULL,
    resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    utilization_rate DECIMAL(5,2), -- 0-100%
    throughput DECIMAL(10,2), -- units per hour
    efficiency_score DECIMAL(5,2), -- 0-100
    downtime_minutes INTEGER,
    error_count INTEGER,
    temperature DECIMAL(5,2), -- for equipment monitoring
    energy_consumption DECIMAL(10,2), -- kWh
    metadata JSONB DEFAULT '{}'::jsonb
);

SELECT create_hypertable('resource_metrics', 'time');
CREATE INDEX idx_resource_metrics_resource_time ON resource_metrics (resource_id, time DESC);

-- Employee Attendance & Performance (TimescaleDB hypertable)
CREATE TABLE employee_attendance (
    time TIMESTAMPTZ NOT NULL,
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
    shift_id UUID, -- reference to scheduled shift
    status VARCHAR(50) NOT NULL, -- present, absent, late, overtime
    clock_in TIMESTAMPTZ,
    clock_out TIMESTAMPTZ,
    hours_worked DECIMAL(5,2),
    tasks_completed INTEGER,
    performance_score DECIMAL(5,2), -- 0-100
    notes TEXT
);

SELECT create_hypertable('employee_attendance', 'time');
CREATE INDEX idx_attendance_employee_time ON employee_attendance (employee_id, time DESC);

-- ================================================
-- 3. SCHEDULING & PLANNING
-- ================================================

-- Shifts/Schedules
CREATE TABLE shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    shift_date DATE NOT NULL,
    shift_type VARCHAR(50) NOT NULL, -- morning, afternoon, night, custom
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    required_employees INTEGER NOT NULL,
    required_skills JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_shifts_org_date ON shifts (organization_id, shift_date);
CREATE INDEX idx_shifts_location_date ON shifts (location_id, shift_date);

-- Shift Assignments
CREATE TABLE shift_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shift_id UUID REFERENCES shifts(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed BOOLEAN DEFAULT false,
    confirmed_at TIMESTAMPTZ,
    UNIQUE(shift_id, employee_id)
);

CREATE INDEX idx_shift_assignments_shift ON shift_assignments (shift_id);
CREATE INDEX idx_shift_assignments_employee ON shift_assignments (employee_id);

-- Production Plans
CREATE TABLE production_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    plan_date DATE NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(255),
    planned_quantity DECIMAL(10,2) NOT NULL,
    actual_quantity DECIMAL(10,2),
    resource_id UUID REFERENCES resources(id) ON DELETE SET NULL,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, completed, delayed
    priority INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_production_plans_org_date ON production_plans (organization_id, plan_date);
CREATE INDEX idx_production_plans_location_date ON production_plans (location_id, plan_date);

-- ================================================
-- 4. ML PREDICTIONS & FORECASTS
-- ================================================

-- Demand Forecasts
CREATE TABLE demand_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    product_id VARCHAR(100) NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_quantity DECIMAL(10,2) NOT NULL,
    confidence_lower DECIMAL(10,2), -- lower bound of prediction interval
    confidence_upper DECIMAL(10,2), -- upper bound
    model_name VARCHAR(100), -- LSTM, Prophet, ARIMA, etc.
    model_version VARCHAR(50),
    accuracy_score DECIMAL(5,4), -- MAPE, MAE, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, location_id, product_id, forecast_date, model_name)
);

CREATE INDEX idx_demand_forecasts_org_product_date ON demand_forecasts (organization_id, product_id, forecast_date);

-- Anomaly Predictions (bottlenecks, failures, etc.)
CREATE TABLE anomaly_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    predicted_time TIMESTAMPTZ NOT NULL, -- when anomaly is expected
    entity_type VARCHAR(50) NOT NULL, -- resource, location, employee, process
    entity_id UUID NOT NULL,
    anomaly_type VARCHAR(100) NOT NULL, -- bottleneck, failure, shortage, delay
    severity VARCHAR(50) NOT NULL, -- low, medium, high, critical
    probability DECIMAL(5,4) NOT NULL, -- 0-1
    impact_score DECIMAL(10,2), -- estimated cost/impact
    description TEXT,
    recommended_actions JSONB DEFAULT '[]'::jsonb,
    model_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, false_positive
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_anomaly_predictions_org_time ON anomaly_predictions (organization_id, predicted_time);
CREATE INDEX idx_anomaly_predictions_entity ON anomaly_predictions (entity_type, entity_id, predicted_time);
CREATE INDEX idx_anomaly_predictions_status ON anomaly_predictions (status, severity);

-- Employee Absence Predictions
CREATE TABLE absence_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    absence_probability DECIMAL(5,4) NOT NULL, -- 0-1
    predicted_reason VARCHAR(100), -- sick, personal, vacation
    model_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(employee_id, forecast_date)
);

CREATE INDEX idx_absence_forecasts_date ON absence_forecasts (forecast_date, absence_probability DESC);

-- ================================================
-- 5. EXTERNAL DATA SOURCES
-- ================================================

-- External Factors (weather, holidays, market data, etc.)
CREATE TABLE external_factors (
    time TIMESTAMPTZ NOT NULL,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    factor_type VARCHAR(100) NOT NULL, -- weather, holiday, market_price, fuel_cost
    factor_name VARCHAR(255),
    value DECIMAL(10,2),
    unit VARCHAR(50),
    source VARCHAR(100), -- API source
    metadata JSONB DEFAULT '{}'::jsonb
);

SELECT create_hypertable('external_factors', 'time');
CREATE INDEX idx_external_factors_location_type_time ON external_factors (location_id, factor_type, time DESC);

-- ================================================
-- 6. OPTIMIZATION RESULTS
-- ================================================

-- Optimization Runs (store results of OR algorithms)
CREATE TABLE optimization_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    optimization_type VARCHAR(100) NOT NULL, -- shift_scheduling, production_planning, route_optimization
    algorithm VARCHAR(100), -- linear_programming, genetic_algorithm, constraint_programming
    input_parameters JSONB NOT NULL,
    output_solution JSONB NOT NULL,
    objective_value DECIMAL(15,2), -- optimal value achieved
    computation_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'completed', -- completed, failed, in_progress
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_optimization_runs_org_type ON optimization_runs (organization_id, optimization_type, created_at DESC);

-- ================================================
-- 7. ALERTS & NOTIFICATIONS
-- ================================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL,
    alert_type VARCHAR(100) NOT NULL, -- prediction, anomaly, threshold_breach, schedule_conflict
    severity VARCHAR(50) NOT NULL, -- info, warning, error, critical
    title VARCHAR(255) NOT NULL,
    description TEXT,
    entity_type VARCHAR(50),
    entity_id UUID,
    related_prediction_id UUID, -- link to anomaly_predictions
    actions_taken JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'active', -- active, acknowledged, resolved
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_org_status ON alerts (organization_id, status, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts (severity, status, created_at DESC);

-- ================================================
-- 8. AUDIT & LOGGING
-- ================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID,
    user_id UUID, -- if you add user authentication
    action VARCHAR(100) NOT NULL, -- create, update, delete, predict, optimize
    entity_type VARCHAR(100),
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_org_time ON audit_logs (organization_id, created_at DESC);

-- ================================================
-- 9. VIEWS FOR COMMON QUERIES
-- ================================================

-- Daily resource utilization summary
CREATE VIEW daily_resource_utilization AS
SELECT 
    DATE(time) as date,
    resource_id,
    AVG(utilization_rate) as avg_utilization,
    AVG(efficiency_score) as avg_efficiency,
    SUM(downtime_minutes) as total_downtime,
    SUM(error_count) as total_errors
FROM resource_metrics
GROUP BY DATE(time), resource_id;

-- Employee attendance rate
CREATE VIEW employee_attendance_rate AS
SELECT 
    employee_id,
    DATE_TRUNC('month', time) as month,
    COUNT(*) FILTER (WHERE status = 'present') as present_days,
    COUNT(*) FILTER (WHERE status = 'absent') as absent_days,
    COUNT(*) FILTER (WHERE status = 'late') as late_days,
    COUNT(*) as total_scheduled_days,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'present') / NULLIF(COUNT(*), 0), 2) as attendance_rate
FROM employee_attendance
GROUP BY employee_id, DATE_TRUNC('month', time);

-- Production efficiency by location
CREATE VIEW production_efficiency AS
SELECT 
    location_id,
    DATE(plan_date) as date,
    COUNT(*) as total_plans,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_plans,
    SUM(planned_quantity) as total_planned,
    SUM(actual_quantity) as total_actual,
    ROUND(100.0 * SUM(actual_quantity) / NULLIF(SUM(planned_quantity), 0), 2) as efficiency_rate
FROM production_plans
GROUP BY location_id, DATE(plan_date);

-- ================================================
-- 10. FUNCTIONS & TRIGGERS
-- ================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to relevant tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shifts_updated_at BEFORE UPDATE ON shifts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_production_plans_updated_at BEFORE UPDATE ON production_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- SAMPLE DATA GENERATION (for hackathon demo)
-- ================================================

-- You can uncomment this section to populate with sample data
/*
-- Insert sample organization
INSERT INTO organizations (id, name, industry) 
VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Manufacturing Co.', 'manufacturing');

-- Insert sample location
INSERT INTO locations (id, organization_id, name, type, capacity)
VALUES ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Main Factory', 'factory', 1000);
*/
