"use client";
import Link from "next/link";
import { ModeToggle } from "./mode-toggle";
import { LanguageToggle } from "./language-toggle";
import { useLanguage } from "@/contexts/language-context";

export default function Header() {
	const { t } = useLanguage();
	const links = [{ to: "/", label: t.dashboard }] as const;

	return (
		<div>
			<div className="flex flex-row items-center justify-between px-2 py-1">
				<nav className="flex gap-4 text-lg">
					{links.map(({ to, label }) => {
						return (
							<Link key={to} href={to}>
								{label}
							</Link>
						);
					})}
				</nav>
				<div className="flex items-center gap-2">
					<LanguageToggle />
					<ModeToggle />
				</div>
			</div>
			<hr />
		</div>
	);
}
