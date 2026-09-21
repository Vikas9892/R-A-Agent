import React, { FormEvent, KeyboardEvent } from "react";
import { ArrowUp, Loader2, Sparkles } from "lucide-react";

interface ChatInputProps {
  message: string;
  setMessage: (val: string) => void;
  onSubmit: (e: FormEvent) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  "What is HNSW and why is it used in Qdrant?",
  "Calculate (25 * 18) + (144 / 12) ** 2",
  "What is the current weather in Tokyo and Paris?",
  "Explain LangGraph state machines in simple terms",
];

export function ChatInput({
  message,
  setMessage,
  onSubmit,
  isLoading,
}: ChatInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (message.trim() && !isLoading) {
        onSubmit(e as unknown as FormEvent);
      }
    }
  };

  return (
    <div className="space-y-3">
      <form onSubmit={onSubmit} className="relative">
        <div className="overflow-hidden rounded-xl border border-border bg-surface shadow-md focus-within:border-accent/80 transition-colors">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="Ask a question and let the agents research it..."
            rows={3}
            className="w-full resize-none bg-transparent p-4 text-sm text-textPrimary placeholder:text-textSecondary/60 focus:outline-none disabled:opacity-50"
          />
          <div className="flex items-center justify-between px-4 py-2.5 bg-surface-hover/30 border-t border-border/50">
            <div className="flex items-center gap-1.5 text-[11px] text-textSecondary">
              <span>Press</span>
              <kbd className="px-1.5 py-0.5 rounded bg-surface border border-border text-[10px] font-mono">
                Enter
              </kbd>
              <span>to send</span>
            </div>
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-lg bg-primary text-white text-xs font-medium hover:bg-primary-hover disabled:opacity-40 disabled:hover:bg-primary transition-all shadow-sm"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Researching...</span>
                </>
              ) : (
                <>
                  <span>Run Agent</span>
                  <ArrowUp className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Example Chips */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-textSecondary flex items-center gap-1">
          <Sparkles className="w-3 h-3" /> Examples:
        </span>
        {EXAMPLE_QUERIES.map((query) => (
          <button
            key={query}
            type="button"
            disabled={isLoading}
            onClick={() => setMessage(query)}
            className="text-[11px] px-2.5 py-1 rounded-md bg-surface-hover/70 hover:bg-surface-hover border border-border text-textSecondary hover:text-textPrimary transition-colors truncate max-w-[280px]"
            title={query}
          >
            {query}
          </button>
        ))}
      </div>
    </div>
  );
}
