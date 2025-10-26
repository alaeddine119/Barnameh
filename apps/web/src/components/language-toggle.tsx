"use client";

import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Languages } from "lucide-react";
import { useLanguage } from "@/contexts/language-context";

export function LanguageToggle() {
	const { language, setLanguage } = useLanguage();

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button variant="ghost" size="icon">
					<Languages className="h-[1.2rem] w-[1.2rem]" />
					<span className="sr-only">Toggle language</span>
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent align="end">
				<DropdownMenuItem
					onClick={() => setLanguage("en")}
					className={language === "en" ? "bg-accent" : ""}
				>
					English
				</DropdownMenuItem>
				<DropdownMenuItem
					onClick={() => setLanguage("it")}
					className={language === "it" ? "bg-accent" : ""}
				>
					Italiano
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
