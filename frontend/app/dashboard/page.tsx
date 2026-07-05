import { AlertTriangle, Building2, Siren, UtilityPole } from "lucide-react";
import { ChartCard } from "@/components/ChartCard";
import { KpiCard } from "@/components/KpiCard";
import { Nav } from "@/components/Nav";
import { RecommendationCard } from "@/components/RecommendationCard";
import { RiskRankingChart } from "@/components/RiskRankingChart";
import { getOverview, getRecommendations, getRiskRanking } from "@/lib/api";

export default async function DashboardPage() {
  const [overview, ranking, recommendations] = await Promise.all([
    getOverview(),
    getRiskRanking(),
    getRecommendations(),
  ]);

  return (
    <main>
      <Nav />
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-6">
        <header>
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">CivicIQ Dashboard</p>
          <h1 className="text-3xl font-bold text-civic-ink">Community Risk Overview</h1>
        </header>
        <section className="grid gap-3 md:grid-cols-4">
          <KpiCard icon={Building2} label="Total Wards" value={overview.total_wards} />
          <KpiCard icon={AlertTriangle} label="Average Risk" value={overview.average_risk_score} />
          <KpiCard icon={Siren} label="Emergency Incidents" value={overview.total_emergency_incidents} />
          <KpiCard icon={UtilityPole} label="Utility Outages" value={overview.total_utility_outages} />
        </section>
        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.9fr]">
          <ChartCard title="Top High-Risk Wards">
            <RiskRankingChart wards={ranking.slice(0, 8)} />
          </ChartCard>
          <section className="grid gap-4">
            {recommendations.slice(0, 3).map((recommendation) => (
              <RecommendationCard key={recommendation.ward_id} recommendation={recommendation} />
            ))}
          </section>
        </div>
      </div>
    </main>
  );
}
