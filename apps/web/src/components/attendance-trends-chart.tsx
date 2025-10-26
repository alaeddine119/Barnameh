"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { mlApiClient } from "@/lib/ml-api-client";
import type { AttendanceTrend } from "@/lib/ml-api-client";

interface AttendanceTrendsChartProps {
	organizationId: string;
	days?: number;
	autoRefresh?: boolean;
	refreshInterval?: number;
}

export function AttendanceTrendsChart({
	organizationId,
	days = 30,
	autoRefresh = false,
	refreshInterval = 60000,
}: AttendanceTrendsChartProps) {
	const [trends, setTrends] = useState<AttendanceTrend[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const fetchData = async () => {
		try {
			setError(null);
			const data = await mlApiClient.getAttendanceTrends(organizationId, days);
			setTrends(data.trends);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load data");
			console.error("Error fetching attendance trends:", err);
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

	// Calculate average attendance rate
	const avgAttendanceRate = trends.length > 0
		? trends.reduce((sum, t) => sum + t.attendance_rate, 0) / trends.length
		: 0;

	// Show only last 30 data points for better visualization
	const displayTrends = trends.slice(-30);

	// Find min/max for scaling
	const maxRate = Math.max(...displayTrends.map(t => t.attendance_rate), 100);
	const minRate = Math.min(...displayTrends.map(t => t.attendance_rate), 0);

	return (
		<Card>
			<CardHeader>
				<CardTitle>Employee Attendance Trends</CardTitle>
				<CardDescription>
					Daily attendance rate over last {days} days
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
				) : trends.length === 0 ? (
					<div className="py-8 text-center text-muted-foreground">
						No attendance data available
					</div>
				) : (
					<div className="space-y-4">
						{/* Summary Stats */}
						<div className="grid grid-cols-3 gap-4 rounded-lg bg-muted/50 p-4">
							<div className="text-center">
								<div className="text-2xl font-bold">
									{avgAttendanceRate.toFixed(1)}%
								</div>
								<div className="text-xs text-muted-foreground">Avg Rate</div>
							</div>
							<div className="text-center">
								<div className="text-2xl font-bold text-green-600">
									{trends[trends.length - 1]?.present_count || 0}
								</div>
								<div className="text-xs text-muted-foreground">Present Today</div>
							</div>
							<div className="text-center">
								<div className="text-2xl font-bold text-red-600">
									{trends[trends.length - 1]?.absent_count || 0}
								</div>
								<div className="text-xs text-muted-foreground">Absent Today</div>
							</div>
						</div>

						{/* Line Chart */}
						<div className="relative h-64 w-full border-b border-l border-muted">
							<div className="absolute inset-0 flex items-end justify-between gap-0.5 px-2 pb-2">
								{displayTrends.map((trend) => {
									// Scale to show variation - use pixel heights for better visibility
									// Chart is h-64 = 256px, leaving some padding
									const range = maxRate - minRate;
									const normalizedValue = range > 0 
										? ((trend.attendance_rate - minRate) / range)
										: 0.5;
									const pixelHeight = Math.max(15, 80 + (normalizedValue * 150)); // 80-230px range, min 15px
									const isWeekend = new Date(trend.date).getDay() % 6 === 0;
									
									return (
										<div key={trend.date} className="group relative flex flex-1 flex-col items-center">
											{/* Bar */}
											<div
												className={`w-full rounded-t transition-all hover:opacity-80 ${
													trend.attendance_rate >= 90
														? "bg-green-500"
														: trend.attendance_rate >= 75
															? "bg-yellow-500"
															: "bg-red-500"
												} ${isWeekend ? "opacity-50" : ""}`}
												style={{ height: `${pixelHeight}px` }}
											/>
											
											{/* Tooltip on hover */}
											<div className="pointer-events-none absolute bottom-full z-10 mb-2 hidden w-32 rounded bg-popover p-2 text-xs shadow-lg group-hover:block">
												<div className="font-semibold">
													{new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
												</div>
												<div className="text-muted-foreground">
													Rate: {trend.attendance_rate.toFixed(1)}%
												</div>
												<div className="text-green-600">
													Present: {trend.present_count}
												</div>
												<div className="text-red-600">
													Absent: {trend.absent_count}
												</div>
											</div>
										</div>
									);
								})}
							</div>
						</div>

						{/* Legend */}
						<div className="flex justify-center gap-4 text-xs text-muted-foreground">
							<div className="flex items-center gap-1">
								<div className="h-3 w-3 rounded bg-green-500" />
								<span>≥90%</span>
							</div>
							<div className="flex items-center gap-1">
								<div className="h-3 w-3 rounded bg-yellow-500" />
								<span>75-89%</span>
							</div>
							<div className="flex items-center gap-1">
								<div className="h-3 w-3 rounded bg-red-500" />
								<span>&lt;75%</span>
							</div>
						</div>
					</div>
				)}
			</CardContent>
		</Card>
	);
}
