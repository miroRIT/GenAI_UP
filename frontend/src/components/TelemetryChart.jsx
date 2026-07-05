import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function TelemetryChart({ records }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold">Sector Stress Index</h2>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={records} margin={{ top: 8, right: 8, left: 0, bottom: 32 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis
              dataKey="sector_name"
              interval={0}
              angle={-18}
              textAnchor="end"
              tick={{ fontSize: 11 }}
            />
            <YAxis />
            <Tooltip />
            <Bar dataKey="traffic_congestion_level" fill="#2563EB" name="Congestion" />
            <Bar dataKey="decision_priority_score" fill="#DC2626" name="Priority" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
