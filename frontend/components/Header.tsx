import React from "react";
import { Bot, Sparkles } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur sticky top-0 z-10 px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-surface-hover rounded-lg border border-border text-accent">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-semibold tracking-tight text-textPrimary">
                R & A Agent
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-accent/10 text-accent font-medium border border-accent/20">
                LangGraph + LiteLLM
              </span>
            </div>
            <p className="text-xs text-textSecondary">
              Research & Answer Agent
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-surface-hover border border-border text-xs text-textSecondary">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-medium text-emerald-400">Online</span>
        </div>
      </div>
    </header>
  );
}
