import { MapShell } from "@/components/MapShell";
import { Nav } from "@/components/Nav";
import { RecommendationCard } from "@/components/RecommendationCard";
import { RiskBadge } from "@/components/RiskBadge";
import { getDistrictDetail, getDistrictGeoJson } from "@/lib/api";

export default async function DistrictPage({ params }: { params: Promise<{ districtId: string }> }) {
  const { districtId } = await params;
  const [district, geojson] = await Promise.all([getDistrictDetail(districtId), getDistrictGeoJson()]);
  const risks = Object.entries(district.disaster_risk.risks);

  return (
    <main>
      <Nav />
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-6">
        <header>
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">{district.state}</p>
          <h1 className="text-3xl font-bold">{district.ward_name}</h1>
          <p className="mt-2 text-sm text-slate-600">{district.disaster_profile}</p>
        </header>
        <section className="grid gap-3 md:grid-cols-4">
          <Metric label="Population" value={`${(district.population / 1000000).toFixed(1)}M`} />
          <Metric label="Area" value={`${district.area_sq_km} sq km`} />
          <Metric label="Overall Disaster Risk" value={district.disaster_risk.overall.score} />
          <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">Risk Level</p>
            <div className="mt-3"><RiskBadge level={district.disaster_risk.overall.level} /></div>
          </div>
        </section>
        <section className="grid gap-4 md:grid-cols-3">
          {risks.map(([name, risk]) => (
            <article className="rounded-lg border border-civic-line bg-white p-4 shadow-sm" key={name}>
              <div className="flex items-center justify-between gap-3">
                <h2 className="font-semibold capitalize">{name.replaceAll("_", " ")}</h2>
                <RiskBadge level={risk.level} />
              </div>
              <p className="mt-2 text-2xl font-semibold">{risk.score}</p>
              <p className="mt-2 text-sm text-slate-600">{risk.explanation}</p>
            </article>
          ))}
        </section>
        <MapShell geojson={geojson} incidents={district.incidents} />
        <section className="grid gap-4 lg:grid-cols-2">
          <Panel title="Active Alerts" items={district.alerts.map((alert) => `${alert.priority} · ${alert.status} · ${alert.title}`)} />
          <Panel title="Recent Incidents" items={district.incidents.map((incident) => `${incident.severity} · ${incident.category} · ${incident.title}`)} />
          <Panel title="Weather Summary" items={[JSON.stringify(district.weather)]} />
          <Panel title="Traffic Summary" items={[JSON.stringify(district.traffic)]} />
        </section>
        <RecommendationCard recommendation={{
          ward_id: district.ward_id,
          ward_name: district.ward_name,
          risk_level: district.disaster_risk.overall.level,
          community_risk_score: district.disaster_risk.overall.score,
          actions: district.recommendations,
        }} />
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function Panel({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <h2 className="font-semibold">{title}</h2>
      <ul className="mt-3 space-y-2 text-sm text-slate-700">
        {(items.length ? items : ["No current records."]).slice(0, 6).map((item) => <li key={item}>{item}</li>)}
      </ul>
    </section>
  );
}
