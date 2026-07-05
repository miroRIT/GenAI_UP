import { AlertsClient } from "@/components/AlertsClient";
import { AlertSeverityChart, DepartmentWorkloadChart, SlaRiskChart } from "@/components/CommandCharts";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/UIPrimitives";
import { getAlerts } from "@/lib/api";

export default async function AlertsPage() {
  const alerts = await getAlerts();
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <PageHeader eyebrow="Operations" title="Alert Command Center" description="Assign, acknowledge, resolve, and export decision-support briefs for NCR crisis scenarios." />
        <div className="mb-6 grid gap-4 lg:grid-cols-3">
          <AlertSeverityChart alerts={alerts} />
          <DepartmentWorkloadChart alerts={alerts} />
          <SlaRiskChart alerts={alerts} />
        </div>
        <AlertsClient initialAlerts={alerts} />
      </div>
    </main>
  );
}
