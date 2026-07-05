"use client";

import { CheckCircle2, Copy, RotateCcw } from "lucide-react";
import { useState } from "react";
import { SectionCard, StatusBadge } from "./UIPrimitives";

const steps = [
  ["Start NCR Crisis Demo", "Activate the seeded crisis mode."],
  ["Review overall NCR risk score", "Point judges to the command KPIs."],
  ["Open Gurugram flood scenario", "Use the highest-risk district as the narrative anchor."],
  ["Inspect evidence and AI explanation", "Show weather, complaints, traffic, and utility signals."],
  ["Assign alert to Municipal Corporation", "Demonstrate operational routing."],
  ["Acknowledge alert", "Show workflow state change."],
  ["Export incident brief", "Show generated decision-support artifact."],
  ["Ask AI assistant for leadership summary", "Use the same seeded evidence."],
  ["Review operations/provider health", "Show simulated feed readiness."],
  ["End with Google Cloud production path", "Close with deployment roadmap."],
];

const script = `30-second pitch: CivicIQ is an AI decision intelligence command center for NCR authorities. It detects fragmented crisis signals, explains why they matter, and turns them into prioritized response actions.

3-minute walkthrough: Open Dashboard, run Demo Mode, inspect Gurugram flooding, show evidence, open Map, update Alerts, ask the AI assistant, then show Operations health.

5-minute walkthrough: Add exports, role badges, provider simulation, responsible AI limitations, and Google Cloud production path.`;

export function DemoWalkthroughChecklist() {
  const [completed, setCompleted] = useState<number[]>([]);
  const [message, setMessage] = useState("");

  function toggle(index: number) {
    setCompleted((current) => (current.includes(index) ? current.filter((item) => item !== index) : [...current, index]));
  }

  async function copyScript() {
    await navigator.clipboard.writeText(script);
    setMessage("3-minute script copied.");
    window.setTimeout(() => setMessage(""), 2200);
  }

  return (
    <SectionCard title="Guided Judge Walkthrough" badge={<StatusBadge label={`${completed.length}/${steps.length} complete`} tone="blue" />}>
      <div className="grid gap-2">
        {steps.map(([title, detail], index) => (
          <button className="flex gap-3 rounded-md border border-slate-200 p-3 text-left hover:bg-slate-50" key={title} onClick={() => toggle(index)} type="button">
            <CheckCircle2 className={`mt-0.5 h-5 w-5 ${completed.includes(index) ? "text-emerald-600" : "text-slate-300"}`} />
            <span>
              <span className="block font-medium">{index + 1}. {title}</span>
              <span className="text-sm text-slate-600">{detail}</span>
            </span>
          </button>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold" onClick={() => setCompleted([])} type="button">
          <RotateCcw className="h-4 w-4" /> Reset walkthrough
        </button>
        <button className="inline-flex items-center gap-2 rounded-md bg-civic-blue px-3 py-2 text-sm font-semibold text-white" onClick={copyScript} type="button">
          <Copy className="h-4 w-4" /> Copy 3-minute script
        </button>
      </div>
      {message ? <p className="mt-3 rounded-md bg-emerald-50 p-2 text-sm text-emerald-700">{message}</p> : null}
    </SectionCard>
  );
}
