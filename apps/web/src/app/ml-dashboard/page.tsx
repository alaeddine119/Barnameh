"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function MLDashboardPage() {
	const router = useRouter();

	useEffect(() => {
		// Redirect to homepage since ML dashboard is now the main page
		router.replace("/");
	}, [router]);

	return (
		<div className="flex min-h-screen items-center justify-center">
			<div className="text-center">
				<div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto" />
				<p className="text-muted-foreground">Redirecting to dashboard...</p>
			</div>
		</div>
	);
}