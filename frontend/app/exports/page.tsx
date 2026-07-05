import { Download } from "lucide-react";
import { Nav } from "@/components/Nav";
import { getExports } from "@/lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default async function ExportsPage() {
  const exports = await getExports();
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Exports</p>
          <h1 className="text-3xl font-bold">Local Demo Briefs and Reports</h1>
          <p className="mt-2 text-sm text-slate-600">These links simulate signed URLs. Production path: Cloud Storage signed URLs with expiry and audit logging.</p>
        </header>
        <section className="grid gap-3 md:grid-cols-2">
          {exports.map((item) => (
            <article className="rounded-lg border border-civic-line bg-white p-4 shadow-sm" key={item.export_id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold">{item.title}</h2>
                  <p className="mt-1 text-sm text-slate-600">{item.storage_mode} / expires in {item.expires_in_minutes} minutes</p>
                </div>
                <a className="rounded-md bg-civic-blue p-2 text-white" href={`${API_BASE_URL}${item.download_url}`}>
                  <Download className="h-4 w-4" />
                </a>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
