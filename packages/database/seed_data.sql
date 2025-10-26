-- ================================================
-- SEED DATA for Hackathon Demo
-- Sample data for Smart Operations Platform
-- ================================================

-- Insert sample organization
INSERT INTO organizations (id, name, industry, settings) VALUES 
('11111111-1111-1111-1111-111111111111', 'TechManuf Corp', 'manufacturing', '{"working_hours": {"start": "08:00", "end": "17:00"}, "timezone": "Europe/Paris"}'),
('22222222-2222-2222-2222-222222222222', 'LogisticsPro SA', 'logistics', '{"working_hours": {"start": "06:00", "end": "22:00"}, "timezone": "Europe/Paris"}');

-- Insert sample locations
INSERT INTO locations (id, organization_id, name, type, address, capacity) VALUES
('10000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Paris Factory North', 'factory', '12 Rue de la Production, Paris 75018', 500),
('10000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 'Lyon Warehouse', 'warehouse', '45 Avenue Logistique, Lyon 69007', 1000),
('20000000-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'Marseille Distribution Center', 'distribution_center', '78 Boulevard Maritime, Marseille 13001', 800);

-- Insert sample resources (machines, equipment)
INSERT INTO resources (id, organization_id, location_id, name, type, status, capacity, cost_per_hour, metadata) VALUES
('30000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', 'Assembly Line A1', 'assembly_line', 'active', 100, 250.00, '{"max_speed": 100, "maintenance_interval_hours": 168}'),
('30000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', 'Assembly Line A2', 'assembly_line', 'active', 100, 250.00, '{"max_speed": 100, "maintenance_interval_hours": 168}'),
('30000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', 'CNC Machine B1', 'cnc_machine', 'active', 50, 180.00, '{"precision": "0.01mm", "materials": ["aluminum", "steel"]}'),
('30000000-0000-0000-0000-000000000004', '11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', 'Quality Check Station', 'inspection', 'active', 80, 50.00, '{"automated": true}'),
('30000000-0000-0000-0000-000000000005', '22222222-2222-2222-2222-222222222222', '20000000-0000-0000-0000-000000000001', 'Delivery Truck 01', 'vehicle', 'active', 1500, 75.00, '{"fuel_type": "diesel", "capacity_kg": 1500}');

-- Insert sample employees
INSERT INTO employees (id, organization_id, employee_code, first_name, last_name, email, role, skills, hourly_rate, max_hours_per_week, preferences, hired_at) VALUES
-- TechManuf Corp employees
('40000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'EMP001', 'Jean', 'Dupont', 'jean.dupont@techmanuf.com', 'operator', '["assembly", "quality_control"]', 25.00, 35, '{"preferred_shifts": ["morning"], "days_off": ["sunday"]}', '2023-01-15'),
('40000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 'EMP002', 'Marie', 'Martin', 'marie.martin@techmanuf.com', 'operator', '["assembly", "cnc"]', 26.50, 35, '{"preferred_shifts": ["afternoon"], "days_off": ["saturday"]}', '2023-02-20'),
('40000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-111111111111', 'EMP003', 'Pierre', 'Durand', 'pierre.durand@techmanuf.com', 'supervisor', '["assembly", "quality_control", "leadership"]', 35.00, 40, '{"preferred_shifts": ["morning"], "days_off": ["sunday"]}', '2022-06-10'),
('40000000-0000-0000-0000-000000000004', '11111111-1111-1111-1111-111111111111', 'EMP004', 'Sophie', 'Bernard', 'sophie.bernard@techmanuf.com', 'technician', '["cnc", "maintenance"]', 30.00, 40, '{"preferred_shifts": ["morning", "afternoon"], "days_off": ["sunday"]}', '2023-03-05'),
('40000000-0000-0000-0000-000000000005', '11111111-1111-1111-1111-111111111111', 'EMP005', 'Luc', 'Petit', 'luc.petit@techmanuf.com', 'operator', '["assembly"]', 24.00, 35, '{"preferred_shifts": ["night"], "days_off": ["saturday", "sunday"]}', '2023-08-12'),
('40000000-0000-0000-0000-000000000006', '11111111-1111-1111-1111-111111111111', 'EMP006', 'Claire', 'Moreau', 'claire.moreau@techmanuf.com', 'operator', '["quality_control"]', 25.50, 35, '{"preferred_shifts": ["afternoon"], "days_off": ["monday"]}', '2023-09-01'),
-- LogisticsPro employees
('50000000-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'LOG001', 'Antoine', 'Leroy', 'antoine.leroy@logisticspro.com', 'driver', '["driving", "logistics"]', 28.00, 40, '{"preferred_shifts": ["morning"], "days_off": ["sunday"]}', '2022-11-20');

-- Insert historical demand data (last 90 days)
DO $$
DECLARE
    org_id UUID := '11111111-1111-1111-1111-111111111111';
    loc_id UUID := '10000000-0000-0000-0000-000000000001';
    day_offset INTEGER;
    base_demand DECIMAL;
    seasonal_factor DECIMAL;
    random_factor DECIMAL;
BEGIN
    FOR day_offset IN 0..90 LOOP
        -- Product A: Widget Pro (seasonal pattern + random noise)
        base_demand := 150;
        seasonal_factor := 1 + 0.3 * SIN((day_offset / 7.0) * 3.14159); -- weekly pattern
        random_factor := 0.8 + (RANDOM() * 0.4); -- ±20% noise
        
        INSERT INTO demand_history (time, organization_id, location_id, product_id, product_name, category, quantity, revenue, channel)
        VALUES (
            NOW() - INTERVAL '1 day' * day_offset,
            org_id,
            loc_id,
            'PROD-A-001',
            'Widget Pro',
            'electronics',
            ROUND((base_demand * seasonal_factor * random_factor)::numeric, 2),
            ROUND((base_demand * seasonal_factor * random_factor * 49.99)::numeric, 2),
            CASE WHEN RANDOM() < 0.6 THEN 'online' ELSE 'retail' END
        );

        -- Product B: Gadget Plus
        base_demand := 80;
        seasonal_factor := 1 + 0.2 * SIN((day_offset / 14.0) * 3.14159); -- bi-weekly pattern
        random_factor := 0.85 + (RANDOM() * 0.3);
        
        INSERT INTO demand_history (time, organization_id, location_id, product_id, product_name, category, quantity, revenue, channel)
        VALUES (
            NOW() - INTERVAL '1 day' * day_offset,
            org_id,
            loc_id,
            'PROD-B-002',
            'Gadget Plus',
            'electronics',
            ROUND((base_demand * seasonal_factor * random_factor)::numeric, 2),
            ROUND((base_demand * seasonal_factor * random_factor * 79.99)::numeric, 2),
            CASE WHEN RANDOM() < 0.5 THEN 'online' ELSE 'wholesale' END
        );
    END LOOP;
END $$;

-- Insert historical operational events (last 30 days)
DO $$
DECLARE
    org_id UUID := '11111111-1111-1111-1111-111111111111';
    loc_id UUID := '10000000-0000-0000-0000-000000000001';
    resource_ids UUID[] := ARRAY[
        '30000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        '30000000-0000-0000-0000-000000000003'
    ];
    day_offset INTEGER;
    hour_offset INTEGER;
    resource_id UUID;
    production_rate DECIMAL;
BEGIN
    FOR day_offset IN 0..30 LOOP
        FOR hour_offset IN 8..17 LOOP  -- 8 AM to 5 PM
            FOREACH resource_id IN ARRAY resource_ids LOOP
                -- Production events
                production_rate := 8 + (RANDOM() * 4); -- 8-12 units per hour
                
                INSERT INTO operational_events (
                    time, organization_id, location_id, resource_id, 
                    event_type, quantity, duration_minutes, quality_score
                )
                VALUES (
                    NOW() - INTERVAL '1 day' * day_offset + INTERVAL '1 hour' * hour_offset,
                    org_id,
                    loc_id,
                    resource_id,
                    'production',
                    production_rate,
                    60,
                    85 + (RANDOM() * 15) -- 85-100 quality score
                );

                -- Random downtime events (5% probability)
                IF RANDOM() < 0.05 THEN
                    INSERT INTO operational_events (
                        time, organization_id, location_id, resource_id,
                        event_type, event_subtype, duration_minutes
                    )
                    VALUES (
                        NOW() - INTERVAL '1 day' * day_offset + INTERVAL '1 hour' * hour_offset,
                        org_id,
                        loc_id,
                        resource_id,
                        'downtime',
                        CASE WHEN RANDOM() < 0.5 THEN 'maintenance' ELSE 'technical_issue' END,
                        15 + (RANDOM() * 45)::INTEGER -- 15-60 minutes
                    );
                END IF;
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- Insert resource metrics (hourly, last 7 days)
DO $$
DECLARE
    resource_ids UUID[] := ARRAY[
        '30000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000002',
        '30000000-0000-0000-0000-000000000003'
    ];
    day_offset INTEGER;
    hour_offset INTEGER;
    resource_id UUID;
BEGIN
    FOR day_offset IN 0..7 LOOP
        FOR hour_offset IN 0..23 LOOP
            FOREACH resource_id IN ARRAY resource_ids LOOP
                INSERT INTO resource_metrics (
                    time, resource_id, utilization_rate, throughput,
                    efficiency_score, downtime_minutes, error_count,
                    energy_consumption
                )
                VALUES (
                    NOW() - INTERVAL '1 day' * day_offset + INTERVAL '1 hour' * hour_offset,
                    resource_id,
                    CASE 
                        WHEN hour_offset BETWEEN 8 AND 17 THEN 75 + (RANDOM() * 20) -- work hours
                        ELSE 5 + (RANDOM() * 10) -- off hours
                    END,
                    CASE 
                        WHEN hour_offset BETWEEN 8 AND 17 THEN 8 + (RANDOM() * 4)
                        ELSE 0
                    END,
                    80 + (RANDOM() * 18),
                    CASE WHEN RANDOM() < 0.1 THEN (RANDOM() * 30)::INTEGER ELSE 0 END,
                    CASE WHEN RANDOM() < 0.05 THEN (RANDOM() * 3)::INTEGER ELSE 0 END,
                    CASE 
                        WHEN hour_offset BETWEEN 8 AND 17 THEN 15 + (RANDOM() * 10)
                        ELSE 2 + (RANDOM() * 3)
                    END
                );
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- Insert employee attendance (last 30 days)
DO $$
DECLARE
    emp_ids UUID[] := ARRAY[
        '40000000-0000-0000-0000-000000000001',
        '40000000-0000-0000-0000-000000000002',
        '40000000-0000-0000-0000-000000000003',
        '40000000-0000-0000-0000-000000000004',
        '40000000-0000-0000-0000-000000000005',
        '40000000-0000-0000-0000-000000000006'
    ];
    loc_id UUID := '10000000-0000-0000-0000-000000000001';
    day_offset INTEGER;
    emp_id UUID;
    is_weekend BOOLEAN;
    attendance_status VARCHAR(50);
BEGIN
    FOR day_offset IN 0..30 LOOP
        is_weekend := EXTRACT(DOW FROM (NOW() - INTERVAL '1 day' * day_offset)) IN (0, 6);
        
        FOREACH emp_id IN ARRAY emp_ids LOOP
            -- Skip weekends for most employees
            IF is_weekend AND RANDOM() > 0.2 THEN
                CONTINUE;
            END IF;

            -- 90% present, 5% absent, 5% late
            IF RANDOM() < 0.90 THEN
                attendance_status := 'present';
            ELSIF RANDOM() < 0.5 THEN
                attendance_status := 'absent';
            ELSE
                attendance_status := 'late';
            END IF;

            INSERT INTO employee_attendance (
                time, employee_id, location_id, status,
                clock_in, clock_out, hours_worked, tasks_completed,
                performance_score
            )
            VALUES (
                DATE(NOW() - INTERVAL '1 day' * day_offset),
                emp_id,
                loc_id,
                attendance_status,
                CASE 
                    WHEN attendance_status = 'absent' THEN NULL
                    WHEN attendance_status = 'late' THEN 
                        DATE(NOW() - INTERVAL '1 day' * day_offset) + INTERVAL '8 hour' + INTERVAL '30 minute'
                    ELSE 
                        DATE(NOW() - INTERVAL '1 day' * day_offset) + INTERVAL '8 hour'
                END,
                CASE 
                    WHEN attendance_status = 'absent' THEN NULL
                    ELSE DATE(NOW() - INTERVAL '1 day' * day_offset) + INTERVAL '17 hour'
                END,
                CASE 
                    WHEN attendance_status = 'absent' THEN 0
                    WHEN attendance_status = 'late' THEN 8.5
                    ELSE 9
                END,
                CASE 
                    WHEN attendance_status = 'absent' THEN 0
                    ELSE (5 + (RANDOM() * 5))::INTEGER
                END,
                CASE 
                    WHEN attendance_status = 'absent' THEN NULL
                    ELSE 75 + (RANDOM() * 20)
                END
            );
        END LOOP;
    END LOOP;
END $$;

-- Insert sample shifts for next 7 days
DO $$
DECLARE
    org_id UUID := '11111111-1111-1111-1111-111111111111';
    loc_id UUID := '10000000-0000-0000-0000-000000000001';
    day_offset INTEGER;
    shift_date DATE;
BEGIN
    FOR day_offset IN 0..7 LOOP
        shift_date := CURRENT_DATE + day_offset;
        
        -- Morning shift
        INSERT INTO shifts (organization_id, location_id, shift_date, shift_type, start_time, end_time, required_employees, required_skills)
        VALUES (org_id, loc_id, shift_date, 'morning', '08:00', '16:00', 3, '["assembly"]');
        
        -- Afternoon shift
        INSERT INTO shifts (organization_id, location_id, shift_date, shift_type, start_time, end_time, required_employees, required_skills)
        VALUES (org_id, loc_id, shift_date, 'afternoon', '14:00', '22:00', 2, '["assembly"]');
        
        -- Night shift (only weekdays)
        IF EXTRACT(DOW FROM shift_date) NOT IN (0, 6) THEN
            INSERT INTO shifts (organization_id, location_id, shift_date, shift_type, start_time, end_time, required_employees, required_skills)
            VALUES (org_id, loc_id, shift_date, 'night', '22:00', '06:00', 1, '["assembly"]');
        END IF;
    END LOOP;
END $$;

-- Insert sample production plans
INSERT INTO production_plans (organization_id, location_id, plan_date, product_id, product_name, planned_quantity, resource_id, start_time, end_time, priority)
VALUES
('11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', CURRENT_DATE, 'PROD-A-001', 'Widget Pro', 150, '30000000-0000-0000-0000-000000000001', CURRENT_DATE + INTERVAL '8 hour', CURRENT_DATE + INTERVAL '17 hour', 1),
('11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', CURRENT_DATE, 'PROD-B-002', 'Gadget Plus', 80, '30000000-0000-0000-0000-000000000002', CURRENT_DATE + INTERVAL '8 hour', CURRENT_DATE + INTERVAL '17 hour', 2),
('11111111-1111-1111-1111-111111111111', '10000000-0000-0000-0000-000000000001', CURRENT_DATE + 1, 'PROD-A-001', 'Widget Pro', 180, '30000000-0000-0000-0000-000000000001', CURRENT_DATE + INTERVAL '32 hour', CURRENT_DATE + INTERVAL '41 hour', 1);

-- Insert sample demand forecasts (next 30 days)
DO $$
DECLARE
    org_id UUID := '11111111-1111-1111-1111-111111111111';
    loc_id UUID := '10000000-0000-0000-0000-000000000001';
    day_offset INTEGER;
    base_forecast DECIMAL;
    trend_factor DECIMAL;
BEGIN
    FOR day_offset IN 1..30 LOOP
        -- Widget Pro forecast
        base_forecast := 155;
        trend_factor := 1 + (day_offset / 100.0); -- slight upward trend
        
        INSERT INTO demand_forecasts (
            organization_id, location_id, product_id, forecast_date,
            predicted_quantity, confidence_lower, confidence_upper,
            model_name, model_version, accuracy_score
        )
        VALUES (
            org_id, loc_id, 'PROD-A-001', CURRENT_DATE + day_offset,
            ROUND((base_forecast * trend_factor)::numeric, 2),
            ROUND((base_forecast * trend_factor * 0.85)::numeric, 2),
            ROUND((base_forecast * trend_factor * 1.15)::numeric, 2),
            'LSTM', 'v1.0', 0.9234
        );

        -- Gadget Plus forecast
        base_forecast := 85;
        
        INSERT INTO demand_forecasts (
            organization_id, location_id, product_id, forecast_date,
            predicted_quantity, confidence_lower, confidence_upper,
            model_name, model_version, accuracy_score
        )
        VALUES (
            org_id, loc_id, 'PROD-B-002', CURRENT_DATE + day_offset,
            ROUND((base_forecast * trend_factor)::numeric, 2),
            ROUND((base_forecast * trend_factor * 0.80)::numeric, 2),
            ROUND((base_forecast * trend_factor * 1.20)::numeric, 2),
            'Prophet', 'v1.0', 0.8876
        );
    END LOOP;
END $$;

-- Insert sample anomaly predictions
INSERT INTO anomaly_predictions (
    organization_id, predicted_time, entity_type, entity_id,
    anomaly_type, severity, probability, impact_score,
    description, recommended_actions, model_name
)
VALUES
('11111111-1111-1111-1111-111111111111', NOW() + INTERVAL '2 days', 'resource', '30000000-0000-0000-0000-000000000001', 
 'bottleneck', 'high', 0.78, 2500.00,
 'Assembly Line A1 predicted to reach capacity limit due to forecasted demand spike',
 '["Consider overtime scheduling", "Prepare backup line", "Increase maintenance frequency"]',
 'IsolationForest'),
 
('11111111-1111-1111-1111-111111111111', NOW() + INTERVAL '5 hours', 'resource', '30000000-0000-0000-0000-000000000003',
 'failure', 'medium', 0.62, 1800.00,
 'CNC Machine B1 showing early indicators of potential component failure',
 '["Schedule preventive maintenance", "Order replacement parts", "Monitor temperature closely"]',
 'LSTM-Autoencoder');

-- Insert sample alerts
INSERT INTO alerts (
    organization_id, alert_type, severity, title, description,
    entity_type, entity_id
)
VALUES
('11111111-1111-1111-1111-111111111111', 'prediction', 'warning', 'High Demand Forecast',
 'Widget Pro demand forecasted to increase 25% next week. Review production capacity.',
 'location', '10000000-0000-0000-0000-000000000001'),
 
('11111111-1111-1111-1111-111111111111', 'threshold_breach', 'error', 'Resource Utilization Critical',
 'Assembly Line A1 operating at 98% capacity. Risk of bottleneck.',
 'resource', '30000000-0000-0000-0000-000000000001');

-- Verify data insertion
DO $$
BEGIN
    RAISE NOTICE '✅ Organizations: %', (SELECT COUNT(*) FROM organizations);
    RAISE NOTICE '✅ Locations: %', (SELECT COUNT(*) FROM locations);
    RAISE NOTICE '✅ Resources: %', (SELECT COUNT(*) FROM resources);
    RAISE NOTICE '✅ Employees: %', (SELECT COUNT(*) FROM employees);
    RAISE NOTICE '✅ Demand History Records: %', (SELECT COUNT(*) FROM demand_history);
    RAISE NOTICE '✅ Operational Events: %', (SELECT COUNT(*) FROM operational_events);
    RAISE NOTICE '✅ Resource Metrics: %', (SELECT COUNT(*) FROM resource_metrics);
    RAISE NOTICE '✅ Employee Attendance: %', (SELECT COUNT(*) FROM employee_attendance);
    RAISE NOTICE '✅ Shifts: %', (SELECT COUNT(*) FROM shifts);
    RAISE NOTICE '✅ Production Plans: %', (SELECT COUNT(*) FROM production_plans);
    RAISE NOTICE '✅ Demand Forecasts: %', (SELECT COUNT(*) FROM demand_forecasts);
    RAISE NOTICE '✅ Anomaly Predictions: %', (SELECT COUNT(*) FROM anomaly_predictions);
    RAISE NOTICE '✅ Alerts: %', (SELECT COUNT(*) FROM alerts);
    RAISE NOTICE '========================================';
    RAISE NOTICE '🎉 Database seeded successfully!';
END $$;
