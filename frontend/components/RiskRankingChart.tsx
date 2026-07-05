"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Ward } from "@/lib/api";

export function RiskRankingChart({ wards }: { wards: Ward[] }) {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={wards}>
          <CartesianGrid strokeDasharray="3 3" stroke="#DCE3EC" />
          <XAxis dataKey="ward_name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="community_risk_score" fill="#DC2626" name="Risk Score" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
