import React from "react";
import { ShieldCheck, Search, Wrench, MessageSquare, CheckCircle2, Loader2 } from "lucide-react";

export type WorkflowStage =
  | "idle"
  | "input_guardrail"
  | "research_agent"
  | "tool_calling"
  | "answer_agent"
  | "output_guardrail"
  | "completed"
  | "error";

interface WorkflowStatusProps {
  currentStage: WorkflowStage;
}

const STEPS = [
  { id: "input_guardrail", label: "Input Guardrail", icon: ShieldCheck },
  { id: "research_agent", label: "Research Agent", icon: Search },
  { id: "tool_calling", label: "Tool Calling", icon: Wrench },
  { id: "answer_agent", label: "Answer Agent", icon: MessageSquare },
  { id: "output_guardrail", label: "Output Guardrail", icon: CheckCircle2 },
];

export function WorkflowStatus({ currentStage }: WorkflowStatusProps) {
  const stageOrder = [
    "idle",
    "input_guardrail",
    "research_agent",
    "tool_calling",
    "answer_agent",
    "output_guardrail",
    "completed",
  ];

  const currentIdx = stageOrder.indexOf(currentStage);

  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-textSecondary">
          Workflow Pipeline
        </h3>
        <span className="text-xs text-textSecondary font-mono">
          {currentStage === "idle" && "Ready"}
          {currentStage === "completed" && "Completed"}
          {currentStage === "error" && "Error Encountered"}
          {currentStage !== "idle" && currentStage !== "completed" && currentStage !== "error" && "Processing..."}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {STEPS.map((step, idx) => {
          const stepStageIdx = stageOrder.indexOf(step.id);
          const isCurrent = currentStage === step.id;
          const isDone = currentIdx > stepStageIdx;
          const isError = currentStage === "error" && currentIdx === stepStageIdx;

          const IconComponent = step.icon;

          let badgeStyle = "border-border bg-surface-hover/50 text-textSecondary";
          if (isDone) {
            badgeStyle = "border-emerald-500/40 bg-emerald-500/10 text-emerald-400";
          } else if (isCurrent) {
            badgeStyle = "border-accent bg-accent/15 text-accent shadow-sm shadow-accent/20";
          } else if (isError) {
            badgeStyle = "border-rose-500/40 bg-rose-500/10 text-rose-400";
          }

          return (
            <div
              key={step.id}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${badgeStyle}`}
            >
              <div className="p-1.5 rounded-md bg-background/50">
                {isCurrent ? (
                  <Loader2 className="w-4 h-4 animate-spin text-accent" />
                ) : (
                  <IconComponent className="w-4 h-4" />
                )}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-medium truncate">{step.label}</span>
                <span className="text-[10px] text-textSecondary/80">
                  {isDone ? "Done" : isCurrent ? "Active" : "Pending"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
