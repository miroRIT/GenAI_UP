"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { DemoOverview, DemoRecommendation, explainRecommendation, refreshDemoFeeds, runCrisisDemo, seedDemo, RecommendationExplanation } from "@/lib/api";
import { RiskBadge } from "./RiskBadge";

export function DemoModeClient({ overview, recommendations }: { overview: DemoOverview; recommendations: DemoRecommendation[] }) {
  const [message, setMessage] = useState(overview.demo_active ? "NCR crisis demo is active." : "Demo data is ready.");
  const [explanation, setExplanation] = useState<RecommendationExplanation | null>(null);

  async function activate() {
    const result = await runCrisisDemo();
    setMessage(`${result.message} ${result.scenario_count} scenarios activated.`);
  }

  async function reset() {
    await seedDemo();
    setMessage("Demo data reset to baseline.");
  }

  async function refresh() {
    await refreshDemoFeeds();
    setMessage("Weather, news, traffic, and risk demo feeds refreshed.");
  }

  async function openExplanation(id: string) {
    setExplanation(await explainRecommendation(id));
  }

  return (
    <div className="grid gap-6">
      <section className="grid gap-3 md:grid-cols-5">
        {[
          ["NCR Risk", overview.overall_risk_score],
          ["Critical Alerts", overview.active_critical_alerts],
          ["High/Critical Districts", overview.districts_at_high_or_critical_risk],
          ["Average AQI", overview.average_aqi],
          ["Traffic Index", overview.traffic_disruption_index],
        ].map(([label, value]) => (
          <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm" key={label}>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
            <p className="mt-2 text-3xl font-bold text-civic-ink">{value}</p>
          </div>
        ))}
      </section>

      <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Competition Demo Mode</p>
            <h2 className="text-2xl font-bold">Run the NCR Crisis Demo</h2>
            <p className="mt-2 max-w-3xl text-sm text-slate-600">{overview.why_this_matters}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white" onClick={activate}>Run NCR Crisis Demo</button>
            <button className="rounded-md bg-civic-blue px-4 py-2 text-sm font-semibold text-white" onClick={refresh}>Refresh Demo Feeds</button>
            <button className="rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold" onClick={reset}>Reset Demo Data</button>
          </div>
        </div>
        <p className="mt-4 rounded-md bg-slate-50 p-3 text-sm text-slate-700">{message}</p>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
          <h2 className="text-lg font-semibold">Scenario Risk Scores</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overview.scenarios}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="district_name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="risk_score" fill="#ef4444" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="grid gap-3">
          {overview.scenarios.map((scenario) => (
            <article className="rounded-lg border border-civic-line bg-white p-4 shadow-sm" key={scenario.scenario_id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">{scenario.district_name} / {scenario.primary_risk}</p>
                  <h3 className="font-semibold">{scenario.title}</h3>
                </div>
                <RiskBadge level={scenario.risk_level} />
              </div>
              <p className="mt-2 text-sm text-slate-600">{scenario.summary}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
        <h2 className="text-lg font-semibold">AI Recommendation Explainability</h2>
        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          {recommendations.map((recommendation) => (
            <button className="rounded-md border border-slate-200 p-4 text-left hover:bg-slate-50" key={recommendation.recommendation_id} onClick={() => openExplanation(recommendation.recommendation_id)}>
              <p className="font-semibold">{recommendation.title}</p>
              <p className="mt-1 text-sm text-slate-600">{recommendation.expected_impact}</p>
              <p className="mt-2 text-xs text-civic-blue">Confidence {(recommendation.confidence_score * 100).toFixed(0)}% / {recommendation.suggested_department}</p>
            </button>
          ))}
        </div>
        {explanation ? (
          <div className="mt-5 rounded-lg bg-slate-50 p-4">
            <h3 className="font-semibold">{explanation.title}</h3>
            <p className="mt-2 text-sm text-slate-700">{explanation.why_generated}</p>
            <div className="mt-4 grid gap-2 md:grid-cols-2">
              {explanation.evidence_records.map((record) => (
                <div className="rounded-md bg-white p-3 text-sm" key={`${record.title}-${record.value}`}>
                  <p className="font-medium">{record.title}</p>
                  <p className="text-slate-600">{record.value}</p>
                  <p className="text-xs text-slate-500">{record.source_type} / {record.freshness} / contribution {record.risk_contribution}</p>
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-slate-500">{explanation.limitation_note}</p>
          </div>
        ) : null}
      </section>
    </div>
  );
}
