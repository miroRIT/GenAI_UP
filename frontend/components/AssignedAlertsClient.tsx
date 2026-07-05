"use client";

import { useEffect, useState } from "react";
import { Alert, getAssignedAlerts, transitionAlert } from "@/lib/api";
import { RiskBadge } from "./RiskBadge";

export function AssignedAlertsClient() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [message, setMessage] = useState("Loading assigned alerts...");

  useEffect(() => {
    getAssignedAlerts()
      .then((items) => {
        setAlerts(items);
        setMessage(items.length ? "" : "No assigned alerts found for the current user.");
      })
      .catch(() => setMessage("Login as an authority user to view assigned alerts."));
  }, []);

  async function resolve(alert: Alert) {
    const updated = await transitionAlert(alert.alert_id, "resolve", "Resolved from assigned workflow");
    setAlerts((current) => current.map((item) => (item.alert_id === updated.alert_id ? updated : item)));
  }

  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
      <div className="grid gap-3">
        {alerts.map((alert) => (
          <article className="rounded-md border border-slate-200 p-4" key={alert.alert_id}>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm text-slate-500">{alert.district_name} / {alert.assigned_department}</p>
                <h2 className="text-lg font-semibold">{alert.title}</h2>
                <p className="mt-2 text-sm text-slate-600">{alert.description}</p>
              </div>
              <RiskBadge level={alert.severity} />
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
              <span>Status: {alert.status}</span>
              <span>SLA: {alert.sla_status || "On Track"}</span>
              <button className="rounded-md bg-emerald-100 px-3 py-2 font-medium text-emerald-700" onClick={() => resolve(alert)} type="button">
                Mark Resolved
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
