const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchLiveTelemetry() {
  const response = await fetch(`${API_BASE_URL}/api/telemetry/live`);

  if (!response.ok) {
    throw new Error("Unable to load live telemetry.");
  }

  return response.json();
}

export async function queryUrbanAgent(query) {
  const response = await fetch(`${API_BASE_URL}/api/agent/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error("Unable to query the intelligence assistant.");
  }

  return response.json();
}
