import React, { useState } from "react";
import { Check, Copy, Wrench, AlertCircle, Sparkles } from "lucide-react";

interface AnswerCardProps {
  answer: string | null;
  toolCalls: number;
  error: string | null;
  isLoading: boolean;
}

export function AnswerCard({
  answer,
  toolCalls,
  error,
  isLoading,
}: AnswerCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!answer) return;
    await navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (error) {
    return (
      <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-300 shadow-sm">
        <div className="flex items-center gap-2 mb-2 font-medium text-sm">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <span>Execution Error</span>
        </div>
        <p className="text-xs leading-relaxed text-rose-200/90 whitespace-pre-wrap">
          {error}
        </p>
      </div>
    );
  }

  if (!answer && !isLoading) {
    return (
      <div className="rounded-xl border border-border/80 border-dashed bg-surface/40 p-10 text-center">
        <div className="inline-flex items-center justify-center p-3 rounded-xl bg-surface-hover border border-border mb-3 text-textSecondary">
          <Sparkles className="w-5 h-5 text-accent" />
        </div>
        <h3 className="text-sm font-medium text-textPrimary mb-1">
          No Query Executed Yet
        </h3>
        <p className="text-xs text-textSecondary max-w-sm mx-auto">
          Type your question above or pick one of the quick examples to watch the
          two-agent Research & Answer workflow in action.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border border-border bg-surface p-6 shadow-sm animate-pulse space-y-3">
        <div className="h-4 bg-surface-hover rounded w-1/4"></div>
        <div className="h-3 bg-surface-hover rounded w-full"></div>
        <div className="h-3 bg-surface-hover rounded w-5/6"></div>
        <div className="h-3 bg-surface-hover rounded w-3/4"></div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-surface p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-textSecondary">
            Final Answer
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-medium bg-surface-hover border border-border text-textSecondary">
            <Wrench className="w-3 h-3 text-accent" />
            Tool Calls: <strong className="text-textPrimary">{toolCalls}</strong>
          </span>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs text-textSecondary hover:text-textPrimary bg-surface-hover/70 hover:bg-surface-hover border border-border transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      <div className="text-sm leading-relaxed text-textPrimary whitespace-pre-wrap">
        {answer}
      </div>
    </div>
  );
}
