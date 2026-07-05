import { JobRunnerClient } from "@/components/JobRunnerClient";
import { Nav } from "@/components/Nav";
import { getJobStatus } from "@/lib/api";

export default async function DataRefreshPage() {
  const logs = await getJobStatus();
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Admin</p>
          <h1 className="text-3xl font-bold">Data Refresh Jobs</h1>
          <p className="mt-2 text-sm text-slate-600">Run provider ingestion and risk refresh jobs manually. APScheduler can run these periodically when enabled.</p>
        </header>
        <JobRunnerClient initialLogs={logs} />
      </div>
    </main>
  );
}
