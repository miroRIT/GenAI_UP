const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export type Ward = {
  ward_id: string;
  ward_name: string;
  population: number;
  community_risk_score: number;
  risk_level: "Low" | "Medium" | "High" | "Critical";
  complaint_volume: number;
  complaint_growth_rate: number;
  emergency_count: number;
  aqi: number;
  outage_count: number;
  average_distance_km: number;
  appointments_wait_days: number;
  delayed_routes: number;
  missed_pickups: number;
};

export type Recommendation = {
  ward_id: string;
  ward_name: string;
  risk_level: string;
  community_risk_score: number;
  actions: string[];
};

export type Anomaly = {
  type: string;
  ward_id: string;
  ward_name: string;
  severity: string;
  metric: string;
  explanation: string;
  suggested_action: string;
};

export async function getOverview() {
  return request<Record<string, number | string>>("/api/overview");
}

export async function getWards() {
  return request<Ward[]>("/api/wards");
}

export async function getRiskRanking() {
  return request<Ward[]>("/api/analytics/risk-ranking");
}

export async function getRecommendations() {
  return request<Recommendation[]>("/api/recommendations");
}

export async function getAnomalies() {
  return request<Anomaly[]>("/api/analytics/anomalies");
}

export async function getForecast(metric: string) {
  return request<{
    metric: string;
    method: string;
    note: string;
    history: { date: string; value: number }[];
    forecast: { date: string; value: number }[];
  }>(`/api/analytics/forecast?metric=${metric}`);
}

export async function askCivicIq(question: string) {
  return request<{
    answer: string;
    sources: { source: string; chunk_id: string }[];
    related_metrics: Record<string, string | number>[];
    recommended_actions: string[];
    risk_or_opportunity_level: string;
    data_limitations: string[];
  }>("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}
