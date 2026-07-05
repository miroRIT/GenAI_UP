import { AssignedAlertsClient } from "@/components/AssignedAlertsClient";
import { Nav } from "@/components/Nav";

export default function AssignedAlertsPage() {
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Operations</p>
          <h1 className="text-3xl font-bold">My Assigned Alerts</h1>
        </header>
        <AssignedAlertsClient />
      </div>
    </main>
  );
}
