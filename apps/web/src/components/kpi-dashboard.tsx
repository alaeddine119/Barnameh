"use client";

import {
	Activity,
	AlertCircle,
	ArrowDownRight,
	ArrowUpRight,
	Clock,
	Package,
	Users,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { type KPISummary, mlApiClient } from "@/lib/ml-api-client";

interface KPIDashboardProps {
	organizationId: string;
	autoRefresh?: boolean;
	refreshInterval?: number; // in milliseconds
}

interface KPICardData {
	title: string;
	value: string | number;
	change?: number;
	changeLabel?: string;
	icon: React.ElementType;
	color: string;
	bgColor: string;
}

export function KPIDashboard({
	organizationId,
	autoRefresh = true,
	refreshInterval = 30000, // 30 seconds
}: KPIDashboardProps) {
	const [kpiData, setKpiData] = useState<KPISummary | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

	const fetchKPIs = useCallback(async () => {
		try {
			setLoading(true);
			setError(null);

			const data = await mlApiClient.getKPISummary(organizationId);
			setKpiData(data);
			setLastUpdated(new Date());
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load KPIs");
			console.error("KPI error:", err);
		} finally {
			setLoading(false);
		}
	}, [organizationId]);

	useEffect(() => {
		fetchKPIs();

		// Setup auto-refresh
		if (autoRefresh) {
			const interval = setInterval(fetchKPIs, refreshInterval);
			return () => clearInterval(interval);
		}
	}, [autoRefresh, refreshInterval, fetchKPIs]);

	if (loading && !kpiData) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Key Performance Indicators</CardTitle>
					<CardDescription>Loading metrics...</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
						{["production", "utilization", "downtime", "attendance"].map(
							(key) => (
								<Skeleton key={key} className="h-[120px] w-full" />
							),
						)}
					</div>
				</CardContent>
			</Card>
		);
	}

	if (error) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Key Performance Indicators</CardTitle>
					<CardDescription>Error loading metrics</CardDescription>
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

	if (!kpiData) {
		return null;
	}

	const kpiCards: KPICardData[] = [
		{
			title: "Total Production",
			value: kpiData.total_production.toLocaleString(),
			change: 5.2,
			changeLabel: "vs last period",
			icon: Package,
			color: "text-blue-500",
			bgColor: "bg-blue-500/10",
		},
		{
			title: "Resource Utilization",
			value: `${Math.round(kpiData.avg_utilization)}%`,
			change: kpiData.avg_utilization > 80 ? 3.1 : -2.4,
			changeLabel: "efficiency",
			icon: Activity,
			color: "text-green-500",
			bgColor: "bg-green-500/10",
		},
		{
			title: "Total Downtime",
			value: `${Math.round(kpiData.total_downtime)}h`,
			change: -12.5,
			changeLabel: "improvement",
			icon: Clock,
			color: "text-orange-500",
			bgColor: "bg-orange-500/10",
		},
		{
			title: "Avg. Attendance",
			value: `${Math.round(kpiData.avg_attendance)}%`,
			change: 1.8,
			changeLabel: "this week",
			icon: Users,
			color: "text-purple-500",
			bgColor: "bg-purple-500/10",
		},
	];

	return (
		<Card>
			<CardHeader>
				<div className="flex items-center justify-between">
					<div>
						<CardTitle className="flex items-center gap-2">
							<Activity className="h-5 w-5" />
							Key Performance Indicators
						</CardTitle>
						<CardDescription>
							Last {kpiData.period_days} days • Real-time metrics
						</CardDescription>
					</div>
					{lastUpdated && (
						<div className="text-right">
							<div className="text-muted-foreground text-xs">
								Updated: {lastUpdated.toLocaleTimeString()}
							</div>
							<div className="mt-1 flex items-center justify-end gap-1 text-green-500 text-xs">
								<span className="relative flex h-2 w-2">
									<span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
									<span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
								</span>
								Live
							</div>
						</div>
					)}
				</div>
			</CardHeader>
			<CardContent>
				<div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
					{kpiCards.map((kpi) => {
						const Icon = kpi.icon;
						const isPositive = kpi.change !== undefined && kpi.change > 0;
						const isNegative = kpi.change !== undefined && kpi.change < 0;
						const TrendIcon = isPositive
							? ArrowUpRight
							: isNegative
								? ArrowDownRight
								: null;

						return (
							<Card key={kpi.title} className="relative overflow-hidden">
								<div
									className={`absolute top-0 right-0 h-24 w-24 ${kpi.bgColor} rounded-bl-full opacity-50`}
								/>
								<CardHeader className="pb-2">
									<div className="flex items-center justify-between">
										<CardTitle className="font-medium text-muted-foreground text-sm">
											{kpi.title}
										</CardTitle>
										<Icon className={`h-5 w-5 ${kpi.color}`} />
									</div>
								</CardHeader>
								<CardContent>
									<div className="space-y-1">
										<div className="font-bold text-2xl">{kpi.value}</div>
										{kpi.change !== undefined && (
											<div className="flex items-center gap-1 text-xs">
												{TrendIcon && (
													<TrendIcon
														className={`h-3 w-3 ${
															kpi.title === "Total Downtime"
																? isNegative
																	? "text-green-500"
																	: "text-red-500"
																: isPositive
																	? "text-green-500"
																	: "text-red-500"
														}`}
													/>
												)}
												<span
													className={
														kpi.title === "Total Downtime"
															? isNegative
																? "text-green-500"
																: "text-red-500"
															: isPositive
																? "text-green-500"
																: "text-red-500"
													}
												>
													{Math.abs(kpi.change)}%
												</span>
												<span className="text-muted-foreground">
													{kpi.changeLabel}
												</span>
											</div>
										)}
									</div>
								</CardContent>
							</Card>
						);
					})}
				</div>

				{/* Summary Statistics */}
				<div className="mt-6 border-t pt-6">
					<div className="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
						<div>
							<p className="font-bold text-2xl text-green-500">
								{kpiData.avg_utilization > 80 ? "Optimal" : "Good"}
							</p>
							<p className="text-muted-foreground text-xs">Overall Status</p>
						</div>
						<div>
							<p className="font-bold text-2xl">
								{Math.round(
									(kpiData.total_production / kpiData.period_days) * 100,
								) / 100}
							</p>
							<p className="text-muted-foreground text-xs">Avg Daily Output</p>
						</div>
						<div>
							<p className="font-bold text-2xl">
								{Math.round(
									(kpiData.total_downtime / kpiData.period_days) * 10,
								) / 10}
								h
							</p>
							<p className="text-muted-foreground text-xs">
								Avg Daily Downtime
							</p>
						</div>
						<div>
							<p className="font-bold text-2xl">{kpiData.period_days}</p>
							<p className="text-muted-foreground text-xs">Days Analyzed</p>
						</div>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
