import Link from "next/link";
import { Nav } from "@/components/Nav";
import { RiskBadge } from "@/components/RiskBadge";
import { getDistricts, getDisasterRisk } from "@/lib/api";

export default async function DistrictsPage() {
  const [districts, disasterRisk] = await Promise.all([getDistricts(), getDisasterRisk()]);
  const riskByDistrict = new Map(disasterRisk.map((risk) => [risk.district_id, risk]));

  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">District Intelligence</p>
          <h1 className="text-3xl font-bold">NCR District Drilldowns</h1>
        </header>
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {districts.map((district) => {
            const risk = riskByDistrict.get(district.ward_id);
            return (
              <Link className="rounded-lg border border-civic-line bg-white p-4 shadow-sm hover:border-civic-blue" href={`/districts/${district.ward_id}`} key={district.ward_id}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="font-semibold">{district.ward_name}</h2>
                    <p className="text-sm text-slate-500">{district.state} · {(district.population / 1000000).toFixed(1)}M people</p>
                  </div>
                  <RiskBadge level={risk?.overall.level || district.risk_level} />
                </div>
                <p className="mt-3 text-sm text-slate-600">{district.disaster_profile}</p>
                <p className="mt-3 text-sm font-medium">Disaster score {risk?.overall.score ?? "N/A"}</p>
              </Link>
            );
          })}
        </section>
      </div>
    </main>
  );
}
