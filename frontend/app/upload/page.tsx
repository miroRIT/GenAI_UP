import { Nav } from "@/components/Nav";

const schemas = [
  "wards: ward_id, ward_name, population, vulnerable_population_percentage, average_income_band, service_coverage_score, latitude, longitude",
  "citizen_complaints: complaint_id, ward_id, date, category, status, resolution_time_hours",
  "air_quality: ward_id, date, aqi, pm25, source",
  "utility_outages: outage_id, ward_id, date, utility_type, affected_households, duration_hours",
];

export default function UploadPage() {
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-4xl px-5 py-6">
        <section className="rounded-lg border border-civic-line bg-white p-5 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Data Upload</p>
          <h1 className="mt-1 text-3xl font-bold text-civic-ink">Bring Your Own Civic CSV</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The backend supports CSV upload through POST /api/upload with a dataset category and file.
            This page documents the prototype schemas; sample data works out of the box.
          </p>
          <div className="mt-5 rounded-md border border-dashed border-civic-line bg-slate-50 p-5 text-sm text-slate-600">
            UI upload wiring is intentionally simple for the hackathon prototype. Use the API endpoint
            directly or reset to generated sample data with POST /api/upload/reset.
          </div>
          <h2 className="mt-6 font-semibold">Expected Schemas</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            {schemas.map((schema) => <li key={schema}>{schema}</li>)}
          </ul>
        </section>
      </div>
    </main>
  );
}
