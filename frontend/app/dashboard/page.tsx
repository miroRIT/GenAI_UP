import { AlertTriangle, Map, Siren, Users } from "lucide-react";
import { ChartCard } from "@/components/ChartCard";
import { KpiCard } from "@/components/KpiCard";
import { LiveMonitoringPanel } from "@/components/LiveMonitoringPanel";
import { MapShell } from "@/components/MapShell";
import { Nav } from "@/components/Nav";
import { RecommendationCard } from "@/components/RecommendationCard";
import { RiskRankingChart } from "@/components/RiskRankingChart";
import { getDistrictGeoJson, getGeoIncidents, getLiveMonitoring, getOverview, getRecommendations, getRiskRanking } from "@/lib/api";

export default async function DashboardPage() {
  const [overview, ranking, recommendations, geojson, incidents, monitoring] = await Promise.all([
    getOverview(),
    getRiskRanking(),
    getRecommendations(),
    getDistrictGeoJson(),
    getGeoIncidents(),
    getLiveMonitoring(),
  ]);

  return (
    <main>
      <Nav />
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-6">
        <header>
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">CivicIQ NCR Command Dashboard</p>
          <h1 className="text-3xl font-bold text-civic-ink">National Capital Region Risk Overview</h1>
          <p className="mt-2 text-sm text-slate-600">Approx. 7.5 crore people across 55,083 sq km, spanning Delhi, Haryana, Uttar Pradesh, and Rajasthan NCR districts.</p>
        </header>
        <section className="grid gap-3 md:grid-cols-4">
          <KpiCard icon={Users} label="NCR Population" value={`${((overview.total_population as number) / 10000000).toFixed(1)} crore`} />
          <KpiCard icon={Map} label="Area Covered" value={`${overview.total_area_sq_km} sq km`} />
          <KpiCard icon={AlertTriangle} label="Average Risk" value={overview.average_risk_score} />
          <KpiCard icon={Siren} label="Emergency Incidents" value={overview.total_emergency_incidents} />
        </section>
        <LiveMonitoringPanel
          updatedAt={monitoring.updated_at}
          mode={monitoring.mode}
          feeds={{
            weather: monitoring.weather,
            traffic: monitoring.traffic,
            news: monitoring.news,
            geospatial: monitoring.geospatial,
          }}
        />
        <MapShell geojson={geojson} incidents={incidents} />
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
