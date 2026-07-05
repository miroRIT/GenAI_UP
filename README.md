# CivicIQ — AI Decision Intelligence Platform for Community Well-being

CivicIQ is a full-stack hackathon prototype showing how AI, analytics, anomaly detection, forecasting, lightweight RAG, and workflow recommendations can help city stakeholders prioritize community well-being.

## Problem Statement

City administrators and community leaders often need to decide which wards need urgent attention across complaints, public services, mobility, healthcare access, environmental conditions, utilities, waste collection, and emergency incidents. CivicIQ turns fragmented civic signals into explainable risk scores, recommendations, and AI-assisted answers.

## Features

- Next.js + TypeScript civic dashboard with KPI cards, charts, tables, filters, and chat.
- FastAPI backend with modular REST APIs for overview, wards, analytics, anomalies, forecasts, recommendations, chat, and CSV upload.
- Automatic sample civic data generation in `backend/data`.
- Community Risk Score engine with weighted factors and Low/Medium/High/Critical classification.
- Rule-based anomaly detection for AQI spikes, complaint spikes, utility outages, and emergency load.
- Moving-average forecast estimates for complaints, AQI, and outages.
- Lightweight RAG over local markdown files in `backend/knowledge_base`.
- Mock AI mode by default, with optional Gemini-compatible mode via environment variable.

## Architecture

```text
frontend/               Next.js App Router, TypeScript, Tailwind CSS, Recharts
backend/app/main.py     FastAPI app and CORS setup
backend/app/routes/     REST API routers
backend/app/services/   Data loading, risk, anomaly, forecast, RAG, AI, recommendations
backend/data/           Generated civic CSV datasets
backend/knowledge_base/ Local policy and service guidance documents
```

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS, Recharts, lucide-react
- Backend: Python, FastAPI, pandas, numpy
- AI: Mock rule-based assistant by default; Gemini API when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set
- Storage: Local CSV files for prototype data

## Local Setup

From the repository root:

```bash
cp .env.example .env
```

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: frontend API target, default `http://127.0.0.1:8000`
- `GEMINI_API_KEY`: optional Gemini API key
- `GOOGLE_API_KEY`: optional Gemini-compatible fallback key

No paid service is required. Without an API key, CivicIQ runs in mock AI mode.

## Running Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs at `http://127.0.0.1:8000`. Sample CSV files are generated automatically on startup.

## Running Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs at `http://127.0.0.1:3000`.

## API Endpoints

- `GET /api/health`
- `GET /api/overview`
- `GET /api/wards`
- `GET /api/wards/{ward_id}`
- `GET /api/analytics/risk-ranking`
- `GET /api/analytics/anomalies`
- `GET /api/analytics/forecast?metric=complaints|aqi|outages`
- `GET /api/recommendations`
- `POST /api/chat`
- `POST /api/upload`
- `POST /api/upload/reset`

## Sample Questions

- Which wards need urgent action this week?
- Why is Ward 4 classified as high risk?
- What are the top 3 recommendations for improving community well-being?
- Are there any anomalies in air quality?
- Which areas have both high complaints and poor healthcare access?
- What should city officials prioritize tomorrow?
- Summarize the current state of the city.
- Which services are underperforming?
- What data is missing for better decisions?

## Google Cloud Deployment Path

- Local CSV data maps to BigQuery for analytical warehousing.
- FastAPI backend maps to Cloud Run.
- Uploaded datasets map to Cloud Storage.
- Optional Gemini mode maps to Vertex AI or Gemini APIs.
- Local knowledge base maps to Cloud Storage plus Vertex AI Search or a vector store.
- Local dashboards can be complemented by Looker.
- Upload and anomaly workflows map to Cloud Functions.
- Structured operational data can move to AlloyDB or Cloud SQL.
- Real-time civic events can be ingested through Pub/Sub.
- Future multi-step workflows can use Agent Development Kit.

## Responsible AI Considerations

- CivicIQ is decision support, not an automated emergency decision maker.
- Forecasts are prototype estimates and should be reviewed by domain experts.
- AI responses explain data used and include limitations.
- Vulnerable population data is used only to improve service prioritization.
- Recommendations should be reviewed for bias and local context before action.
- Low-confidence or incomplete data should trigger human review.

## Future Enhancements

- Add authenticated user roles for city teams and community organizations.
- Add geospatial maps and ward boundary overlays.
- Replace keyword RAG with embeddings and semantic retrieval.
- Add workflow ticket creation for recommended actions.
- Add streaming telemetry ingestion and real-time alerting.
- Add model evaluation, feedback capture, and audit logs.
