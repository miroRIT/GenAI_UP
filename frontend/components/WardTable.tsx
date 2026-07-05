"use client";

import { useMemo, useState } from "react";
import { Ward } from "@/lib/api";
import { RiskBadge } from "./RiskBadge";

export function WardTable({ wards }: { wards: Ward[] }) {
  const [riskFilter, setRiskFilter] = useState("All");
  const filteredWards = useMemo(
    () => wards.filter((ward) => riskFilter === "All" || ward.risk_level === riskFilter),
    [riskFilter, wards],
  );

  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-lg font-semibold">Ward Intelligence</h2>
        <select
          className="rounded-md border border-civic-line px-3 py-2 text-sm"
          onChange={(event) => setRiskFilter(event.target.value)}
          value={riskFilter}
        >
          {["All", "Low", "Medium", "High", "Critical"].map((level) => (
            <option key={level}>{level}</option>
          ))}
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              <th className="py-2">Ward</th>
              <th>Risk</th>
              <th>Score</th>
              <th>Complaints</th>
              <th>AQI</th>
              <th>Outages</th>
              <th>Healthcare Wait</th>
            </tr>
          </thead>
          <tbody>
            {filteredWards.map((ward) => (
              <tr className="border-t border-slate-100" key={ward.ward_id}>
                <td className="py-3 font-medium">{ward.ward_name}</td>
                <td><RiskBadge level={ward.risk_level} /></td>
                <td>{ward.community_risk_score}</td>
                <td>{ward.complaint_volume}</td>
                <td>{Math.round(ward.aqi)}</td>
                <td>{ward.outage_count}</td>
                <td>{ward.appointments_wait_days} days</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {filteredWards.length === 0 ? <p className="py-8 text-center text-slate-500">No wards match this filter.</p> : null}
    </section>
  );
}
