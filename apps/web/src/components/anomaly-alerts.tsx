"use client";

import {
	AlertCircle,
	AlertTriangle,
	CheckCircle,
	ChevronDown,
	ChevronUp,
	Clock,
	Info,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { type AnomalyPrediction, mlApiClient } from "@/lib/ml-api-client";

interface AnomalyAlertsProps {
	organizationId: string;
	locationId?: string;
	autoRefresh?: boolean;
	refreshInterval?: number; // in milliseconds
	maxAlerts?: number;
}

const severityConfig = {
	low: {
		icon: Info,
		color: "text-blue-500",
		bgColor: "bg-blue-500/10",
		badgeVariant: "secondary" as const,
	},
	medium: {
		icon: AlertCircle,
		color: "text-yellow-500",
		bgColor: "bg-yellow-500/10",
		badgeVariant: "default" as const,
	},
	high: {
		icon: AlertTriangle,
		color: "text-orange-500",
		bgColor: "bg-orange-500/10",
		badgeVariant: "destructive" as const,
	},
	critical: {
		icon: AlertTriangle,
		color: "text-red-500",
		bgColor: "bg-red-500/10",
		badgeVariant: "destructive" as const,
	},
};

export function AnomalyAlerts({
	organizationId,
	locationId,
	autoRefresh = true,
	refreshInterval = 30000, // 30 seconds
	maxAlerts = 10,
}: AnomalyAlertsProps) {
	const [anomalies, setAnomalies] = useState<AnomalyPrediction[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
	const [expandedAlerts, setExpandedAlerts] = useState<Set<string>>(new Set());

	const fetchAnomalies = useCallback(async () => {
		try {
			setLoading(true);
			setError(null);

			const data = await mlApiClient.getAnomalyPredictions({
				organization_id: organizationId,
				resource_id: locationId,
				hours_ahead: 336, // Next 2 weeks (14 days * 24 hours)
			});

			// Sort by severity and then by date
			const sorted = data
				.sort((a, b) => {
					const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
					const severityA =
						severityOrder[a.severity as keyof typeof severityOrder] ?? 4;
					const severityB =
						severityOrder[b.severity as keyof typeof severityOrder] ?? 4;

					if (severityA !== severityB) return severityA - severityB;
					return (
						new Date(a.predicted_time).getTime() -
						new Date(b.predicted_time).getTime()
					);
				})
				.slice(0, maxAlerts);

			setAnomalies(sorted);
			setLastUpdated(new Date());
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load anomalies");
			console.error("Anomaly error:", err);
		} finally {
			setLoading(false);
		}
	}, [organizationId, locationId, maxAlerts]);

	useEffect(() => {
		fetchAnomalies();

		// Setup auto-refresh
		if (autoRefresh) {
			const interval = setInterval(fetchAnomalies, refreshInterval);
			return () => clearInterval(interval);
		}
	}, [autoRefresh, refreshInterval, fetchAnomalies]);

	const toggleAlert = (anomalyId: string) => {
		setExpandedAlerts((prev) => {
			const newSet = new Set(prev);
			if (newSet.has(anomalyId)) {
				newSet.delete(anomalyId);
			} else {
				newSet.add(anomalyId);
			}
			return newSet;
		});
	};

	const getTimeUntil = (date: string) => {
		const now = new Date();
		const target = new Date(date);
		const diffMs = target.getTime() - now.getTime();
		const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
		const diffHours = Math.floor(
			(diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
		);

		if (diffDays > 0) {
			return `in ${diffDays}d ${diffHours}h`;
		}
		if (diffHours > 0) {
			return `in ${diffHours}h`;
		}
		return "soon";
	};

	const criticalCount = anomalies.filter(
		(a) => a.severity === "critical",
	).length;
	const highCount = anomalies.filter((a) => a.severity === "high").length;

	if (loading && anomalies.length === 0) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Anomaly Alerts</CardTitle>
					<CardDescription>Loading alerts...</CardDescription>
				</CardHeader>
				<CardContent>
					<Skeleton className="h-[200px] w-full" />
				</CardContent>
			</Card>
		);
	}

	if (error) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Anomaly Alerts</CardTitle>
					<CardDescription>Error loading alerts</CardDescription>
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
							<AlertTriangle className="h-5 w-5" />
							Anomaly Alerts
						</CardTitle>
						<CardDescription>
							Predicted operational issues •{" "}
							{anomalies[0]?.entity_type || "ML-Powered"}
						</CardDescription>
					</div>
					<div className="flex items-center gap-2">
						{criticalCount > 0 && (
							<Badge variant="destructive">{criticalCount} Critical</Badge>
						)}
						{highCount > 0 && <Badge variant="default">{highCount} High</Badge>}
					</div>
				</div>
				{lastUpdated && (
					<div className="flex items-center gap-1 text-muted-foreground text-xs">
						<Clock className="h-3 w-3" />
						Updated: {lastUpdated.toLocaleTimeString()}
					</div>
				)}
			</CardHeader>
			<CardContent>
				{anomalies.length === 0 ? (
					<div className="flex flex-col items-center justify-center py-8 text-center">
						<CheckCircle className="mb-2 h-12 w-12 text-green-500" />
						<p className="font-semibold">No Anomalies Detected</p>
						<p className="text-muted-foreground text-sm">
							All systems operating normally
						</p>
					</div>
				) : (
					<div className="space-y-3">
						{anomalies.map((anomaly) => {
							const config =
								severityConfig[
									anomaly.severity as keyof typeof severityConfig
								] || severityConfig.medium;
							const Icon = config.icon;
							const isExpanded = expandedAlerts.has(anomaly.entity_id);

							return (
								<div
									key={anomaly.entity_id}
									className={`rounded-lg border p-4 transition-colors hover:bg-muted/50 ${config.bgColor}`}
								>
									<div className="flex items-start justify-between">
										<div className="flex flex-1 items-start gap-3">
											<Icon className={`mt-0.5 h-5 w-5 ${config.color}`} />
											<div className="flex-1 space-y-1">
												<div className="flex flex-wrap items-center gap-2">
													<Badge
														variant={config.badgeVariant}
														className="uppercase"
													>
														{anomaly.severity}
													</Badge>
													<Badge variant="outline">
														{anomaly.anomaly_type}
													</Badge>
													<div className="flex items-center gap-1 text-muted-foreground text-xs">
														<Clock className="h-3 w-3" />
														{getTimeUntil(anomaly.predicted_time)}
													</div>
												</div>
												<p className="font-semibold">
													{anomaly.anomaly_type === "bottleneck" &&
														"Resource Bottleneck Predicted"}
													{anomaly.anomaly_type === "failure" &&
														"System Failure Risk"}
													{anomaly.anomaly_type === "performance_degradation" &&
														"Performance Degradation Detected"}
													{anomaly.anomaly_type === "unknown" &&
														"Operational Issue Detected"}
												</p>
												<p className="text-muted-foreground text-sm">
													Probability: {Math.round(anomaly.probability * 100)}%
													•{" "}
													{new Date(anomaly.predicted_time).toLocaleDateString(
														"en-US",
														{
															month: "short",
															day: "numeric",
															hour: "2-digit",
															minute: "2-digit",
														},
													)}
												</p>
											</div>
										</div>
										<button
											type="button"
											onClick={() => toggleAlert(anomaly.entity_id)}
											className="ml-2 rounded p-1 hover:bg-background"
											aria-label={isExpanded ? "Collapse" : "Expand"}
										>
											{isExpanded ? (
												<ChevronUp className="h-4 w-4" />
											) : (
												<ChevronDown className="h-4 w-4" />
											)}
										</button>
									</div>

									{isExpanded && anomaly.recommendations && (
										<div className="mt-4 ml-8 space-y-2 border-t pt-3">
											<p className="font-semibold text-sm">
												Recommended Actions:
											</p>
											<ul className="space-y-1.5 text-sm">
												{anomaly.recommendations.map((action) => (
													<li
														key={`${anomaly.entity_id}-${action}`}
														className="flex items-start gap-2"
													>
														<span className="mt-0.5 text-primary">•</span>
														<span>{action}</span>
													</li>
												))}
											</ul>
										</div>
									)}
								</div>
							);
						})}
					</div>
				)}
			</CardContent>
		</Card>
	);
}
