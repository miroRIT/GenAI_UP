import { Activity, AlertTriangle, RefreshCw } from "lucide-react";

function statusClasses(status) {
  if (status === "critical") {
    return "border-red-200 bg-red-50 text-red-700";
  }

  if (status === "elevated") {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }

  return "border-emerald-200 bg-emerald-50 text-emerald-700";
}

export default function LiveFeed({ records, isLoading }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-civic-signal" aria-hidden="true" />
          <h2 className="text-lg font-semibold">Live Feed</h2>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refreshes every 5s</span>
        </div>
      </div>

      <div className="space-y-3">
        {records.map((record) => (
          <article
            className="rounded-md border border-slate-200 p-3"
            key={record.sector_id}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-medium text-slate-900">{record.sector_name}</h3>
                <p className="text-sm text-slate-500">{record.traffic_sensor_id}</p>
              </div>
              <span
                className={`rounded-md border px-2 py-1 text-xs font-semibold uppercase ${statusClasses(
                  record.status,
                )}`}
              >
                {record.status}
              </span>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <span>Congestion: {record.traffic_congestion_level}%</span>
              <span>AQI: {record.air_quality_index}</span>
              <span>Calls: {record.emergency_call_volume}</span>
              <span>Response: {record.emergency_response_time_minutes}m</span>
            </div>

            {record.status === "critical" ? (
              <div className="mt-3 flex items-center gap-2 text-sm text-red-700">
                <AlertTriangle className="h-4 w-4" />
                <span>Priority score {record.decision_priority_score}</span>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
