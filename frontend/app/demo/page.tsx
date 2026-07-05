import { DemoModeClient } from "@/components/DemoModeClient";
import { NCRCrisisSummaryCard } from "@/components/NCRCrisisSummaryCard";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/UIPrimitives";
import { getCrisisSummary, getDemoOverview, getDemoRecommendations } from "@/lib/api";

export default async function DemoPage() {
  const [overview, recommendations, summary] = await Promise.all([getDemoOverview(), getDemoRecommendations(), getCrisisSummary()]);

  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <PageHeader
          eyebrow="CivicIQ Demo Mode"
          title={overview.tagline}
          description="A judge-ready crisis walkthrough for Delhi, Gurugram, Noida, Ghaziabad, and Meerut."
        />
        <div className="mb-6">
          <NCRCrisisSummaryCard summary={summary} />
        </div>
        <DemoModeClient overview={overview} recommendations={recommendations} />
      </div>
    </main>
  );
}
