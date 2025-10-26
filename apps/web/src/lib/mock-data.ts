/**
 * Mock Data for ML Dashboard
 * Use this when ML API is not available
 */

import type {
	AnomalyPrediction,
	DemandForecast,
	KPISummary,
} from "./ml-api-client";

// Generate mock demand forecast data
export function generateMockForecast(
	productId: string,
	days = 30,
): DemandForecast[] {
	const forecasts: DemandForecast[] = [];
	const baseQuantity = productId === "PROD-A-001" ? 850 : 650;
	const today = new Date();

	for (let i = 0; i < days; i++) {
		const date = new Date(today);
		date.setDate(date.getDate() + i);

		// Add some seasonality and randomness
		const seasonality = Math.sin((i / 7) * Math.PI) * 100;
		const trend = i * 2;
		const random = (Math.random() - 0.5) * 50;
		const predicted = baseQuantity + seasonality + trend + random;

		forecasts.push({
			product_id: productId,
			forecast_date: date.toISOString().split("T")[0],
			predicted_quantity: Math.round(predicted),
			lower_bound: Math.round(predicted * 0.85),
			upper_bound: Math.round(predicted * 1.15),
			confidence_level: 0.95,
			model_name: "Prophet (Mock)",
		});
	}

	return forecasts;
}

// Generate mock anomaly predictions
export function generateMockAnomalies(count = 5): AnomalyPrediction[] {
	const anomalyTypes = [
		"bottleneck",
		"failure",
		"performance_degradation",
	] as const;
	const severities = ["low", "medium", "high", "critical"] as const;
	const anomalies: AnomalyPrediction[] = [];

	const descriptions = {
		bottleneck: "Resource bottleneck predicted in production line",
		failure: "System failure risk detected",
		performance_degradation: "Performance degradation trend observed",
	};

	const recommendations = {
		bottleneck: [
			"Allocate additional resources to production line",
			"Schedule preventive maintenance during off-peak hours",
			"Review resource allocation strategies",
		],
		failure: [
			"Schedule immediate maintenance inspection",
			"Prepare backup systems",
			"Alert maintenance team",
		],
		performance_degradation: [
			"Monitor system metrics closely",
			"Review recent configuration changes",
			"Schedule performance optimization",
		],
	};

	for (let i = 0; i < count; i++) {
		const date = new Date();
		date.setHours(date.getHours() + (i + 1) * 12);

		const type = anomalyTypes[Math.floor(Math.random() * anomalyTypes.length)];
		const severity = severities[Math.min(i, severities.length - 1)];

		anomalies.push({
			predicted_time: date.toISOString(),
			entity_type: "machine",
			entity_id: `MACHINE-${100 + i}`,
			anomaly_type: type,
			severity,
			probability: 0.65 + Math.random() * 0.3,
			description: descriptions[type],
			recommendations: recommendations[type],
		});
	}

	return anomalies;
}

// Generate mock KPI summary
export function generateMockKPIs(): KPISummary {
	return {
		total_production: 12450,
		avg_utilization: 82.5,
		total_downtime: 45.5,
		avg_attendance: 94.2,
		period_days: 30,
	};
}

// Mock API responses
export const MOCK_DATA = {
	forecast: {
		"PROD-A-001": generateMockForecast("PROD-A-001", 30),
		"PROD-B-002": generateMockForecast("PROD-B-002", 30),
	},
	anomalies: generateMockAnomalies(5),
	kpis: generateMockKPIs(),
};
