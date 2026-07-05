from __future__ import annotations

import json
import urllib.request

from app.config import get_settings
from app.services.assistant_context_service import demo_assistant_response
from app.services.anomaly_engine import detect_anomalies
from app.services.data_loader import load_all_data
from app.services.rag_engine import retrieve_context
from app.services.recommendation_engine import generate_recommendations
from app.services.risk_engine import calculate_ward_risk_scores


SYSTEM_CONTEXT = """
You are CivicIQ, the NCR Disaster and Civic Decision Intelligence Assistant.
Answer questions about NCR district risk, flood risk, heatwave risk, AQI/public health,
traffic disruption, alerts, responsible departments, incident briefs, and 24-hour priorities.
Always include a direct answer, evidence, affected districts, recommended department,
recommended actions, confidence level, and data limitations.
Do not claim certainty when data is incomplete. Do not issue official emergency orders.
Recommend escalation to official authorities for critical events. Label AI recommendations
as decision support. Use vulnerable population data only for service prioritization.
""".strip()


def answer_question(question: str) -> dict[str, object]:
    if _is_demo_question(question) or not get_settings().gemini_api_key:
        return demo_assistant_response(question)

    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    sources = retrieve_context(question)
    recommendations = generate_recommendations(data, scores)
    anomalies = detect_anomalies(data)

    if get_settings().gemini_api_key:
        gemini_answer = _try_gemini_answer(question, scores, sources, recommendations, anomalies)
        if gemini_answer:
            return gemini_answer

    return _mock_answer(question, scores, sources, recommendations, anomalies)


def _is_demo_question(question: str) -> bool:
    keywords = [
        "gurugram",
        "delhi",
        "noida",
        "ghaziabad",
        "meerut",
        "ncr crisis",
        "leadership",
        "next 24",
        "industrial",
        "heatwave",
        "aqi",
        "flood",
    ]
    lowered = question.lower()
    return any(keyword in lowered for keyword in keywords)


def _mock_answer(
    question: str,
    scores,
    sources: list[dict[str, str]],
    recommendations: list[dict[str, object]],
    anomalies: list[dict[str, object]],
) -> dict[str, object]:
    top_wards = scores.head(3).to_dict(orient="records")
    top_ward = top_wards[0]
    recommended_actions = _flatten_actions(recommendations)[:5]

    key_evidence = [
        f"{ward['ward_name']} has a Community Risk Score of {ward['community_risk_score']} ({ward['risk_level']})."
        for ward in top_wards
    ]
    if anomalies:
        key_evidence.append(f"{len(anomalies)} anomaly signal(s) were detected, including {anomalies[0]['type']}.")

    answer = (
        "Summary: CivicIQ identifies "
        f"{top_ward['ward_name']} as the most urgent ward this week, with risk level "
        f"{top_ward['risk_level']} and score {top_ward['community_risk_score']}. "
        "Key Evidence: "
        + " ".join(key_evidence)
        + " Risk or Opportunity Level: "
        + str(top_ward["risk_level"])
        + ". Recommended Actions: "
        + " ".join(recommended_actions[:3])
        + " Data Limitations: Sample data is synthetic and forecasts are prototype estimates."
    )

    return {
        "answer": answer,
        "sources": [{"source": item["source"], "chunk_id": item["chunk_id"]} for item in sources],
        "related_metrics": [
            {
                "ward_id": ward["ward_id"],
                "ward_name": ward["ward_name"],
                "community_risk_score": ward["community_risk_score"],
                "risk_level": ward["risk_level"],
                "complaint_volume": ward["complaint_volume"],
                "aqi": round(float(ward["aqi"]), 1),
                "outage_count": ward["outage_count"],
            }
            for ward in top_wards
        ],
        "recommended_actions": recommended_actions,
        "risk_or_opportunity_level": str(top_ward["risk_level"]),
        "data_limitations": [
            "Sample data is synthetic for prototype demonstration.",
            "Forecasts and recommendations support human review; they are not final emergency decisions.",
            "Vulnerable population percentage is used only to prioritize service support.",
        ],
    }


def _try_gemini_answer(
    question: str,
    scores,
    sources: list[dict[str, str]],
    recommendations: list[dict[str, object]],
    anomalies: list[dict[str, object]],
) -> dict[str, object] | None:
    api_key = get_settings().gemini_api_key
    if not api_key:
        return None

    prompt = {
        "system_context": SYSTEM_CONTEXT,
        "question": question,
        "top_risk_wards": scores.head(5).to_dict(orient="records"),
        "retrieved_context": sources,
        "recommendations": recommendations[:5],
        "anomalies": anomalies[:6],
        "response_format": [
            "Summary",
            "Key Evidence",
            "Risk or Opportunity Level",
            "Recommended Actions",
            "Data Limitations",
        ],
    }

    request_body = json.dumps({"contents": [{"parts": [{"text": json.dumps(prompt)}]}]}).encode("utf-8")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )

    try:
        request = urllib.request.Request(
            url,
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

    return {
        "answer": text,
        "sources": [{"source": item["source"], "chunk_id": item["chunk_id"]} for item in sources],
        "related_metrics": scores.head(3).to_dict(orient="records"),
        "recommended_actions": _flatten_actions(recommendations)[:5],
        "risk_or_opportunity_level": str(scores.iloc[0]["risk_level"]),
        "data_limitations": [
            "Gemini response is grounded with retrieved local context and synthetic sample data.",
            "Predictions are estimates and require human validation.",
        ],
    }


def _flatten_actions(recommendations: list[dict[str, object]]) -> list[str]:
    actions = []
    for recommendation in recommendations:
        for action in recommendation.get("actions", []):
            actions.append(f"{recommendation['ward_name']}: {action}")
    return actions or ["Maintain monitoring and review service performance weekly."]
