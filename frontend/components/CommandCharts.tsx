"use client";

import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Alert, OperationsSnapshot } from "@/lib/api";
import { EmptyState, SectionCard } from "./UIPrimitives";

const colors: Record<string, string> = {
  Critical: "#dc2626",
  High: "#ea580c",
  Medium: "#ca8a04",
  Low: "#16a34a",
  "On Track": "#16a34a",
  "At Risk": "#ca8a04",
  Breached: "#dc2626",
};

export function AlertSeverityChart({ alerts }: { alerts: Alert[] }) {
  const data = ["Critical", "High", "Medium", "Low"].map((name) => ({ name, value: alerts.filter((alert) => alert.severity === name).length }));
  return (
    <SectionCard title="Alert Severity Distribution">
      {alerts.length ? <ChartBox><PieChart><Pie data={data} dataKey="value" nameKey="name" outerRadius={86} label>{data.map((item) => <Cell key={item.name} fill={colors[item.name]} />)}</Pie><Tooltip /></PieChart></ChartBox> : <EmptyState label="No alerts found for severity chart." />}
    </SectionCard>
  );
}

export function DepartmentWorkloadChart({ alerts }: { alerts: Alert[] }) {
  const departments = ["Municipal Corporation", "Traffic Police", "Fire Department", "Health Department", "Disaster Management Authority", "Electricity Utility", "Water Department"];
  const data = departments.map((name) => ({ name, alerts: alerts.filter((alert) => alert.assigned_department === name).length }));
  return (
    <SectionCard title="Department Workload">
      {alerts.length ? <ChartBox><BarChart data={data} layout="vertical" margin={{ left: 120 }}><CartesianGrid strokeDasharray="3 3" /><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11 }} /><Tooltip /><Bar dataKey="alerts" fill="#2563eb" radius={[0, 6, 6, 0]} /></BarChart></ChartBox> : <EmptyState label="No department workload available." />}
    </SectionCard>
  );
}

export function SlaRiskChart({ alerts }: { alerts: Alert[] }) {
  const data = ["On Track", "At Risk", "Breached"].map((name) => ({ name, value: alerts.filter((alert) => (alert.sla_status || "On Track") === name).length }));
  return (
    <SectionCard title="SLA Risk">
      {alerts.length ? <ChartBox height="h-56"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="value" radius={[6, 6, 0, 0]}>{data.map((item) => <Cell key={item.name} fill={colors[item.name]} />)}</Bar></BarChart></ChartBox> : <EmptyState label="No SLA records available." />}
    </SectionCard>
  );
}

export function ProviderFreshnessTrend({ operations }: { operations: OperationsSnapshot }) {
  const data = operations.provider_health.map((provider, index) => ({
    provider: provider.provider.replace("NewsAPI/GDELT", "News"),
    minutes: Number(provider.freshness.match(/\d+/)?.[0] || 10) + index,
  }));
  data.push({ provider: "AQI", minutes: 9 }, { provider: "Map Layer", minutes: 20 });
  return (
    <SectionCard title="Provider Freshness Trend">
      <ChartBox height="h-64"><LineChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="provider" /><YAxis label={{ value: "minutes", angle: -90, position: "insideLeft" }} /><Tooltip /><Line type="monotone" dataKey="minutes" stroke="#2563eb" strokeWidth={3} /></LineChart></ChartBox>
    </SectionCard>
  );
}

export function JobHealthSummaryChart({ operations }: { operations: OperationsSnapshot }) {
  return (
    <SectionCard title="Job Health Summary">
      <ChartBox height="h-64"><BarChart data={operations.job_health}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="job" tick={{ fontSize: 10 }} /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="records" fill="#0891b2" radius={[6, 6, 0, 0]} /></BarChart></ChartBox>
    </SectionCard>
  );
}

function ChartBox({ children, height = "h-72" }: { children: React.ReactElement; height?: string }) {
  return <div className={`${height} w-full`}><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></div>;
}
