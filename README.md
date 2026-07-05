# Decision Intelligence Platform

Web-based dashboard scaffold for the Gen AI Academy APAC Challenge. The app uses a React + Tailwind CSS + Recharts frontend and a FastAPI backend with a mock RAG-style urban decision intelligence agent.

## Project Structure

```text
backend/
  main.py
  requirements.txt
  app/
    api/
      agent_routes.py
      telemetry_routes.py
    services/
      agent_service.py
      mock_data_service.py
  tests/
frontend/
  package.json
  index.html
  src/
    App.jsx
    components/
      AgentPanel.jsx
      LiveFeed.jsx
      TelemetryChart.jsx
    pages/
    services/
      api.js
    styles/
      index.css
```

## Backend

From the backend directory:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

Available endpoints:

- `GET /health`
- `GET /api/telemetry/live`
- `POST /api/agent/query`

## Frontend

From the frontend directory:

```bash
npm install
npm start
```

The dashboard runs at `http://localhost:3000`.

## Current Scaffold

The backend generates realistic mock city telemetry across multiple sectors. Traffic congestion peaks during morning and evening rush hours, emergency call volume affects response times, and air quality responds to congestion pressure.

The agent uses a system context that frames it as an Urban Decision Intelligence Assistant. If it cannot find relevant data, it responds:

```text
I don't have enough data on [Topic]—would you like me to simulate a projection based on historical trends?
```
