import { AlertsClient } from "@/components/AlertsClient";
import { Nav } from "@/components/Nav";
import { getAlerts } from "@/lib/api";

export default async function AlertsPage() {
  const alerts = await getAlerts();
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Operations</p>
          <h1 className="text-3xl font-bold">Alert Workflow Center</h1>
        </header>
        <AlertsClient initialAlerts={alerts} />
      </div>
    </main>
  );
}
