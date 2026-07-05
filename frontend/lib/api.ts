const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token =
    typeof window !== "undefined" ? window.localStorage.getItem("civiciq_token") : null;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
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
  state: string;
  population: number;
  area_sq_km: number;
  latitude: number;
  longitude: number;
  disaster_profile: string;
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

export async function getRegionProfile() {
  return request<{
    region_name: string;
    population: number;
    population_label: string;
    area_sq_km: number;
    planning_note: string;
    states: string[];
    zone_count: number;
  }>("/api/region/profile");
}

export async function getDisasterMap() {
  return request<{
    region: Record<string, string | number | string[]>;
    bbox: { north: number; south: number; east: number; west: number };
    layers: Array<Ward & { disaster_score: number; primary_hazards: string[] }>;
  }>("/api/geospatial/disaster-map");
}

export async function getLiveMonitoring() {
  return request<{
    updated_at: string;
    mode: string;
    providers_ready: string[];
    weather: MonitoringSignal[];
    traffic: MonitoringSignal[];
    news: MonitoringSignal[];
    geospatial: MonitoringSignal[];
  }>("/api/monitoring/live");
}

export type MonitoringSignal = {
  zone: string;
  signal: string;
  value: string;
  severity: string;
  action: string;
};

export type GeoIncident = {
  incident_id: string;
  title: string;
  district_id: string;
  district_name: string;
  category: string;
  severity: string;
  timestamp: string;
  source: string;
  url: string;
  summary: string;
  latitude: number;
  longitude: number;
  recommended_action: string;
};

export type Alert = {
  alert_id: string;
  title: string;
  description: string;
  district_id: string;
  district_name: string;
  category: string;
  severity: string;
  priority: string;
  status: string;
  assigned_department: string;
  source: string;
  created_at: string;
  updated_at: string;
  sla_due_at?: string | null;
  sla_status?: string;
  first_response_due_at?: string | null;
  resolution_due_at?: string | null;
  escalation_status?: string;
  recommended_actions: string[];
  notes: string;
  incident_brief: string;
};

export type ProviderStatus = {
  provider_name: string;
  provider_type: string;
  configured: boolean;
  health_status: string;
  last_success_at: string | null;
  last_failure_at: string | null;
  last_error: string;
  rate_limit_status: string;
};

export type DisasterRisk = {
  district_id: string;
  district_name: string;
  state: string;
  population: number;
  area_sq_km: number;
  latitude: number;
  longitude: number;
  overall: {
    score: number;
    level: string;
    explanation: string;
    confidence: string;
    data_sources_used: string[];
  };
  risks: Record<
    string,
    {
      score: number;
      level: string;
      top_contributing_factors: string[];
      explanation: string;
      recommended_actions: string[];
      confidence: string;
      data_sources_used: string[];
    }
  >;
};

export async function getDistrictGeoJson() {
  return request<Record<string, unknown>>("/api/geospatial/districts");
}

export async function getGeoIncidents() {
  return request<GeoIncident[]>("/api/geospatial/incidents");
}

export async function getGeoLayers() {
  return request<Array<{ id: string; name: string; source: string }>>("/api/geospatial/layers");
}

export async function getDistricts() {
  return request<Ward[]>("/api/districts");
}

export async function getDistrictDetail(districtId: string) {
  return request<
    Ward & {
      disaster_risk: DisasterRisk;
      alerts: Alert[];
      incidents: GeoIncident[];
      recommendations: string[];
      weather: Record<string, string | number | object>;
      traffic: Record<string, string | number>;
      environment: Record<string, string | number>;
    }
  >(`/api/districts/${districtId}`);
}

export async function getDisasterRisk() {
  return request<DisasterRisk[]>("/api/disaster-risk");
}

export async function getAlerts() {
  return request<Alert[]>("/api/alerts");
}

export async function getAssignedAlerts() {
  return request<Alert[]>("/api/alerts/assigned-to-me");
}

export async function getSlaSummary() {
  return request<{ summary: Record<string, number>; total: number }>("/api/alerts/sla-summary");
}

export async function assignAlert(alertId: string, department: string, priority?: string) {
  return request<Alert>(`/api/alerts/${alertId}/assign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ department, priority }),
  });
}

export async function transitionAlert(
  alertId: string,
  transition: "acknowledge" | "resolve" | "close",
  notes = "",
) {
  return request<Alert>(`/api/alerts/${alertId}/${transition}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes }),
  });
}

export async function getJobStatus() {
  return request<
    Array<{
      id: number;
      job_name: string;
      status: string;
      started_at: string;
      completed_at: string | null;
      records_processed: number;
      error_message: string;
    }>
  >("/api/jobs/status");
}

export async function runJob(jobName: string) {
  return request<Record<string, string | number | null>>(`/api/jobs/run/${jobName}`, {
    method: "POST",
  });
}

export async function getProviderStatus() {
  return request<ProviderStatus[]>("/api/providers/status");
}

export async function testProvider(providerType: string) {
  return request<Record<string, unknown>>(`/api/providers/test/${providerType}`, {
    method: "POST",
  });
}

export async function login(email: string, password: string) {
  return request<{
    access_token: string;
    token_type: string;
    user: {
      email: string;
      full_name: string;
      role: string;
      department: string | null;
      district_id: string | null;
      assigned_districts?: string;
    };
  }>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
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
