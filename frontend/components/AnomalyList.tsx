import { Anomaly } from "@/lib/api";

export function AnomalyList({ anomalies }: { anomalies: Anomaly[] }) {
  if (anomalies.length === 0) {
    return <p className="rounded-lg border border-civic-line bg-white p-6 text-slate-500">No anomalies detected.</p>;
  }

  return (
    <div className="grid gap-4">
      {anomalies.map((anomaly, index) => (
        <article className="rounded-lg border border-civic-line bg-white p-4 shadow-sm" key={`${anomaly.type}-${index}`}>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 className="font-semibold text-civic-ink">{anomaly.type}</h3>
              <p className="text-sm text-slate-500">{anomaly.ward_name} · {anomaly.metric}</p>
            </div>
            <span className="rounded-md border border-orange-200 bg-orange-50 px-2 py-1 text-xs font-semibold text-orange-700">
              {anomaly.severity}
            </span>
          </div>
          <p className="mt-3 text-sm text-slate-700">{anomaly.explanation}</p>
          <p className="mt-2 text-sm font-medium text-civic-ink">{anomaly.suggested_action}</p>
        </article>
      ))}
    </div>
  );
}
