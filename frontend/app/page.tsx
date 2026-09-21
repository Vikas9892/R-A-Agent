"use client";

import React, { useState, FormEvent } from "react";
import { Header } from "@/components/Header";
import { ChatInput } from "@/components/ChatInput";
import { WorkflowStatus, WorkflowStage } from "@/components/WorkflowStatus";
import { AnswerCard } from "@/components/AnswerCard";

export default function Home() {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [stage, setStage] = useState<WorkflowStage>("idle");
  const [answer, setAnswer] = useState<string | null>(null);
  const [toolCalls, setToolCalls] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const query = message.trim();
    if (!query || isLoading) return;

    setIsLoading(true);
    setError(null);
    setAnswer(null);
    setToolCalls(0);

    // Dynamic animation sequence simulating LangGraph nodes
    setStage("input_guardrail");

    const timer1 = setTimeout(() => setStage("research_agent"), 400);
    const timer2 = setTimeout(() => setStage("tool_calling"), 900);
    const timer3 = setTimeout(() => setStage("answer_agent"), 1600);
    const timer4 = setTimeout(() => setStage("output_guardrail"), 2200);

    try {
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Server responded with status ${res.status}`
        );
      }

      const data = await res.json();
      setAnswer(data.answer);
      setToolCalls(data.tool_calls);
      setStage("completed");
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      setStage("error");
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-accent/20">
      <Header />

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8 space-y-8">
        <section className="space-y-2">
          <h2 className="text-xl font-bold tracking-tight text-textPrimary">
            Research & Answer Assistant
          </h2>
          <p className="text-sm text-textSecondary">
            Type an arithmetic equation, weather inquiry, or technical topic.
            Watch the explicit LangGraph pipeline validate, research, and synthesize the result.
          </p>
        </section>

        {/* Input area */}
        <ChatInput
          message={message}
          setMessage={setMessage}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        {/* Pipeline status visualizer */}
        <WorkflowStatus currentStage={stage} />

        {/* Result presentation card */}
        <AnswerCard
          answer={answer}
          toolCalls={toolCalls}
          error={error}
          isLoading={isLoading}
        />
      </main>

      <footer className="border-t border-border py-4 px-6 text-center text-xs text-textSecondary">
        R & A Agent • Built with FastAPI, LangGraph, LiteLLM, and Next.js
      </footer>
    </div>
  );
}
