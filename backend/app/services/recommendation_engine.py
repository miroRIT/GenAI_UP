from __future__ import annotations

import pandas as pd


def generate_recommendations(
    data: dict[str, pd.DataFrame],
    ward_scores: pd.DataFrame,
) -> list[dict[str, object]]:
    recommendations = []
    for _, ward in ward_scores[ward_scores["risk_level"].isin(["High", "Critical"])].iterrows():
        recommendations.append(
            {
                "ward_id": ward["ward_id"],
                "ward_name": ward["ward_name"],
                "risk_level": ward["risk_level"],
                "community_risk_score": ward["community_risk_score"],
                "actions": get_recommendations_for_ward(ward.to_dict()),
            }
        )
    return recommendations


def get_recommendations_for_ward(ward: dict[str, object]) -> list[str]:
    actions: list[str] = []

    if float(ward.get("air_quality_score", 0)) >= 65:
        actions.append("Run pollution source checks and prepare a public health advisory.")
    if float(ward.get("complaint_score", 0)) >= 65:
        actions.append("Audit complaint queues and deploy a rapid service response team.")
    if float(ward.get("utility_score", 0)) >= 65:
        actions.append("Schedule utility inspection for recurring outage corridors.")
    if float(ward.get("healthcare_score", 0)) >= 65:
        actions.append("Launch a mobile health camp and review clinic appointment capacity.")
    if float(ward.get("waste_score", 0)) >= 65:
        actions.append("Optimize waste collection routes and inspect missed pickup clusters.")
    if float(ward.get("emergency_score", 0)) >= 65:
        actions.append("Rebalance emergency response staging for peak incident windows.")
    if float(ward.get("vulnerable_population_score", 0)) >= 65:
        actions.append("Prioritize outreach resources for residents with higher service needs.")

    if not actions:
        actions.append("Maintain monitoring and review service coverage weekly.")

    return actions
