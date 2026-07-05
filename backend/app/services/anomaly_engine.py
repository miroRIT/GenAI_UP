from __future__ import annotations

import pandas as pd


def detect_anomalies(data: dict[str, pd.DataFrame]) -> list[dict[str, object]]:
    anomalies: list[dict[str, object]] = []
    ward_names = data["wards"].set_index("ward_id")["ward_name"].to_dict()

    aqi = data["air_quality"]
    aqi_threshold = aqi["aqi"].mean() + (2 * aqi["aqi"].std())
    for _, row in aqi[aqi["aqi"] > aqi_threshold].iterrows():
        anomalies.append(
            {
                "type": "Air Quality Spike",
                "ward_id": row["ward_id"],
                "ward_name": ward_names.get(row["ward_id"], row["ward_id"]),
                "severity": "High",
                "metric": f"AQI {row['aqi']}",
                "explanation": "AQI is above the city mean plus two standard deviations.",
                "suggested_action": "Issue a public health advisory and inspect pollution sources.",
            }
        )

    complaints = data["citizen_complaints"].copy()
    complaints["date"] = pd.to_datetime(complaints["date"])
    daily = complaints.groupby(["ward_id", "date"], as_index=False).size()
    for ward_id, group in daily.groupby("ward_id"):
        recent_value = group.sort_values("date").tail(1)["size"].iloc[0]
        threshold = group["size"].mean() + group["size"].std()
        if recent_value > threshold:
            anomalies.append(
                {
                    "type": "Complaint Spike",
                    "ward_id": ward_id,
                    "ward_name": ward_names.get(ward_id, ward_id),
                    "severity": "Medium",
                    "metric": f"{int(recent_value)} complaints today",
                    "explanation": "Latest complaint volume is above the ward's normal range.",
                    "suggested_action": "Audit service queues and contact local response teams.",
                }
            )

    outage_counts = data["utility_outages"].groupby("ward_id", as_index=False).size()
    for _, row in outage_counts[outage_counts["size"] >= 9].iterrows():
        anomalies.append(
            {
                "type": "Utility Outage Frequency",
                "ward_id": row["ward_id"],
                "ward_name": ward_names.get(row["ward_id"], row["ward_id"]),
                "severity": "High",
                "metric": f"{int(row['size'])} outages in sample period",
                "explanation": "Outage frequency exceeds the prototype threshold.",
                "suggested_action": "Schedule utility inspection and resilience checks.",
            }
        )

    emergency_counts = data["emergency_incidents"].groupby("ward_id", as_index=False).size()
    emergency_threshold = emergency_counts["size"].mean() + emergency_counts["size"].std()
    for _, row in emergency_counts[emergency_counts["size"] > emergency_threshold].iterrows():
        anomalies.append(
            {
                "type": "Emergency Incident Load",
                "ward_id": row["ward_id"],
                "ward_name": ward_names.get(row["ward_id"], row["ward_id"]),
                "severity": "High",
                "metric": f"{int(row['size'])} incidents",
                "explanation": "Emergency incidents are above the city normal range.",
                "suggested_action": "Review response staging and preventive outreach.",
            }
        )

    return anomalies
