import { AnomalyList } from "@/components/AnomalyList";
import { Nav } from "@/components/Nav";
import { getAnomalies } from "@/lib/api";

export default async function AnomaliesPage() {
  const anomalies = await getAnomalies();
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-5xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Anomaly Detection</p>
          <h1 className="text-3xl font-bold text-civic-ink">Detected Civic Signals</h1>
        </header>
        <AnomalyList anomalies={anomalies} />
      </div>
    </main>
  );
}
