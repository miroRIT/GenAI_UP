import { DemoModeClient } from "@/components/DemoModeClient";
import { Nav } from "@/components/Nav";
import { getDemoOverview, getDemoRecommendations } from "@/lib/api";

export default async function DemoPage() {
  const [overview, recommendations] = await Promise.all([getDemoOverview(), getDemoRecommendations()]);

  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">CivicIQ Demo Mode</p>
          <h1 className="text-3xl font-bold">{overview.tagline}</h1>
          <p className="mt-2 text-sm text-slate-600">A judge-ready crisis walkthrough for Delhi, Gurugram, Noida, Ghaziabad, and Meerut.</p>
        </header>
        <DemoModeClient overview={overview} recommendations={recommendations} />
      </div>
    </main>
  );
}
