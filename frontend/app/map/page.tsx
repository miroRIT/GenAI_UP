import { MapShell } from "@/components/MapShell";
import { Nav } from "@/components/Nav";
import { getDemoMapLayers, getDistrictGeoJson } from "@/lib/api";

export default async function MapPage() {
  const [geojson, layers] = await Promise.all([getDistrictGeoJson(), getDemoMapLayers()]);
  const incidents = layers.incidents.map((incident) => ({
    ...incident,
    district_id: incident.incident_id,
    severity: incident.risk_level,
    timestamp: incident.updated_at,
    source: "CivicIQ Demo Scenario Engine",
    url: "",
    summary: `${incident.category} risk score ${incident.risk_score}`,
    recommended_action: "Open scenario explanation in Demo Mode",
  }));

  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">NCR Risk Map</p>
          <h1 className="text-3xl font-bold">Disaster-Prone Areas and Active Incidents</h1>
          <p className="mt-2 text-sm text-slate-600">
            {layers.boundary_source.source_name}. Production sources: {layers.boundary_source.production_source_options.join(", ")}.
          </p>
        </header>
        <MapShell geojson={geojson} incidents={incidents} />
      </div>
    </main>
  );
}
