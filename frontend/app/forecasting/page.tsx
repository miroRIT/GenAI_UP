import { ForecastChart } from "@/components/ForecastChart";
import { Nav } from "@/components/Nav";
import { getForecast } from "@/lib/api";

export default async function ForecastingPage() {
  const [complaints, aqi, outages] = await Promise.all([
    getForecast("complaints"),
    getForecast("aqi"),
    getForecast("outages"),
  ]);

  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Forecasting</p>
          <h1 className="text-3xl font-bold text-civic-ink">Prototype Risk Forecasts</h1>
          <p className="mt-2 text-sm text-slate-600">Forecasts are moving-average prototype estimates for planning support.</p>
        </header>
        <div className="grid gap-6 lg:grid-cols-3">
          <ForecastChart title="Complaint Forecast" data={[...complaints.history, ...complaints.forecast]} />
          <ForecastChart title="AQI Forecast" data={[...aqi.history, ...aqi.forecast]} />
          <ForecastChart title="Outage Forecast" data={[...outages.history, ...outages.forecast]} />
        </div>
      </div>
    </main>
  );
}
