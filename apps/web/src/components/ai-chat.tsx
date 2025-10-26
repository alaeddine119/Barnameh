"use client";

import React, { useState, useRef, useEffect } from "react";
import { mlApiClient } from "@/lib/ml-api-client";
import type { RecommendationResponse } from "@/lib/ml-api-client";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useLanguage } from "@/contexts/language-context";

interface Message {
	id: string;
	role: "user" | "assistant";
	content: string;
	timestamp: Date;
}

interface Props {
	organizationId: string;
	productId?: string;
	defaultOpen?: boolean;
}

export function AIChat({ organizationId, productId, defaultOpen = false }: Props) {
	const { t } = useLanguage();
	const [messages, setMessages] = useState<Message[]>([
		{
			id: "welcome",
			role: "assistant",
			content: t.aiChatAssistant,
			timestamp: new Date(),
		},
	]);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [isOpen, setIsOpen] = useState(defaultOpen);
	const messagesEndRef = useRef<HTMLDivElement>(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	const handleSend = async () => {
		if (!input.trim() || loading) return;

		const userMessage: Message = {
			id: `user-${Date.now()}`,
			role: "user",
			content: input.trim(),
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInput("");
		setLoading(true);

		try {
			const response: RecommendationResponse = await mlApiClient.getRecommendations({
				organization_id: organizationId,
				product_id: productId,
				question: userMessage.content,
			});

			const assistantMessage: Message = {
				id: `assistant-${Date.now()}`,
				role: "assistant",
				content: formatResponse(response),
				timestamp: new Date(),
			};

			setMessages((prev) => [...prev, assistantMessage]);
		} catch (error: unknown) {
			const errorMsg = error instanceof Error ? error.message : "Unknown error";
			const errorMessage: Message = {
				id: `error-${Date.now()}`,
				role: "assistant",
				content: `Sorry, I encountered an error: ${errorMsg}. Please try again.`,
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);
		} finally {
			setLoading(false);
		}
	};

	const formatResponse = (response: RecommendationResponse): string => {
		let formatted = `**${response.summary}**\n\n`;

		if (response.actions && response.actions.length > 0) {
			formatted += "**Recommended Actions:**\n";
			response.actions.forEach((action, i) => {
				formatted += `${i + 1}. ${action}\n`;
			});
			formatted += "\n";
		}

		if (response.rationale) {
			formatted += `**Why:** ${response.rationale}\n\n`;
		}

		if (response.estimated_impact) {
			formatted += `**Expected Impact:** ${response.estimated_impact}`;
		}

		return formatted;
	};

	const formatMessageContent = (content: string) => {
		// Simple markdown-like formatting
		return content.split("\n").map((line, i) => {
			if (line.startsWith("**") && line.endsWith("**")) {
				return (
					<p key={i} className="font-semibold mb-2">
						{line.replace(/\*\*/g, "")}
					</p>
				);
			}
			if (line.match(/^\d+\./)) {
				return (
					<li key={i} className="ml-4 mb-1">
						{line.replace(/^\d+\.\s*/, "")}
					</li>
				);
			}
			if (line.trim() === "") {
				return <br key={i} />;
			}
			return (
				<p key={i} className="mb-2">
					{line}
				</p>
			);
		});
	};

	if (!isOpen) {
		return (
			<div className="fixed bottom-6 right-6 z-50">
				<Button
					onClick={() => setIsOpen(true)}
					className="h-14 w-14 rounded-full shadow-lg"
					size="icon"
				>
					<svg
						className="h-6 w-6"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
						/>
					</svg>
				</Button>
			</div>
		);
	}

	return (
		<div className="fixed bottom-6 right-6 z-50 w-96 h-[600px] flex flex-col shadow-2xl">
			<Card className="flex flex-col h-full">
				{/* Header */}
				<div className="flex items-center justify-between p-4 border-b">
					<div className="flex items-center gap-2">
						<div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
						<h3 className="font-semibold">{t.aiChatAssistant}</h3>
					</div>
					<Button
						variant="ghost"
						size="icon"
						onClick={() => setIsOpen(false)}
						className="h-8 w-8"
					>
						<svg
							className="h-4 w-4"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</Button>
				</div>

				{/* Messages */}
				<div className="flex-1 overflow-y-auto p-4 space-y-4">
					{messages.map((message) => (
						<div
							key={message.id}
							className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
						>
							<div
								className={`max-w-[85%] rounded-lg p-3 ${
									message.role === "user"
										? "bg-primary text-primary-foreground"
										: "bg-muted"
								}`}
							>
								<div className="text-sm">
									{formatMessageContent(message.content)}
								</div>
								<div
									className={`text-xs mt-1 ${message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"}`}
								>
									{message.timestamp.toLocaleTimeString([], {
										hour: "2-digit",
										minute: "2-digit",
									})}
								</div>
							</div>
						</div>
					))}
					{loading && (
						<div className="flex justify-start">
							<div className="bg-muted rounded-lg p-3">
								<div className="flex items-center gap-2">
									<div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" />
									<div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce [animation-delay:0.2s]" />
									<div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce [animation-delay:0.4s]" />
								</div>
							</div>
						</div>
					)}
					<div ref={messagesEndRef} />
				</div>

				{/* Input */}
				<div className="p-4 border-t">
					<form
						onSubmit={(e) => {
							e.preventDefault();
							handleSend();
						}}
						className="flex gap-2"
					>
						<Input
							value={input}
							onChange={(e) => setInput(e.target.value)}
							placeholder={t.askQuestion}
							disabled={loading}
							className="flex-1"
						/>
						<Button type="submit" disabled={loading || !input.trim()}>
							<svg
								className="h-4 w-4"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
								/>
							</svg>
						</Button>
					</form>
					<p className="text-xs text-muted-foreground mt-2">
						Powered by Llama 3.3 via Groq
					</p>
				</div>
			</Card>
		</div>
	);
}

export default AIChat;
