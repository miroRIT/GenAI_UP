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
            _ncr_zone("NCR01", "Delhi NCT", "Delhi", 19500000, 1483, 24, "Mixed", 68, 28.6139, 77.2090, "Yamuna floodplain, seismic zone IV, extreme heat, severe AQI"),
            _ncr_zone("NCR02", "Gurugram", "Haryana", 3100000, 1258, 16, "Upper-Middle", 74, 28.4595, 77.0266, "Urban flooding, heat stress, Aravalli degradation, traffic gridlock"),
            _ncr_zone("NCR03", "Faridabad", "Haryana", 2800000, 742, 18, "Middle", 64, 28.4089, 77.3178, "Industrial air pollution, Yamuna floodplain, heat stress"),
            _ncr_zone("NCR04", "Ghaziabad", "Uttar Pradesh", 4900000, 1179, 23, "Middle", 57, 28.6692, 77.4538, "Hindon-Yamuna flood risk, severe AQI, high emergency load"),
            _ncr_zone("NCR05", "Gautam Buddh Nagar / Noida", "Uttar Pradesh", 3600000, 1282, 17, "Upper-Middle", 71, 28.5355, 77.3910, "Yamuna floodplain, expressway incidents, severe AQI"),
            _ncr_zone("NCR06", "Meerut", "Uttar Pradesh", 4000000, 2522, 26, "Lower-Middle", 55, 28.9845, 77.7064, "Ganga-Yamuna basin flooding, dense urban fire risk, seismic shaking"),
            _ncr_zone("NCR07", "Sonipat", "Haryana", 2200000, 2260, 21, "Middle", 61, 28.9931, 77.0151, "Yamuna floodplain, industrial emissions, highway incidents"),
            _ncr_zone("NCR08", "Panipat", "Haryana", 1900000, 1268, 20, "Middle", 58, 29.3909, 76.9635, "Industrial fire risk, poor AQI, heat stress"),
            _ncr_zone("NCR09", "Rohtak-Jhajjar Belt", "Haryana", 3300000, 3742, 19, "Middle", 62, 28.8955, 76.6066, "Heatwave exposure, water stress, transport disruption"),
            _ncr_zone("NCR10", "Rewari-Mahendragarh Belt", "Haryana", 2700000, 3485, 24, "Lower-Middle", 52, 28.1928, 76.6239, "Aravalli slope erosion, drought, heatwave exposure"),
            _ncr_zone("NCR11", "Nuh-Palwal Belt", "Haryana", 3000000, 2868, 34, "Lower", 46, 28.1020, 77.0010, "Flash flooding, low healthcare access, heat stress"),
            _ncr_zone("NCR12", "Karnal-Jind-Bhiwani-Dadri Belt", "Haryana", 6200000, 10384, 25, "Lower-Middle", 54, 29.6857, 76.9905, "Agricultural fire smoke, heatwave, water stress"),
            _ncr_zone("NCR13", "Baghpat-Shamli-Muzaffarnagar Belt", "Uttar Pradesh", 5800000, 5037, 28, "Lower-Middle", 49, 29.4727, 77.7085, "Yamuna floodplain, sugar-belt fire risk, fog and highway incidents"),
            _ncr_zone("NCR14", "Hapur-Bulandshahr Belt", "Uttar Pradesh", 4800000, 5532, 26, "Lower-Middle", 51, 28.4069, 77.8498, "Ganga basin flooding, AQI episodes, utility stress"),
            _ncr_zone("NCR15", "Alwar", "Rajasthan", 4000000, 8380, 27, "Lower-Middle", 50, 27.5530, 76.6346, "Aravalli degradation, drought, heatwave, flash flooding"),
            _ncr_zone("NCR16", "Bharatpur", "Rajasthan", 3600000, 3661, 29, "Lower-Middle", 48, 27.2152, 77.5030, "Flooding, heatwave, wetland stress, vector disease risk"),
        ]
    )


def _ncr_zone(
    ward_id: str,
    ward_name: str,
    state: str,
    population: int,
    area_sq_km: int,
    vulnerable_population_percentage: int,
    average_income_band: str,
    service_coverage_score: int,
    latitude: float,
    longitude: float,
    disaster_profile: str,
) -> dict[str, Any]:
    return {
        "ward_id": ward_id,
        "ward_name": ward_name,
        "state": state,
        "population": population,
        "area_sq_km": area_sq_km,
        "vulnerable_population_percentage": vulnerable_population_percentage,
        "average_income_band": average_income_band,
        "service_coverage_score": service_coverage_score,
        "latitude": latitude,
        "longitude": longitude,
        "disaster_profile": disaster_profile,
    }


def _build_complaints(wards: pd.DataFrame, dates: list[date], randomizer: Random) -> pd.DataFrame:
    categories = ["sanitation", "roads", "noise", "water", "electricity", "public safety"]
    rows: list[dict[str, Any]] = []
    complaint_id = 1

    for _, ward in wards.iterrows():
        baseline = max(6, int((100 - ward["service_coverage_score"]) / 2.8))
        for day_index, day in enumerate(dates):
            trend = 1 + (day_index / 95)
            if ward["ward_id"] in {"NCR04", "NCR06", "NCR11", "NCR13"}:
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
        if ward["ward_id"] in {"NCR01", "NCR02", "NCR04", "NCR05"}:
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
        if ward["ward_id"] in {"NCR01", "NCR03", "NCR04", "NCR08"}:
            base = 118
        if ward["ward_id"] in {"NCR05", "NCR12"}:
            base = 88
        for day_index, day in enumerate(dates):
            anomaly = 44 if ward["ward_id"] in {"NCR01", "NCR04"} and day_index in {22, 23} else 0
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
        if ward["ward_id"] in {"NCR04", "NCR11", "NCR13", "NCR16"}:
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
        shortage = 1 if ward["ward_id"] in {"NCR06", "NCR10", "NCR11", "NCR13", "NCR16"} else 0
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
        baseline = 2 if ward["ward_id"] not in {"NCR01", "NCR04", "NCR05", "NCR06"} else 4
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
        delay_bias = 0.22 if ward["ward_id"] in {"NCR01", "NCR04", "NCR06", "NCR11"} else 0.08
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
