"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { mlApiClient } from "@/lib/ml-api-client";
import type { ResourceUtilization } from "@/lib/ml-api-client";

interface ResourceUtilizationChartProps {
	organizationId: string;
	days?: number;
	autoRefresh?: boolean;
	refreshInterval?: number;
}

export function ResourceUtilizationChart({
	organizationId,
	days = 7,
	autoRefresh = false,
	refreshInterval = 60000,
}: ResourceUtilizationChartProps) {
	const [resources, setResources] = useState<ResourceUtilization[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const fetchData = async () => {
		try {
			setError(null);
			const data = await mlApiClient.getResourceUtilization(organizationId, days);
			setResources(data.resources);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load data");
			console.error("Error fetching resource utilization:", err);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchData();

		if (autoRefresh && refreshInterval > 0) {
			const interval = setInterval(fetchData, refreshInterval);
			return () => clearInterval(interval);
		}
	}, [organizationId, days, autoRefresh, refreshInterval]);

	// Get max utilization for scaling
	const maxUtilization = Math.max(...resources.map(r => r.avg_utilization), 100);

	return (
		<Card>
			<CardHeader>
				<CardTitle>Resource Utilization</CardTitle>
				<CardDescription>
					Average utilization and efficiency over last {days} days
				</CardDescription>
			</CardHeader>
			<CardContent>
				{loading ? (
					<div className="flex items-center justify-center py-8">
						<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
					</div>
				) : error ? (
					<div className="rounded-lg bg-destructive/10 p-4 text-center text-destructive">
						{error}
					</div>
				) : resources.length === 0 ? (
					<div className="py-8 text-center text-muted-foreground">
						No resource data available
					</div>
				) : (
					<div className="space-y-4">
						{resources.map((resource, idx) => (
							<div key={idx} className="space-y-2">
								<div className="flex items-center justify-between">
									<div>
										<div className="font-medium">{resource.name}</div>
										<div className="text-xs text-muted-foreground capitalize">{resource.type}</div>
									</div>
									<div className="text-right">
										<div className="font-semibold text-lg">
											{resource.avg_utilization.toFixed(1)}%
										</div>
										<div className="text-xs text-muted-foreground">
											{resource.avg_efficiency.toFixed(1)}% efficiency
										</div>
									</div>
								</div>

								{/* Utilization Bar */}
								<div className="relative h-2 overflow-hidden rounded-full bg-secondary">
									<div
										className={`h-full transition-all duration-500 ${
											resource.avg_utilization >= 85
												? "bg-red-500"
												: resource.avg_utilization >= 70
													? "bg-orange-500"
													: "bg-green-500"
										}`}
										style={{ width: `${(resource.avg_utilization / maxUtilization) * 100}%` }}
									/>
								</div>

								{/* Metrics */}
								<div className="flex gap-4 text-xs text-muted-foreground">
									<span>Downtime: {resource.total_downtime}min</span>
									<span>Errors: {resource.total_errors}</span>
								</div>
							</div>
						))}
					</div>
				)}
			</CardContent>
		</Card>
	);
}
