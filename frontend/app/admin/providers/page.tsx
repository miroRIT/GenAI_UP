import { Nav } from "@/components/Nav";
import { ProviderStatusClient } from "@/components/ProviderStatusClient";

export default function ProvidersPage() {
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Admin</p>
          <h1 className="text-3xl font-bold">Provider Health</h1>
          <p className="mt-2 text-sm text-slate-600">Check live/fallback source status for news, weather, traffic, and geospatial feeds.</p>
        </header>
        <ProviderStatusClient />
      </div>
    </main>
  );
}
