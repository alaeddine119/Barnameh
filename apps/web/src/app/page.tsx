"use client";

import { AnomalyAlerts } from "@/components/anomaly-alerts";
import { DemandForecastChart } from "@/components/demand-forecast-chart";
import { KPIDashboard } from "@/components/kpi-dashboard";
import { RecommendationsCard } from "@/components/recommendations-card";
import { AIChat } from "@/components/ai-chat";
import { ResourceUtilizationChart } from "@/components/resource-utilization-chart";
import { AttendanceTrendsChart } from "@/components/attendance-trends-chart";
import { ProductionRevenueChart } from "@/components/production-revenue-chart";
import { useLanguage } from "@/contexts/language-context";

// Demo organization and product IDs from the database seed data
const DEMO_ORG_ID = "11111111-1111-1111-1111-111111111111";
const DEMO_PRODUCT_ID = "PROD-A-001";

export default function Home() {
	const { t } = useLanguage();
	
	return (
		<div className="container mx-auto max-w-7xl space-y-8 py-8">
			<div className="space-y-2 text-center">
				<h1 className="font-bold text-3xl tracking-tight">
					{t.title}
				</h1>
				<p className="text-muted-foreground">
					{t.subtitle}
				</p>
			</div>

			{/* AI Recommendations - Top Priority */}
			<RecommendationsCard
				organizationId={DEMO_ORG_ID}
				autoRefresh={true}
				refreshInterval={60000}
			/>

			{/* KPI Dashboard */}
			<KPIDashboard
				organizationId={DEMO_ORG_ID}
				autoRefresh
				refreshInterval={30000}
			/>

			{/* Forecasts and Alerts Grid */}
			<div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
				{/* Demand Forecast */}
				<DemandForecastChart
					organizationId={DEMO_ORG_ID}
					productId={DEMO_PRODUCT_ID}
					productName="Product A"
					days={30}
					autoRefresh
					refreshInterval={60000}
				/>

				{/* Anomaly Alerts */}
				<AnomalyAlerts
					organizationId={DEMO_ORG_ID}
					autoRefresh
					refreshInterval={30000}
					maxAlerts={5}
				/>
			</div>

			{/* Additional Forecast for Product B */}
			<DemandForecastChart
				organizationId={DEMO_ORG_ID}
				productId="PROD-B-002"
				productName="Product B"
				days={30}
				autoRefresh
				refreshInterval={60000}
			/>

			{/* Analytics Section - New Charts */}
			<div className="space-y-4">
				<h2 className="text-2xl font-bold">{t.operationalAnalytics}</h2>
				
				{/* Resource Utilization */}
				<ResourceUtilizationChart
					organizationId={DEMO_ORG_ID}
					days={7}
					autoRefresh
					refreshInterval={60000}
				/>

				{/* Production & Attendance Grid */}
				<div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
					{/* Production & Revenue Trends */}
					<ProductionRevenueChart
						organizationId={DEMO_ORG_ID}
						days={30}
						autoRefresh
						refreshInterval={60000}
					/>

					{/* Employee Attendance Trends */}
					<AttendanceTrendsChart
						organizationId={DEMO_ORG_ID}
						days={30}
						autoRefresh
						refreshInterval={60000}
					/>
				</div>
			</div>

			{/* AI Chat Assistant */}
			<AIChat organizationId={DEMO_ORG_ID} productId={DEMO_PRODUCT_ID} />
		</div>
	);
}
