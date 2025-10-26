"use client";

import React, { useEffect, useState } from "react";
import { mlApiClient } from "@/lib/ml-api-client";
import type { RecommendationResponse } from "@/lib/ml-api-client";
import { Badge } from "./ui/badge";

interface Props {
    organizationId: string;
    productId?: string;
    autoRefresh?: boolean;
    refreshInterval?: number;
}

export function RecommendationsCard({
    organizationId,
    productId,
    autoRefresh = false,
    refreshInterval = 60000,
}: Props) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [rec, setRec] = useState<RecommendationResponse | null>(null);

    const fetchRec = async () => {
        setLoading(true);
        setError(null);
        try {
            const r = await mlApiClient.getRecommendations({
                organization_id: organizationId,
                product_id: productId,
                question: "How do I optimize operations for the next month?",
            });
            setRec(r);
        } catch (err: any) {
            setError(err?.message || "Failed to fetch recommendations");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRec();
        if (!autoRefresh) return;
        const id = setInterval(fetchRec, refreshInterval);
        return () => clearInterval(id);
    }, [organizationId, productId]);

    return (
        <div className="rounded-lg border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10 p-6 shadow-lg">
            <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                        <svg
                            className="h-6 w-6 text-primary"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                            />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-xl font-bold">AI Recommendations</h3>
                        <p className="text-sm text-muted-foreground">
                            Powered by Llama 3.3
                        </p>
                    </div>
                </div>
                {rec && (
                    <Badge
                        variant={
                            rec.priority === "critical"
                                ? "destructive"
                                : rec.priority === "high"
                                  ? "secondary"
                                  : "default"
                        }
                        className="text-sm px-3 py-1"
                    >
                        {rec.priority.toUpperCase()} PRIORITY
                    </Badge>
                )}
            </div>

            {loading ? (
                <div className="flex items-center gap-3 rounded-md bg-muted/50 p-6">
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                    <span className="text-sm text-muted-foreground">
                        Analyzing your operations with AI...
                    </span>
                </div>
            ) : error ? (
                <div className="rounded-md border border-destructive/20 bg-destructive/10 p-4">
                    <p className="text-sm text-destructive">{error}</p>
                </div>
            ) : rec ? (
                <div className="space-y-4">
                    {/* Summary */}
                    <div className="rounded-md border bg-card p-4">
                        <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                            Executive Summary
                        </h4>
                        <p className="text-base font-medium leading-relaxed">
                            {rec.summary}
                        </p>
                    </div>

                    {/* Actions */}
                    <div className="rounded-md border bg-card p-4">
                        <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                            Recommended Actions
                        </h4>
                        <ol className="space-y-2">
                            {rec.actions.map((a, i) => (
                                <li
                                    key={`${i}-${a.slice(0, 20)}`}
                                    className="flex gap-3"
                                >
                                    <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                                        {i + 1}
                                    </span>
                                    <span className="flex-1 text-sm leading-relaxed">
                                        {a}
                                    </span>
                                </li>
                            ))}
                        </ol>
                    </div>

                    {/* Rationale and Impact - Side by side on larger screens */}
                    <div className="grid gap-4 md:grid-cols-2">
                        {/* Rationale */}
                        <div className="rounded-md border bg-card p-4">
                            <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                                Why This Matters
                            </h4>
                            <p className="text-sm leading-relaxed text-muted-foreground">
                                {rec.rationale}
                            </p>
                        </div>

                        {/* Impact */}
                        <div className="rounded-md border bg-card p-4">
                            <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                                Expected Impact
                            </h4>
                            <p className="text-sm leading-relaxed text-muted-foreground">
                                {rec.estimated_impact}
                            </p>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="rounded-md bg-muted/50 p-6 text-center">
                    <p className="text-sm text-muted-foreground">
                        No recommendations available at this time.
                    </p>
                </div>
            )}
        </div>
    );
}

export default RecommendationsCard;
