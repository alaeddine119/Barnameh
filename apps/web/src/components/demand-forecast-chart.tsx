"use client";

import { AlertCircle, TrendingUp } from "lucide-react";
import dynamic from "next/dynamic";
import { useCallback, useEffect, useState } from "react";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { type DemandForecast, mlApiClient } from "@/lib/ml-api-client";
import { useLanguage } from "@/contexts/language-context";

// Dynamically import Recharts to avoid SSR issues
const Line = dynamic(() => import("recharts").then((mod) => mod.Line), {
	ssr: false,
});
const XAxis = dynamic(() => import("recharts").then((mod) => mod.XAxis), {
	ssr: false,
});
const YAxis = dynamic(() => import("recharts").then((mod) => mod.YAxis), {
	ssr: false,
});
const CartesianGrid = dynamic(
	() => import("recharts").then((mod) => mod.CartesianGrid),
	{ ssr: false },
);
const Tooltip = dynamic(() => import("recharts").then((mod) => mod.Tooltip), {
	ssr: false,
});
const Legend = dynamic(() => import("recharts").then((mod) => mod.Legend), {
	ssr: false,
});
const Area = dynamic(() => import("recharts").then((mod) => mod.Area), {
	ssr: false,
});
const ComposedChart = dynamic(
	() => import("recharts").then((mod) => mod.ComposedChart),
	{ ssr: false },
);
const ResponsiveContainer = dynamic(
	() => import("recharts").then((mod) => mod.ResponsiveContainer),
	{ ssr: false },
);

interface DemandForecastChartProps {
	organizationId: string;
	productId: string;
	productName?: string;
	days?: number;
	autoRefresh?: boolean;
	refreshInterval?: number; // in milliseconds
}

export function DemandForecastChart({
	organizationId,
	productId,
	productName = "Product",
	days = 30,
	autoRefresh = false,
	refreshInterval = 60000, // 1 minute
}: DemandForecastChartProps) {
	const { t } = useLanguage();
	const [forecast, setForecast] = useState<DemandForecast[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

	const fetchForecast = useCallback(async () => {
		try {
			setLoading(true);
			setError(null);

			const data = await mlApiClient.getDemandForecast({
				organization_id: organizationId,
				product_id: productId,
				periods: days,
			});

			setForecast(data);
			setLastUpdated(new Date());
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load forecast");
			console.error("Forecast error:", err);
		} finally {
			setLoading(false);
		}
	}, [organizationId, productId, days]);

	useEffect(() => {
		fetchForecast();

		// Setup auto-refresh
		if (autoRefresh) {
			const interval = setInterval(fetchForecast, refreshInterval);
			return () => clearInterval(interval);
		}
	}, [autoRefresh, refreshInterval, fetchForecast]);

	// Prepare chart data
	const chartData = forecast.map((f) => ({
		date: new Date(f.forecast_date).toLocaleDateString("en-US", {
			month: "short",
			day: "numeric",
		}),
		predicted: Math.round(f.predicted_quantity),
		lower: Math.round(f.lower_bound),
		upper: Math.round(f.upper_bound),
		confidence: Math.round((f.upper_bound - f.lower_bound) / 2),
	}));

	// Calculate statistics
	const avgPrediction =
		forecast.length > 0
			? Math.round(
					forecast.reduce((sum, f) => sum + f.predicted_quantity, 0) /
						forecast.length,
				)
			: 0;

	const maxPrediction =
		forecast.length > 0
			? Math.round(Math.max(...forecast.map((f) => f.predicted_quantity)))
			: 0;

	if (loading && forecast.length === 0) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>{t.demandForecast}</CardTitle>
					<CardDescription>{t.loading}...</CardDescription>
				</CardHeader>
				<CardContent>
					<Skeleton className="h-[300px] w-full" />
				</CardContent>
			</Card>
		);
	}

	if (error) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>{t.demandForecast}</CardTitle>
					<CardDescription>{t.error}</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="flex items-center gap-2 text-destructive">
						<AlertCircle className="h-5 w-5" />
						<p>{error}</p>
					</div>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card>
			<CardHeader>
				<div className="flex items-center justify-between">
					<div>
						<CardTitle className="flex items-center gap-2">
							<TrendingUp className="h-5 w-5" />
							{t.demandForecast}
						</CardTitle>
						<CardDescription>
							{productName} •{" "}
							{forecast.length > 0 ? forecast[0].model_name : "Prophet"} Model
						</CardDescription>
					</div>
					<div className="text-right">
						<div className="font-bold text-2xl">{avgPrediction}</div>
						<div className="text-muted-foreground text-xs">
							{t.avgDailyDemand}
						</div>
						{lastUpdated && (
							<div className="mt-1 text-muted-foreground text-xs">
								{t.updated}: {lastUpdated.toLocaleTimeString()}
							</div>
						)}
					</div>
				</div>
			</CardHeader>
			<CardContent>
				<div className="space-y-4">
					{/* Statistics */}
					<div className="grid grid-cols-3 gap-4">
						<div className="space-y-1">
							<p className="text-muted-foreground text-sm">Average</p>
							<p className="font-bold text-2xl">{avgPrediction}</p>
						</div>
						<div className="space-y-1">
							<p className="text-muted-foreground text-sm">Peak</p>
							<p className="font-bold text-2xl">{maxPrediction}</p>
						</div>
						<div className="space-y-1">
							<p className="text-muted-foreground text-sm">Confidence</p>
							<p className="font-bold text-2xl">95%</p>
						</div>
					</div>

					{/* Chart */}
					<div className="h-[300px] w-full">
						<ResponsiveContainer width="100%" height="100%">
							<ComposedChart
								data={chartData}
								margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
							>
								<defs>
									<linearGradient
										id="confidenceGradient"
										x1="0"
										y1="0"
										x2="0"
										y2="1"
									>
										<stop
											offset="5%"
											stopColor="hsl(var(--primary))"
											stopOpacity={0.3}
										/>
										<stop
											offset="95%"
											stopColor="hsl(var(--primary))"
											stopOpacity={0.05}
										/>
									</linearGradient>
								</defs>
								<CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
								<XAxis
									dataKey="date"
									className="text-xs"
									tick={{ fill: "hsl(var(--muted-foreground))" }}
								/>
								<YAxis
									className="text-xs"
									tick={{ fill: "hsl(var(--muted-foreground))" }}
								/>
								<Tooltip
									contentStyle={{
										backgroundColor: "hsl(var(--card))",
										border: "1px solid hsl(var(--border))",
										borderRadius: "var(--radius)",
									}}
									labelStyle={{ color: "hsl(var(--foreground))" }}
								/>
								<Legend />

								{/* Confidence interval */}
								<Area
									type="monotone"
									dataKey="upper"
									stroke="none"
									fill="url(#confidenceGradient)"
									name="Upper Bound"
								/>
								<Area
									type="monotone"
									dataKey="lower"
									stroke="none"
									fill="hsl(var(--background))"
									name="Lower Bound"
								/>

								{/* Predicted demand line */}
								<Line
									type="monotone"
									dataKey="predicted"
									stroke="hsl(var(--primary))"
									strokeWidth={3}
									dot={{ r: 3 }}
									name={t.predictedDemand}
								/>
							</ComposedChart>
						</ResponsiveContainer>
					</div>

					{/* Legend explanation */}
					<div className="space-y-1 text-muted-foreground text-xs">
						<p>
							<span className="font-semibold">{t.shadedArea}:</span> {t.confidenceInterval}
						</p>
						<p>
							<span className="font-semibold">{t.blueLine}:</span> {t.predictedDemand}
						</p>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
