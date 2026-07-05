"use client";

import { useMemo, useState } from "react";
import { Alert, assignAlert, transitionAlert } from "@/lib/api";
import { RiskBadge } from "./RiskBadge";
import { DemoBadge, EmptyState, SectionCard } from "./UIPrimitives";

const departments = [
  "District Administration",
  "Disaster Management Authority",
  "Traffic Police",
  "Fire Department",
  "Health Department",
  "Municipal Corporation",
  "Pollution Control Board",
  "Electricity Utility",
  "Water Department",
  "Public Works Department",
];

export function AlertsClient({ initialAlerts }: { initialAlerts: Alert[] }) {
  const [alerts, setAlerts] = useState(initialAlerts);
  const [filter, setFilter] = useState("All");
  const user = useMemo(() => {
    if (typeof window === "undefined") {
      return null;
    }
    const stored = window.localStorage.getItem("civiciq_user");
    return stored ? JSON.parse(stored) : null;
  }, []);
  const canAssign = user?.role === "Admin" || user?.role === "District Officer";
  const canResolve = ["Admin", "District Officer", "Department User"].includes(user?.role);

  const visibleAlerts = alerts.filter((alert) => filter === "All" || alert.status === filter || alert.severity === filter);

  async function refreshAlert(updatedAlert: Alert) {
    setAlerts((current) => current.map((alert) => (alert.alert_id === updatedAlert.alert_id ? updatedAlert : alert)));
  }

  async function downloadPdf(alertId: string) {
    const token = window.localStorage.getItem("civiciq_token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"}/api/alerts/${alertId}/export.pdf`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      throw new Error("PDF export failed");
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${alertId}-incident-brief.pdf`;
    anchor.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <SectionCard title="Operational Alerts" badge={<DemoBadge label="Generated Briefs" />}>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <select className="rounded-md border border-civic-line px-3 py-2 text-sm" value={filter} onChange={(event) => setFilter(event.target.value)}>
          {["All", "New", "Acknowledged", "In Progress", "Resolved", "Closed", "Critical", "High", "Medium", "Low"].map((option) => <option key={option}>{option}</option>)}
        </select>
      </div>
      {visibleAlerts.length === 0 ? <EmptyState label="No alerts found for this filter." /> : <div className="overflow-x-auto">
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              <th className="py-2">Alert</th>
              <th>District</th>
              <th>Category</th>
              <th>Severity</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Department</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {visibleAlerts.map((alert) => (
              <tr className="border-t border-slate-100 align-top" key={alert.alert_id}>
                <td className="py-3">
                  <p className="font-medium">{alert.title}</p>
                  <button className="text-xs text-civic-blue" onClick={() => downloadPdf(alert.alert_id)} type="button">
                    PDF brief
                  </button>
                </td>
                <td>{alert.district_name}</td>
                <td>{alert.category}</td>
                <td><RiskBadge level={alert.severity} /></td>
                <td>{alert.priority}</td>
                <td>{alert.status}</td>
                <td>
                  <select
                    className="max-w-44 rounded-md border border-slate-200 px-2 py-1"
                    disabled={!canAssign}
                    value={alert.assigned_department}
                    onChange={async (event) => refreshAlert(await assignAlert(alert.alert_id, event.target.value, alert.priority))}
                  >
                    {departments.map((department) => <option key={department}>{department}</option>)}
                  </select>
                </td>
                <td>
                  <div className="flex flex-wrap gap-2">
                    <button className="rounded-md bg-slate-100 px-2 py-1 disabled:opacity-50" disabled={!canResolve} onClick={async () => refreshAlert(await transitionAlert(alert.alert_id, "acknowledge", "Acknowledged from UI"))}>Ack</button>
                    <button className="rounded-md bg-emerald-100 px-2 py-1 text-emerald-700 disabled:opacity-50" disabled={!canResolve} onClick={async () => refreshAlert(await transitionAlert(alert.alert_id, "resolve", "Resolved from UI"))}>Resolve</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>}
    </SectionCard>
  );
}
