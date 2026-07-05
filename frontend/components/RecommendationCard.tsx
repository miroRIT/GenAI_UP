import { Recommendation } from "@/lib/api";
import { RiskBadge } from "./RiskBadge";

export function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
  return (
    <article className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-civic-ink">{recommendation.ward_name}</h3>
          <p className="text-sm text-slate-500">Score {recommendation.community_risk_score}</p>
        </div>
        <RiskBadge level={recommendation.risk_level} />
      </div>
      <ul className="mt-3 space-y-2 text-sm text-slate-700">
        {recommendation.actions.slice(0, 4).map((action) => (
          <li key={action}>{action}</li>
        ))}
      </ul>
    </article>
  );
}
