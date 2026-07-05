import Link from "next/link";
import { ArrowRight, BrainCircuit, ChartNoAxesCombined, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      <section className="mx-auto grid min-h-screen max-w-7xl gap-10 px-5 py-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">
            AI Decision Intelligence for Community Well-being
          </p>
          <h1 className="mt-4 text-5xl font-bold leading-tight text-civic-ink">
            CivicIQ
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
            A working civic-tech prototype that combines analytics, anomaly detection,
            forecasting, lightweight RAG, and AI recommendations to help city teams
            prioritize services where communities need them most.
          </p>
          <Link
            className="mt-8 inline-flex items-center gap-2 rounded-md bg-civic-blue px-5 py-3 font-semibold text-white"
            href="/dashboard"
          >
            Open Dashboard
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid gap-4">
          <ValueCard icon={ChartNoAxesCombined} title="Decision Dashboards" text="Risk scores, KPIs, ward ranking, and trend charts for civic operations." />
          <ValueCard icon={BrainCircuit} title="AI + RAG Assistant" text="Ask natural-language questions and see evidence, sources, recommendations, and limitations." />
          <ValueCard icon={ShieldCheck} title="Responsible AI Guardrails" text="Human-in-the-loop guidance, transparent limitations, and service-prioritization safeguards." />
        </div>
      </section>
    </main>
  );
}

function ValueCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof ChartNoAxesCombined;
  title: string;
  text: string;
}) {
  return (
    <article className="rounded-lg border border-civic-line bg-civic-surface p-5">
      <Icon className="h-6 w-6 text-civic-blue" />
      <h2 className="mt-3 text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
    </article>
  );
}
