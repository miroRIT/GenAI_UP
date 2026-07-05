import { Activity, Database, LucideIcon, RadioTower, Timer } from "lucide-react";
import { AdminPreviewCard } from "@/components/AdminPreviewCard";
import { JobHealthSummaryChart, ProviderFreshnessTrend } from "@/components/CommandCharts";
import { Nav } from "@/components/Nav";
import { PageHeader, ProviderBadge, StatusBadge } from "@/components/UIPrimitives";
import { getOperations } from "@/lib/api";

export default async function OperationsPage() {
  const operations = await getOperations();
  const cards: Array<[string, string | number, LucideIcon]> = [
    ["API Status", operations.api_status, Activity],
    ["Avg Response", `${operations.average_response_time_ms} ms`, Timer],
    ["Queue Depth", operations.queue_depth, RadioTower],
    ["Dead Letters", operations.dead_letter_count, Database],
  ];

  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <PageHeader eyebrow="Operations Center" title="Provider, Job, and Audit Health" description="Simulated production readiness for provider feeds, ingestion jobs, queues, and authority audit trails." />
        <section className="grid gap-3 md:grid-cols-4">
          {cards.map(([label, value, Icon]) => (
            <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm" key={String(label)}>
              <Icon className="h-5 w-5 text-civic-blue" />
              <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{String(label)}</p>
              <p className="mt-1 text-2xl font-bold">{String(value)}</p>
            </div>
          ))}
        </section>
        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <ProviderFreshnessTrend operations={operations} />
          <JobHealthSummaryChart operations={operations} />
          <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold">Provider Health Center</h2>
            <div className="mt-3 grid gap-3">
              {operations.provider_health.map((provider) => (
                <div className="rounded-md border border-slate-200 p-3" key={provider.provider}>
                  <div className="flex items-center justify-between">
                    <p className="font-medium">{provider.provider}</p>
                    <ProviderBadge live={provider.status === "Live"} />
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{provider.sample_payload}</p>
                  <p className="mt-1 text-xs text-slate-500">{provider.freshness} / {provider.mode}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold">Ingestion Jobs</h2>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr><th className="py-2">Job</th><th>Status</th><th>Records</th><th>Retry</th><th>DLQ</th></tr>
                </thead>
                <tbody>
                  {operations.job_health.map((job) => (
                    <tr className="border-t border-slate-100" key={job.job}>
                      <td className="py-3">{job.job}</td><td><StatusBadge label={job.status} tone={job.status === "Success" ? "green" : "yellow"} /></td><td>{job.records}</td><td>{job.retry_count}</td><td>{job.dead_letter_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
        <div className="mt-6">
          <AdminPreviewCard />
        </div>
        <section className="mt-6 rounded-lg border border-civic-line bg-white p-4 shadow-sm">
          <h2 className="text-lg font-semibold">Audit Timeline</h2>
          <div className="mt-3 grid gap-2">
            {operations.events.map((event) => (
              <div className="rounded-md bg-slate-50 p-3 text-sm" key={event.event_id}>
                <span className="font-medium">{event.actor}</span> {event.action} <span className="text-slate-500">{event.target}</span>
                <span className="ml-2 text-xs text-slate-500">{event.created_at}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
