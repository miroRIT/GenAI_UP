import { MonitoringSignal } from "@/lib/api";

const feedLabels: Record<string, string> = {
  weather: "Weather",
  traffic: "Traffic",
  news: "News",
  geospatial: "Geo Spatial",
};

export function LiveMonitoringPanel({
  updatedAt,
  mode,
  feeds,
}: {
  updatedAt: string;
  mode: string;
  feeds: Record<string, MonitoringSignal[]>;
}) {
  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Active Monitoring Command Feed</h2>
          <p className="text-sm text-slate-500">{mode}</p>
        </div>
        <span className="text-sm text-slate-500">Updated {updatedAt}</span>
      </div>
      <div className="grid gap-4 lg:grid-cols-4">
        {Object.entries(feeds).map(([feedName, signals]) => (
          <div className="rounded-md border border-slate-200 p-3" key={feedName}>
            <h3 className="font-semibold">{feedLabels[feedName] ?? feedName}</h3>
            <div className="mt-3 space-y-3">
              {signals.slice(0, 3).map((signal) => (
                <article className="rounded-md bg-slate-50 p-3 text-sm" key={`${feedName}-${signal.zone}-${signal.signal}`}>
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-civic-ink">{signal.zone}</p>
                    <span className="rounded bg-white px-2 py-1 text-xs text-slate-600">{signal.severity}</span>
                  </div>
                  <p className="mt-1 text-slate-600">{signal.signal}: {signal.value}</p>
                  <p className="mt-2 text-xs font-medium text-civic-blue">{signal.action}</p>
                </article>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
