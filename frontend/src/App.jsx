import { useEffect, useState } from "react";

import AgentPanel from "./components/AgentPanel.jsx";
import LiveFeed from "./components/LiveFeed.jsx";
import TelemetryChart from "./components/TelemetryChart.jsx";
import { fetchLiveTelemetry } from "./services/api.js";

export default function App() {
  const [records, setRecords] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadTelemetry() {
      try {
        const data = await fetchLiveTelemetry();
        if (isMounted) {
          setRecords(data.records);
          setSummary(data.summary);
          setErrorMessage("");
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(error.message);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadTelemetry();
    const intervalId = window.setInterval(loadTelemetry, 5000);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-5 py-6">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-civic-signal">
              Gen AI Academy APAC Challenge
            </p>
            <h1 className="text-3xl font-bold text-civic-ink">
              Decision Intelligence Platform
            </h1>
          </div>
          <div className="text-sm text-slate-500">Live urban telemetry workspace</div>
        </header>

        {errorMessage ? (
          <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {errorMessage}
          </div>
        ) : null}

        <section className="grid gap-3 md:grid-cols-4">
          <Metric label="Avg Congestion" value={`${summary?.average_congestion ?? 0}%`} />
          <Metric label="Avg AQI" value={summary?.average_aqi ?? 0} />
          <Metric
            label="Avg Response"
            value={`${summary?.average_response_time_minutes ?? 0}m`}
          />
          <Metric label="Emergency Calls" value={summary?.total_emergency_call_volume ?? 0} />
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
          <div className="space-y-6">
            <TelemetryChart records={records} />
            <AgentPanel />
          </div>
          <LiveFeed records={records} isLoading={isLoading} />
        </div>
      </div>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-civic-ink">{value}</p>
    </div>
  );
}
