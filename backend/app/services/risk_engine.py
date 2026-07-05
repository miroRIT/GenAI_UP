from __future__ import annotations

import pandas as pd


RISK_WEIGHTS = {
    "complaint_score": 0.20,
    "emergency_score": 0.15,
    "air_quality_score": 0.15,
    "utility_score": 0.15,
    "healthcare_score": 0.15,
    "waste_score": 0.10,
    "vulnerable_population_score": 0.10,
}


def calculate_ward_risk_scores(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    wards = data["wards"].copy()
    complaint_features = _complaint_features(data["citizen_complaints"])
    emergency_features = _count_by_ward(data["emergency_incidents"], "emergency_count")
    outage_features = _count_by_ward(data["utility_outages"], "outage_count")
    aqi_features = data["air_quality"].groupby("ward_id", as_index=False)["aqi"].mean()
    waste_features = (
        data["waste_collection"]
        .groupby("ward_id", as_index=False)[["delayed_routes", "missed_pickups"]]
        .sum()
    )
    healthcare_features = data["healthcare_access"].copy()

    scores = (
        wards.merge(complaint_features, on="ward_id", how="left")
        .merge(emergency_features, on="ward_id", how="left")
        .merge(outage_features, on="ward_id", how="left")
        .merge(aqi_features, on="ward_id", how="left")
        .merge(waste_features, on="ward_id", how="left")
        .merge(healthcare_features, on="ward_id", how="left")
        .fillna(0)
    )

    scores["complaint_score"] = _normalize(
        scores["complaint_volume"] * 0.65 + scores["complaint_growth_rate"].clip(lower=0) * 0.35
    )
    scores["emergency_score"] = _normalize(scores["emergency_count"])
    scores["air_quality_score"] = _normalize(scores["aqi"])
    scores["utility_score"] = _normalize(scores["outage_count"])
    scores["healthcare_score"] = _normalize(
        scores["average_distance_km"] * 0.55 + scores["appointments_wait_days"] * 0.45
    )
    scores["waste_score"] = _normalize(scores["delayed_routes"] + scores["missed_pickups"] * 0.25)
    scores["vulnerable_population_score"] = _normalize(scores["vulnerable_population_percentage"])

    scores["community_risk_score"] = round(
        sum(scores[column] * weight for column, weight in RISK_WEIGHTS.items()),
        1,
    )
    scores["risk_level"] = scores["community_risk_score"].apply(classify_risk)

    return scores[
        [
            "ward_id",
            "ward_name",
            "population",
            "vulnerable_population_percentage",
            "average_income_band",
            "service_coverage_score",
            "latitude",
            "longitude",
            "community_risk_score",
            "risk_level",
            "complaint_volume",
            "complaint_growth_rate",
            "emergency_count",
            "aqi",
            "outage_count",
            "average_distance_km",
            "appointments_wait_days",
            "delayed_routes",
            "missed_pickups",
            "complaint_score",
            "emergency_score",
            "air_quality_score",
            "utility_score",
            "healthcare_score",
            "waste_score",
            "vulnerable_population_score",
        ]
    ].sort_values("community_risk_score", ascending=False)


def get_ward_detail(
    data: dict[str, pd.DataFrame],
    scores: pd.DataFrame,
    ward_id: str,
) -> dict[str, object] | None:
    match = scores[scores["ward_id"] == ward_id]
    if match.empty:
        return None

    detail = match.iloc[0].to_dict()
    detail["recent_complaints"] = (
        data["citizen_complaints"][data["citizen_complaints"]["ward_id"] == ward_id]
        .tail(10)
        .to_dict(orient="records")
    )
    detail["recent_emergency_incidents"] = (
        data["emergency_incidents"][data["emergency_incidents"]["ward_id"] == ward_id]
        .tail(10)
        .to_dict(orient="records")
    )
    return detail


def classify_risk(score: float) -> str:
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Medium"
    if score <= 80:
        return "High"
    return "Critical"


def _complaint_features(complaints: pd.DataFrame) -> pd.DataFrame:
    complaint_counts = complaints.groupby("ward_id", as_index=False).size()
    complaint_counts = complaint_counts.rename(columns={"size": "complaint_volume"})

    complaints = complaints.copy()
    complaints["date"] = pd.to_datetime(complaints["date"])
    midpoint = complaints["date"].min() + (complaints["date"].max() - complaints["date"].min()) / 2
    earlier = complaints[complaints["date"] <= midpoint].groupby("ward_id").size()
    recent = complaints[complaints["date"] > midpoint].groupby("ward_id").size()
    growth = ((recent - earlier) / earlier.replace(0, 1) * 100).fillna(0)

    return complaint_counts.merge(
        growth.rename("complaint_growth_rate").reset_index(),
        on="ward_id",
        how="left",
    ).fillna(0)


def _count_by_ward(dataframe: pd.DataFrame, output_column: str) -> pd.DataFrame:
    return dataframe.groupby("ward_id", as_index=False).size().rename(columns={"size": output_column})


def _normalize(series: pd.Series) -> pd.Series:
    minimum = float(series.min())
    maximum = float(series.max())
    if maximum == minimum:
        return pd.Series([50.0] * len(series), index=series.index)
    return round(((series - minimum) / (maximum - minimum)) * 100, 1)
