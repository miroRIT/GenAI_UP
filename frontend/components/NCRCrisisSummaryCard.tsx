"use client";

import { Clipboard, Download } from "lucide-react";
import { useState } from "react";
import { CrisisSummary } from "@/lib/api";
import { DemoBadge, SectionCard, StatusBadge } from "./UIPrimitives";

export function NCRCrisisSummaryCard({ summary }: { summary: CrisisSummary }) {
  const [message, setMessage] = useState("");

  async function copy(text: string, label: string) {
    await navigator.clipboard.writeText(text);
    setMessage(`${label} copied.`);
    window.setTimeout(() => setMessage(""), 2400);
  }

  function download() {
    const blob = new Blob([summary.markdown], { type: "text/markdown" });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "civiciq-ncr-crisis-summary.md";
    anchor.click();
    window.URL.revokeObjectURL(url);
    setMessage("Markdown summary downloaded.");
  }

  return (
    <SectionCard title={summary.title} badge={<DemoBadge label="Judge Demo Flow" />}>
      <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
        <div>
          <div className="mb-3 flex flex-wrap gap-2">
            <StatusBadge label={summary.overall_risk_level} tone="red" />
            <StatusBadge label={`${Math.round(summary.ai_confidence * 100)}% AI confidence`} tone="green" />
            <StatusBadge label={`${summary.data_freshness} freshness`} tone="blue" />
          </div>
          <p className="text-sm leading-6 text-slate-700">{summary.executive_summary}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button className="inline-flex items-center gap-2 rounded-md bg-civic-blue px-3 py-2 text-sm font-semibold text-white" onClick={() => copy(summary.executive_summary, "Executive summary")} type="button">
              <Clipboard className="h-4 w-4" /> Copy summary
            </button>
            <button className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold" onClick={() => copy("CivicIQ detects, explains, and prioritizes NCR crisis response using seeded weather, traffic, civic, and incident evidence.", "Judge pitch")} type="button">
              <Clipboard className="h-4 w-4" /> Copy judge pitch
            </button>
            <button className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold" onClick={download} type="button">
              <Download className="h-4 w-4" /> Download markdown
            </button>
          </div>
          {message ? <p className="mt-3 rounded-md bg-emerald-50 p-2 text-sm text-emerald-700">{message}</p> : null}
        </div>
        <div className="grid gap-2 text-sm">
          <SummaryRow label="Top districts" value={summary.top_affected_districts.join(", ")} />
          <SummaryRow label="Critical alerts" value={String(summary.active_critical_alerts)} />
          <SummaryRow label="Highest risk" value={summary.highest_risk_scenario} />
          <SummaryRow label="Top action" value={summary.top_recommended_action} />
          <SummaryRow label="Departments" value={summary.departments_involved.join(", ")} />
        </div>
      </div>
    </SectionCard>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-medium text-civic-ink">{value}</p>
    </div>
  );
}
