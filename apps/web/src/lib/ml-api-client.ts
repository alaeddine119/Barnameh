/**
 * ML API Client
 * TypeScript client for the ML prediction engine
 */

import {
	generateMockAnomalies,
	generateMockForecast,
	generateMockKPIs,
} from "./mock-data";

const ML_API_BASE_URL =
	process.env.NEXT_PUBLIC_ML_API_URL || "http://localhost:8000/api/v1";
const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA === "true";

export interface DemandForecast {
	product_id: string;
	forecast_date: string;
	predicted_quantity: number;
	lower_bound: number;
	upper_bound: number;
	confidence_level: number;
	model_name: string;
}

export interface AnomalyPrediction {
	predicted_time: string;
	entity_type: string;
	entity_id: string;
	anomaly_type:
		| "bottleneck"
		| "failure"
		| "performance_degradation"
		| "unknown";
	severity: "low" | "medium" | "high" | "critical";
	probability: number;
	description: string;
	recommendations: string[];
}

export interface KPISummary {
	total_production: number;
	avg_utilization: number;
	total_downtime: number;
	avg_attendance: number;
	period_days: number;
}

export interface RecommendationRequest {
	organization_id: string;
	question?: string;
	product_id?: string;
	language?: 'en' | 'it';
}

export interface RecommendationResponse {
	summary: string;
	priority: string;
	actions: string[];
	rationale: string;
	estimated_impact: string;
}

export interface ForecastRequest {
	organization_id: string;
	product_id: string;
	periods?: number;
}

export interface AnomalyRequest {
	organization_id: string;
	resource_id?: string;
	hours_ahead?: number;
}

export interface HealthStatus {
	status: string;
	timestamp: string;
	models_loaded: {
		demand_forecaster: boolean;
		anomaly_detector: boolean;
	};
	database_connected: boolean;
}

export interface ModelStatus {
	demand_forecaster: {
		loaded: boolean;
		products: string[];
	};
	anomaly_detector: {
		loaded: boolean;
		contamination: number | null;
	};
}

export interface ResourceUtilization {
	name: string;
	type: string;
	avg_utilization: number;
	avg_efficiency: number;
	total_downtime: number;
	total_errors: number;
}

export interface ResourceUtilizationResponse {
	resources: ResourceUtilization[];
	period_days: number;
}

export interface AttendanceTrend {
	date: string;
	present_count: number;
	absent_count: number;
	total_count: number;
	attendance_rate: number;
}

export interface AttendanceTrendsResponse {
	trends: AttendanceTrend[];
	period_days: number;
}

export interface ProductionRevenueTrend {
	date: string;
	production: number;
	revenue: number;
	downtime: number;
}

export interface ProductionRevenueResponse {
	trends: ProductionRevenueTrend[];
	period_days: number;
}

class MLAPIClient {
	private baseUrl: string;

	constructor(baseUrl: string = ML_API_BASE_URL) {
		this.baseUrl = baseUrl;
	}

	/**
	 * Check ML API health
	 */
	async checkHealth(): Promise<HealthStatus> {
		const response = await fetch(
			`${this.baseUrl.replace("/api/v1", "")}/health`,
		);
		if (!response.ok) {
			throw new Error(`Health check failed: ${response.statusText}`);
		}
		return (await response.json()) as HealthStatus;
	}

	/**
	 * Generate demand forecast
	 */
	async getDemandForecast(request: ForecastRequest): Promise<DemandForecast[]> {
		// Use mock data if configured or if API fails
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
			return generateMockForecast(request.product_id, request.periods || 30);
		}

		try {
			const response = await fetch(`${ML_API_BASE_URL}/forecast/demand`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(request),
			});

			if (!response.ok) {
				throw new Error(`Forecast API error: ${response.statusText}`);
			}

			const data = await response.json();
			return data.forecasts || [];
		} catch (error) {
			console.warn("Forecast API unavailable, using mock data:", error);
			return generateMockForecast(request.product_id, request.periods || 30);
		}
	}

	/**
	 * Get anomaly predictions
	 */
	async getAnomalyPredictions(
		request: AnomalyRequest,
	): Promise<AnomalyPrediction[]> {
		// Use mock data if configured or if API fails
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
			return generateMockAnomalies(10);
		}

		try {
			const response = await fetch(`${ML_API_BASE_URL}/predict/anomalies`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(request),
			});

			if (!response.ok) {
				throw new Error(`Anomaly API error: ${response.statusText}`);
			}

			const data = await response.json();
			return data.predictions || [];
		} catch (error) {
			console.warn("Anomaly API unavailable, using mock data:", error);
			return generateMockAnomalies(10);
		}
	}

	/**
	 * Get KPI summary
	 */
	async getKPISummary(organizationId: string, days = 7): Promise<KPISummary> {
		// Use mock data if configured or if API fails
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
			return generateMockKPIs();
		}

		try {
			const response = await fetch(
				`${ML_API_BASE_URL}/kpi/summary?organization_id=${organizationId}&days=${days}`,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
				},
			);

			if (!response.ok) {
				throw new Error(`KPI API error: ${response.statusText}`);
			}

			return await response.json();
		} catch (error) {
			console.warn("KPI API unavailable, using mock data:", error);
			return generateMockKPIs();
		}
	}

	/**
	 * Trigger model training (background)
	 */
	async trainModel(
		organizationId: string,
		modelType: "demand" | "anomaly",
		productId?: string,
	): Promise<{ message: string; status: string }> {
		const response = await fetch(`${this.baseUrl}/train/${modelType}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				organization_id: organizationId,
				model_type: modelType,
				product_id: productId,
			}),
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || "Failed to train model");
		}

		return response.json();
	}

	/**
	 * Get model status
	 */
	async getModelsStatus(): Promise<ModelStatus> {
		const response = await fetch(`${this.baseUrl}/models/status`);

		if (!response.ok) {
			throw new Error("Failed to get models status");
		}

		return (await response.json()) as ModelStatus;
	}

	/**
	 * Get LLM-based recommendations (combines ML + OR + LLM)
	 */
	async getRecommendations(request: RecommendationRequest): Promise<RecommendationResponse> {
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 600));
			
			// Return Italian mock data if language is Italian
			if (request.language === 'it') {
				return {
					summary: 'Riallocare le risorse e aumentare il personale per soddisfare la domanda di picco',
					priority: 'high',
					actions: [
						'Spostare il 10% del carico di lavoro da Machine-001 a Machine-003',
						'Aggiungere 2 membri temporanei del personale a Worker-Pool-A per i prossimi 7 giorni',
						'Programmare la manutenzione preventiva per la linea di produzione B questo fine settimana'
					],
					rationale: 'La previsione indica una domanda di picco e un elevato utilizzo di Machine-001; la riallocazione riduce i colli di bottiglia.',
					estimated_impact: 'Aumento stimato dell\'8% nell\'adempimento e $40k di risparmio sui costi nel corso del mese'
				} as RecommendationResponse;
			}
			
			return {
				summary: 'Reallocate resources and increase staffing to meet peak demand',
				priority: 'high',
				actions: [
					'Shift 10% workload from Machine-001 to Machine-003',
					'Add 2 temporary staff to Worker-Pool-A for next 7 days',
					'Schedule preventive maintenance for production line B this weekend'
				],
				rationale: 'Forecast indicates a peak demand and high utilization on Machine-001; reallocating reduces bottlenecks.',
				estimated_impact: 'Estimated 8% increase in fulfillment and $40k cost savings over the month'
			} as RecommendationResponse;
		}

		try {
			const response = await fetch(`${ML_API_BASE_URL}/recommendations`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(request)
			});

			if (!response.ok) {
				throw new Error(`Recommendations API error: ${response.statusText}`);
			}

			return await response.json();
		} catch (err) {
			console.warn('Recommendations API unavailable, using mock fallback', err);
			
			// Return Italian mock data if language is Italian
			if (request.language === 'it') {
				return {
					summary: 'Riallocare le risorse e aumentare il personale per soddisfare la domanda di picco',
					priority: 'high',
					actions: [
						'Spostare il 10% del carico di lavoro da Machine-001 a Machine-003',
						'Aggiungere 2 membri temporanei del personale a Worker-Pool-A per i prossimi 7 giorni',
						'Programmare la manutenzione preventiva per la linea di produzione B questo fine settimana'
					],
					rationale: 'La previsione indica una domanda di picco e un elevato utilizzo di Machine-001; la riallocazione riduce i colli di bottiglia.',
					estimated_impact: 'Aumento stimato dell\'8% nell\'adempimento e $40k di risparmio sui costi nel corso del mese'
				} as RecommendationResponse;
			}
			
			return {
				summary: 'Reallocate resources and increase staffing to meet peak demand',
				priority: 'high',
				actions: [
					'Shift 10% workload from Machine-001 to Machine-003',
					'Add 2 temporary staff to Worker-Pool-A for next 7 days',
					'Schedule preventive maintenance for production line B this weekend'
				],
				rationale: 'Forecast indicates a peak demand and high utilization on Machine-001; reallocating reduces bottlenecks.',
				estimated_impact: 'Estimated 8% increase in fulfillment and $40k cost savings over the month'
			} as RecommendationResponse;
		}
	}

	/**
	 * Get resource utilization data
	 */
	async getResourceUtilization(organizationId: string, days = 7): Promise<ResourceUtilizationResponse> {
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 500));
			return {
				resources: [
					{ name: 'Machine-001', type: 'production', avg_utilization: 87.5, avg_efficiency: 92.3, total_downtime: 120, total_errors: 3 },
					{ name: 'Machine-002', type: 'production', avg_utilization: 73.2, avg_efficiency: 88.1, total_downtime: 45, total_errors: 1 },
					{ name: 'Machine-003', type: 'production', avg_utilization: 65.8, avg_efficiency: 85.7, total_downtime: 30, total_errors: 2 },
					{ name: 'Warehouse-A', type: 'storage', avg_utilization: 82.1, avg_efficiency: 90.5, total_downtime: 0, total_errors: 0 },
					{ name: 'Transport-Fleet', type: 'logistics', avg_utilization: 71.4, avg_efficiency: 86.2, total_downtime: 180, total_errors: 4 }
				],
				period_days: days
			};
		}

		try {
			const response = await fetch(
				`${ML_API_BASE_URL}/analytics/resource-utilization?organization_id=${organizationId}&days=${days}`,
				{ method: 'GET', headers: { 'Content-Type': 'application/json' } }
			);

			if (!response.ok) {
				throw new Error(`Resource utilization API error: ${response.statusText}`);
			}

			return await response.json();
		} catch (err) {
			console.warn('Resource utilization API unavailable, using mock data', err);
			return {
				resources: [
					{ name: 'Machine-001', type: 'production', avg_utilization: 87.5, avg_efficiency: 92.3, total_downtime: 120, total_errors: 3 },
					{ name: 'Machine-002', type: 'production', avg_utilization: 73.2, avg_efficiency: 88.1, total_downtime: 45, total_errors: 1 },
					{ name: 'Machine-003', type: 'production', avg_utilization: 65.8, avg_efficiency: 85.7, total_downtime: 30, total_errors: 2 }
				],
				period_days: days
			};
		}
	}

	/**
	 * Get attendance trends
	 */
	async getAttendanceTrends(organizationId: string, days = 30): Promise<AttendanceTrendsResponse> {
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 500));
			const trends = Array.from({ length: days }, (_, i) => {
				const date = new Date();
				date.setDate(date.getDate() - (days - i - 1));
				const attendanceRate = 85 + Math.random() * 15;
				const totalCount = 50;
				const presentCount = Math.round((attendanceRate / 100) * totalCount);
				return {
					date: date.toISOString().split('T')[0],
					present_count: presentCount,
					absent_count: totalCount - presentCount,
					total_count: totalCount,
					attendance_rate: attendanceRate
				};
			});
			return { trends, period_days: days };
		}

		try {
			const response = await fetch(
				`${ML_API_BASE_URL}/analytics/attendance-trends?organization_id=${organizationId}&days=${days}`,
				{ method: 'GET', headers: { 'Content-Type': 'application/json' } }
			);

			if (!response.ok) {
				throw new Error(`Attendance trends API error: ${response.statusText}`);
			}

			return await response.json();
		} catch (err) {
			console.warn('Attendance trends API unavailable, using mock data', err);
			const trends = Array.from({ length: 7 }, (_, i) => {
				const date = new Date();
				date.setDate(date.getDate() - (6 - i));
				return {
					date: date.toISOString().split('T')[0],
					present_count: 45,
					absent_count: 5,
					total_count: 50,
					attendance_rate: 90
				};
			});
			return { trends, period_days: days };
		}
	}

	/**
	 * Get production and revenue trends
	 */
	async getProductionRevenue(organizationId: string, days = 30): Promise<ProductionRevenueResponse> {
		if (USE_MOCK_DATA) {
			await new Promise((resolve) => setTimeout(resolve, 500));
			const trends = Array.from({ length: days }, (_, i) => {
				const date = new Date();
				date.setDate(date.getDate() - (days - i - 1));
				return {
					date: date.toISOString().split('T')[0],
					production: 800 + Math.random() * 400,
					revenue: 15000 + Math.random() * 8000,
					downtime: Math.random() * 120
				};
			});
			return { trends, period_days: days };
		}

		try {
			const response = await fetch(
				`${ML_API_BASE_URL}/analytics/production-revenue?organization_id=${organizationId}&days=${days}`,
				{ method: 'GET', headers: { 'Content-Type': 'application/json' } }
			);

			if (!response.ok) {
				throw new Error(`Production/revenue API error: ${response.statusText}`);
			}

			return await response.json();
		} catch (err) {
			console.warn('Production/revenue API unavailable, using mock data', err);
			const trends = Array.from({ length: 7 }, (_, i) => {
				const date = new Date();
				date.setDate(date.getDate() - (6 - i));
				return {
					date: date.toISOString().split('T')[0],
					production: 1000,
					revenue: 18000,
					downtime: 45
				};
			});
			return { trends, period_days: days };
		}
	}
}

// Export singleton instance
export const mlApiClient = new MLAPIClient();

// Export class for custom instances
export default MLAPIClient;
