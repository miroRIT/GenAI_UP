from __future__ import annotations

from datetime import timedelta

import pandas as pd


def generate_forecast(
    data: dict[str, pd.DataFrame],
    metric: str = "complaints",
    periods: int = 7,
) -> dict[str, object]:
    history = _history_for_metric(data, metric)
    history["date"] = pd.to_datetime(history["date"])
    history = history.sort_values("date")
    values = history["value"].astype(float).tolist()
    last_date = history["date"].max()

    moving_average = pd.Series(values).tail(7).mean()
    trend = _simple_trend(values)

    forecast = []
    for step in range(1, periods + 1):
        forecast.append(
            {
                "date": (last_date + timedelta(days=step)).date().isoformat(),
                "value": round(max(0, moving_average + trend * step), 1),
            }
        )

    return {
        "metric": metric,
        "method": "7-day moving average with simple trend adjustment",
        "note": "Prototype estimate only. Do not use as the sole basis for emergency decisions.",
        "history": history.tail(14).to_dict(orient="records"),
        "forecast": forecast,
    }


def _history_for_metric(data: dict[str, pd.DataFrame], metric: str) -> pd.DataFrame:
    if metric == "complaints":
        return (
            data["citizen_complaints"]
            .groupby("date", as_index=False)
            .size()
            .rename(columns={"size": "value"})
        )
    if metric == "aqi":
        return data["air_quality"].groupby("date", as_index=False)["aqi"].mean().rename(columns={"aqi": "value"})
    if metric == "outages":
        return (
            data["utility_outages"]
            .groupby("date", as_index=False)
            .size()
            .rename(columns={"size": "value"})
        )

    raise ValueError(f"Unsupported forecast metric: {metric}")


def _simple_trend(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return (sum(values[-7:]) / min(7, len(values)) - sum(values[:7]) / min(7, len(values))) / max(1, len(values))
