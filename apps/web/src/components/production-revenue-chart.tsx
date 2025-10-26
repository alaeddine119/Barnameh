"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { mlApiClient } from "@/lib/ml-api-client";
import type { ProductionRevenueTrend } from "@/lib/ml-api-client";
import { useLanguage } from "@/contexts/language-context";

interface ProductionRevenueChartProps {
	organizationId: string;
	days?: number;
	autoRefresh?: boolean;
	refreshInterval?: number;
}

export function ProductionRevenueChart({
	organizationId,
	days = 30,
	autoRefresh = false,
	refreshInterval = 60000,
}: ProductionRevenueChartProps) {
	const { t } = useLanguage();
	const [trends, setTrends] = useState<ProductionRevenueTrend[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const fetchData = async () => {
		try {
			setError(null);
			const data = await mlApiClient.getProductionRevenue(organizationId, days);
			setTrends(data.trends);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load data");
			console.error("Error fetching production/revenue:", err);
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

	// Calculate totals
	const totalProduction = trends.reduce((sum, t) => sum + t.production, 0);
	const totalRevenue = trends.reduce((sum, t) => sum + t.revenue, 0);
	const totalDowntime = trends.reduce((sum, t) => sum + t.downtime, 0);

	// Show only last 30 data points for better visualization
	const displayTrends = trends.slice(-30);

	// Find max values for scaling
	const maxProduction = Math.max(...displayTrends.map(t => t.production), 1);
	const minProduction = Math.min(...displayTrends.map(t => t.production), 0);
	const maxRevenue = Math.max(...displayTrends.map(t => t.revenue), 1);
	const minRevenue = Math.min(...displayTrends.map(t => t.revenue), 0);
	
	// Calculate ranges for better scaling
	const productionRange = maxProduction - minProduction;
	const revenueRange = maxRevenue - minRevenue;

	return (
		<Card>
			<CardHeader>
				<CardTitle>{t.productionRevenueTrends}</CardTitle>
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
						{t.noProductionData}
					</div>
				) : (
					<div className="space-y-4">
						{/* Summary Stats */}
						<div className="grid grid-cols-3 gap-4 rounded-lg bg-muted/50 p-4">
							<div className="text-center">
								<div className="text-2xl font-bold">
									{totalProduction.toFixed(0)}
								</div>
								<div className="text-xs text-muted-foreground">{t.totalProduced}</div>
							</div>
							<div className="text-center">
								<div className="text-2xl font-bold text-green-600">
									${(totalRevenue / 1000).toFixed(1)}K
								</div>
								<div className="text-xs text-muted-foreground">{t.totalRevenue}</div>
							</div>
							<div className="text-center">
								<div className="text-2xl font-bold text-red-600">
									{totalDowntime.toFixed(0)}m
								</div>
								<div className="text-xs text-muted-foreground">{t.downtime}</div>
							</div>
						</div>

						{/* Dual Axis Chart */}
						<div className="space-y-6">
							{/* Production Chart */}
							<div>
								<div className="mb-2 flex items-center gap-2 text-sm font-medium">
									<div className="h-3 w-3 rounded bg-blue-500" />
									<span>{t.production}</span>
								</div>
								<div className="relative h-64 w-full border-b border-l border-muted">
									{/* Grid lines for reference */}
									<div className="absolute inset-0 flex flex-col justify-between py-2">
										<div className="h-px w-full bg-muted/30"></div>
										<div className="h-px w-full bg-muted/30"></div>
										<div className="h-px w-full bg-muted/30"></div>
										<div className="h-px w-full bg-muted/30"></div>
									</div>
									
									<div className="absolute inset-0 flex items-end justify-between gap-0.5 px-2 pb-2">
										{displayTrends.map((trend) => {
											// Scale based on range - shows variation better
											// Chart is h-64 = 256px, leaving some padding
											const chartHeight = 240; // pixels available for bars
											const normalizedValue = productionRange > 0 
												? ((trend.production - minProduction) / productionRange)
												: 0.5;
											const pixelHeight = Math.max(10, 50 + (normalizedValue * 180)); // 50-230px range, min 10px
											
											return (
												<div key={trend.date} className="group relative flex flex-1 flex-col items-center">
													<div
														className="w-full rounded-t bg-blue-500 shadow-sm transition-all hover:bg-blue-600"
														style={{ height: `${pixelHeight}px` }}
													/>
													
													<div className="pointer-events-none absolute bottom-full z-10 mb-2 hidden w-32 rounded bg-popover p-2 text-xs shadow-lg group-hover:block">
														<div className="font-semibold">
															{new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
														</div>
														<div className="text-blue-600">
															Production: {trend.production.toFixed(0)}
														</div>
													</div>
												</div>
											);
										})}
									</div>
								</div>
							</div>

							{/* Revenue Chart */}
							<div>
								<div className="mb-2 flex items-center gap-2 text-sm font-medium">
									<div className="h-3 w-3 rounded bg-green-500" />
									<span>{t.revenue}</span>
								</div>
								<div className="relative h-64 w-full border-b border-l border-muted">
									{revenueRange > 0 ? (
										<>
											{/* Grid lines for reference */}
											<div className="absolute inset-0 flex flex-col justify-between py-2">
												<div className="h-px w-full bg-muted/30" />
												<div className="h-px w-full bg-muted/30" />
												<div className="h-px w-full bg-muted/30" />
												<div className="h-px w-full bg-muted/30" />
											</div>
											
											<div className="absolute inset-0 flex items-end justify-between gap-0.5 px-2 pb-2">
												{displayTrends.map((trend) => {
													// Scale based on range - shows variation better
													// Chart is h-64 = 256px, leaving some padding
													const normalizedValue = ((trend.revenue - minRevenue) / revenueRange);
													const pixelHeight = Math.max(10, 50 + (normalizedValue * 180)); // 50-230px range, min 10px
													
													return (
														<div key={trend.date} className="group relative flex flex-1 flex-col items-center">
															<div
																className="w-full rounded-t bg-green-500 shadow-sm transition-all hover:bg-green-600"
																style={{ height: `${pixelHeight}px` }}
															/>
															<div className="pointer-events-none absolute bottom-full z-10 mb-2 hidden w-32 rounded bg-popover p-2 text-xs shadow-lg group-hover:block">
																<div className="font-semibold">
																	{new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
																</div>
																<div className="text-green-600">
																	Revenue: ${trend.revenue.toFixed(0)}
																</div>
																<div className="text-red-600">
																	Downtime: {trend.downtime.toFixed(0)}m
																</div>
															</div>
														</div>
													);
												})}
											</div>
										</>
									) : (
										<div className="flex h-full items-center justify-center text-sm text-muted-foreground">
											No revenue data available
										</div>
									)}
								</div>
							</div>
						</div>

						{/* Date Range */}
						<div className="flex justify-between text-xs text-muted-foreground">
							<span>
								{displayTrends.length > 0 
									? new Date(displayTrends[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
									: 'N/A'}
							</span>
							<span>
								{displayTrends.length > 0
									? new Date(displayTrends[displayTrends.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
									: 'N/A'}
							</span>
						</div>
					</div>
				)}
			</CardContent>
		</Card>
	);
}
