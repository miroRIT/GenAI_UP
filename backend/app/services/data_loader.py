from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from random import Random
from typing import Any

import pandas as pd
from fastapi import UploadFile

from app.config import get_settings


DATASET_FILENAMES = {
    "wards": "wards.csv",
    "citizen_complaints": "citizen_complaints.csv",
    "traffic": "traffic.csv",
    "air_quality": "air_quality.csv",
    "utility_outages": "utility_outages.csv",
    "healthcare_access": "healthcare_access.csv",
    "emergency_incidents": "emergency_incidents.csv",
    "waste_collection": "waste_collection.csv",
    "community_programs": "community_programs.csv",
}


def ensure_sample_data() -> None:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    if all((settings.data_dir / filename).exists() for filename in DATASET_FILENAMES.values()):
        return

    _write_sample_data(settings.data_dir)


def reset_sample_data() -> None:
    _write_sample_data(get_settings().data_dir)


def load_all_data() -> dict[str, pd.DataFrame]:
    ensure_sample_data()
    data_dir = get_settings().data_dir
    return {
        dataset_name: pd.read_csv(data_dir / filename)
        for dataset_name, filename in DATASET_FILENAMES.items()
    }


async def save_uploaded_dataset(category: str, file: UploadFile) -> int:
    content = await file.read()
    try:
        dataframe = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise ValueError(f"Could not parse uploaded CSV: {exc}") from exc

    output_path = get_settings().data_dir / DATASET_FILENAMES[category]
    dataframe.to_csv(output_path, index=False)
    return int(len(dataframe))


def _write_sample_data(data_dir: Path) -> None:
    randomizer = Random(42)
    wards = _build_wards()
    today = date.today()
    dates = [today - timedelta(days=day_offset) for day_offset in range(27, -1, -1)]

    wards.to_csv(data_dir / "wards.csv", index=False)
    _build_complaints(wards, dates, randomizer).to_csv(
        data_dir / "citizen_complaints.csv", index=False
    )
    _build_traffic(wards, dates, randomizer).to_csv(data_dir / "traffic.csv", index=False)
    _build_air_quality(wards, dates, randomizer).to_csv(
        data_dir / "air_quality.csv", index=False
    )
    _build_utility_outages(wards, dates, randomizer).to_csv(
        data_dir / "utility_outages.csv", index=False
    )
    _build_healthcare_access(wards, randomizer).to_csv(
        data_dir / "healthcare_access.csv", index=False
    )
    _build_emergency_incidents(wards, dates, randomizer).to_csv(
        data_dir / "emergency_incidents.csv", index=False
    )
    _build_waste_collection(wards, dates, randomizer).to_csv(
        data_dir / "waste_collection.csv", index=False
    )
    _build_community_programs(wards, dates, randomizer).to_csv(
        data_dir / "community_programs.csv", index=False
    )


def _build_wards() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ward_id": "W01",
                "ward_name": "Riverside Central",
                "population": 82000,
                "vulnerable_population_percentage": 18,
                "average_income_band": "Middle",
                "service_coverage_score": 76,
                "latitude": 1.3001,
                "longitude": 103.8519,
            },
            {
                "ward_id": "W02",
                "ward_name": "Northgate Estates",
                "population": 64000,
                "vulnerable_population_percentage": 22,
                "average_income_band": "Lower-Middle",
                "service_coverage_score": 69,
                "latitude": 1.3584,
                "longitude": 103.8292,
            },
            {
                "ward_id": "W03",
                "ward_name": "Harborview Industrial",
                "population": 51000,
                "vulnerable_population_percentage": 14,
                "average_income_band": "Mixed",
                "service_coverage_score": 61,
                "latitude": 1.2738,
                "longitude": 103.8097,
            },
            {
                "ward_id": "W04",
                "ward_name": "Eastwood Health Belt",
                "population": 73000,
                "vulnerable_population_percentage": 29,
                "average_income_band": "Lower-Middle",
                "service_coverage_score": 58,
                "latitude": 1.3297,
                "longitude": 103.9245,
            },
            {
                "ward_id": "W05",
                "ward_name": "Westlink Transit Hub",
                "population": 91000,
                "vulnerable_population_percentage": 16,
                "average_income_band": "Middle",
                "service_coverage_score": 72,
                "latitude": 1.3402,
                "longitude": 103.7068,
            },
            {
                "ward_id": "W06",
                "ward_name": "Lakeside Community",
                "population": 56000,
                "vulnerable_population_percentage": 25,
                "average_income_band": "Lower",
                "service_coverage_score": 54,
                "latitude": 1.3465,
                "longitude": 103.7221,
            },
            {
                "ward_id": "W07",
                "ward_name": "Innovation Quarter",
                "population": 47000,
                "vulnerable_population_percentage": 10,
                "average_income_band": "Upper-Middle",
                "service_coverage_score": 84,
                "latitude": 1.2934,
                "longitude": 103.7849,
            },
            {
                "ward_id": "W08",
                "ward_name": "South Market District",
                "population": 68000,
                "vulnerable_population_percentage": 21,
                "average_income_band": "Mixed",
                "service_coverage_score": 66,
                "latitude": 1.2823,
                "longitude": 103.8426,
            },
        ]
    )


def _build_complaints(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    categories = ["sanitation", "roads", "noise", "water", "electricity", "public safety"]
    rows: list[dict[str, Any]] = []
    complaint_id = 1

    for _, ward in wards.iterrows():
        baseline = max(6, int((100 - ward["service_coverage_score"]) / 2.8))
        for day_index, day in enumerate(dates):
            trend = 1 + (day_index / 95)
            if ward["ward_id"] in {"W04", "W06"}:
                trend += day_index / 58
            count = max(1, int(randomizer.gauss(baseline * trend, 2.2)))
            for _ in range(count):
                rows.append(
                    {
                        "complaint_id": f"C{complaint_id:05d}",
                        "ward_id": ward["ward_id"],
                        "date": day.isoformat(),
                        "category": randomizer.choice(categories),
                        "status": randomizer.choice(["open", "in_progress", "closed"]),
                        "resolution_time_hours": max(4, round(randomizer.gauss(35, 14), 1)),
                    }
                )
                complaint_id += 1

    return pd.DataFrame(rows)


def _build_traffic(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    rows = []
    for _, ward in wards.iterrows():
        base = 48 + (72 - ward["service_coverage_score"]) * 0.45
        if ward["ward_id"] == "W05":
            base += 18
        for day in dates:
            rows.append(
                {
                    "ward_id": ward["ward_id"],
                    "date": day.isoformat(),
                    "morning_congestion": _clamp(round(randomizer.gauss(base + 16, 8)), 0, 100),
                    "evening_congestion": _clamp(round(randomizer.gauss(base + 20, 9)), 0, 100),
                    "average_speed_kmph": round(max(12, randomizer.gauss(42 - base * 0.22, 5)), 1),
                }
            )
    return pd.DataFrame(rows)


def _build_air_quality(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    rows = []
    for _, ward in wards.iterrows():
        base = 68
        if ward["ward_id"] == "W03":
            base = 118
        if ward["ward_id"] == "W05":
            base = 88
        for day_index, day in enumerate(dates):
            anomaly = 44 if ward["ward_id"] == "W03" and day_index in {22, 23} else 0
            rows.append(
                {
                    "ward_id": ward["ward_id"],
                    "date": day.isoformat(),
                    "aqi": _clamp(round(randomizer.gauss(base + anomaly, 12)), 25, 260),
                    "pm25": round(randomizer.gauss(base * 0.42 + anomaly * 0.25, 5), 1),
                    "source": "AQI Sensor Network",
                }
            )
    return pd.DataFrame(rows)


def _build_utility_outages(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    rows = []
    outage_id = 1
    for _, ward in wards.iterrows():
        weekly_frequency = 1
        if ward["ward_id"] in {"W04", "W06"}:
            weekly_frequency = 3
        for day in dates:
            if randomizer.random() < weekly_frequency / 7:
                rows.append(
                    {
                        "outage_id": f"U{outage_id:04d}",
                        "ward_id": ward["ward_id"],
                        "date": day.isoformat(),
                        "utility_type": randomizer.choice(["water", "electricity"]),
                        "affected_households": randomizer.randint(80, 1300),
                        "duration_hours": round(randomizer.uniform(1.5, 12), 1),
                    }
                )
                outage_id += 1
    return pd.DataFrame(rows)


def _build_healthcare_access(wards: pd.DataFrame, randomizer: Random) -> pd.DataFrame:
    rows = []
    for _, ward in wards.iterrows():
        shortage = 1 if ward["ward_id"] in {"W04", "W06"} else 0
        rows.append(
            {
                "ward_id": ward["ward_id"],
                "clinics_count": max(1, int(randomizer.gauss(5 - shortage * 2, 1))),
                "average_distance_km": round(randomizer.gauss(2.2 + shortage * 2.1, 0.6), 1),
                "appointments_wait_days": max(1, int(randomizer.gauss(5 + shortage * 7, 2))),
                "mobile_health_coverage": "limited" if shortage else "standard",
            }
        )
    return pd.DataFrame(rows)


def _build_emergency_incidents(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    rows = []
    incident_id = 1
    for _, ward in wards.iterrows():
        baseline = 2 if ward["ward_id"] not in {"W04", "W05"} else 4
        for day in dates:
            count = max(0, int(randomizer.gauss(baseline, 1.4)))
            for _ in range(count):
                rows.append(
                    {
                        "incident_id": f"E{incident_id:05d}",
                        "ward_id": ward["ward_id"],
                        "date": day.isoformat(),
                        "incident_type": randomizer.choice(["medical", "fire", "road safety", "public safety"]),
                        "response_time_minutes": round(randomizer.gauss(9 + baseline, 2.5), 1),
                    }
                )
                incident_id += 1
    return pd.DataFrame(rows)


def _build_waste_collection(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    rows = []
    for _, ward in wards.iterrows():
        delay_bias = 0.22 if ward["ward_id"] in {"W02", "W06", "W08"} else 0.08
        for day in dates:
            delayed = randomizer.random() < delay_bias
            rows.append(
                {
                    "ward_id": ward["ward_id"],
                    "date": day.isoformat(),
                    "routes_completed": randomizer.randint(18, 42),
                    "delayed_routes": randomizer.randint(2, 9) if delayed else randomizer.randint(0, 2),
                    "missed_pickups": randomizer.randint(8, 65) if delayed else randomizer.randint(0, 12),
                }
            )
    return pd.DataFrame(rows)


def _build_community_programs(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    rows = []
    program_id = 1
    for _, ward in wards.iterrows():
        for week_start in dates[::7]:
            rows.append(
                {
                    "program_id": f"P{program_id:04d}",
                    "ward_id": ward["ward_id"],
                    "week_start": week_start.isoformat(),
                    "program_type": randomizer.choice(["health outreach", "youth services", "job support", "elder care"]),
                    "participants": randomizer.randint(35, 420),
                    "capacity": randomizer.randint(120, 520),
                }
            )
            program_id += 1
    return pd.DataFrame(rows)


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))
