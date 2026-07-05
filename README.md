# CivicIQ — NCR Disaster and Civic Decision Intelligence Platform

CivicIQ is a full-stack NCR-focused decision intelligence prototype for disaster response, civic operations, and community well-being. It combines FastAPI, Next.js, provider-based monitoring, geospatial maps, risk scoring, alert workflows, scheduled ingestion jobs, and an AI decision-support assistant.

## What It Does

- Monitors NCR districts across Delhi, Haryana, Uttar Pradesh, and Rajasthan.
- Uses default NCR sample data covering about 7.5 crore people across 55,083 sq km.
- Integrates provider adapters for news, weather, traffic, environmental data, geospatial layers, and disaster alerts.
- Uses GDELT by default for free news search, NewsAPI when `NEWS_API_KEY` is available, OpenWeather when `OPENWEATHER_API_KEY` is available, and fallback mock mode when keys are missing.
- Displays OpenStreetMap tiles with simplified NCR GeoJSON district boundaries and incident markers.
- Scores flood, heatwave, AQI/public health, seismic, drought/water-stress, and industrial/fire risks.
- Persists users, alerts, timelines, incidents, and ingestion job logs in SQLite.
- Supports alert assignment, acknowledgement, resolution, CSV export, and Markdown incident briefs.
- Provides demo JWT login roles for Admin, District Officer, Analyst, and Viewer.
- Includes Cloud Run deployment files for backend and frontend.

## Tech Stack

- Frontend: Next.js App Router, TypeScript, Tailwind CSS, Recharts, Leaflet, React Leaflet
- Backend: FastAPI, pandas, numpy, SQLAlchemy, SQLite, APScheduler, PyJWT
- AI: Mock/rule-based mode by default; Gemini-compatible mode with `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- Data: Generated CSVs, SQLite runtime state, local GeoJSON, local RAG knowledge base

## Local Setup

```bash
cp .env.example .env
```

### Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend default: `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend default: `http://127.0.0.1:3000`

If the backend runs on another port:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 npm start
```

## Demo Credentials

- Admin: `admin@civiciq.demo` / `Admin@12345`
- District Officer: `officer@civiciq.demo` / `Officer@12345`
- Analyst: `analyst@civiciq.demo` / `Analyst@12345`
- Viewer: `viewer@civiciq.demo` / `Viewer@12345`

## Environment Variables

Backend:

- `PORT=8080`
- `DATABASE_URL=sqlite:///./civiciq.db`
- `JWT_SECRET_KEY=change-me`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- `GEMINI_API_KEY=`
- `GOOGLE_API_KEY=`
- `NEWS_API_KEY=`
- `OPENWEATHER_API_KEY=`
- `GOOGLE_MAPS_API_KEY=`
- `TOMTOM_API_KEY=`
- `MAPBOX_ACCESS_TOKEN=`
- `ENABLE_SCHEDULER=false`
- `NEWS_REFRESH_MINUTES=30`
- `WEATHER_REFRESH_MINUTES=30`
- `TRAFFIC_REFRESH_MINUTES=15`
- `RISK_REFRESH_MINUTES=30`
- `ALERT_REFRESH_MINUTES=30`
- `MOCK_MODE=true`
- `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`

Frontend:

- `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`
- `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=`
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=`

## Key Pages

- `/dashboard`: NCR overview, live monitoring, interactive map, recommendations
- `/districts`: district ranking and drilldown entry
- `/districts/[districtId]`: district profile, disaster risk scores, alerts, incidents, weather, traffic, map
- `/alerts`: operational alert workflow table
- `/admin/data-refresh`: manual ingestion job runner
- `/assistant`: AI decision-support chat
- `/login`: demo authority login

## API Highlights

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/districts`
- `GET /api/districts/{district_id}`
- `GET /api/districts/{district_id}/risk`
- `GET /api/districts/{district_id}/alerts`
- `GET /api/districts/{district_id}/incidents`
- `GET /api/disaster-risk`
- `GET /api/disaster-risk/{district_id}`
- `GET /api/disaster-risk/{district_id}/{risk_type}`
- `GET /api/geospatial/districts`
- `GET /api/geospatial/incidents`
- `GET /api/geospatial/layers`
- `GET /api/monitoring/live`
- `GET /api/alerts`
- `POST /api/alerts`
- `POST /api/alerts/{alert_id}/assign`
- `POST /api/alerts/{alert_id}/acknowledge`
- `POST /api/alerts/{alert_id}/resolve`
- `GET /api/alerts/export.csv`
- `GET /api/alerts/{alert_id}/export.md`
- `POST /api/jobs/run/news|weather|traffic|risk|alerts|geospatial`
- `GET /api/jobs/status`
- `POST /api/chat`

## Provider Integrations

- News: GDELT free API by default; NewsAPI when `NEWS_API_KEY` is set.
- Weather: OpenWeather when `OPENWEATHER_API_KEY` is set; fallback weather otherwise.
- IMD: `IMDProvider` abstraction is included for official future feed wiring.
- Traffic: abstraction is ready for Google Maps, TomTom, or Mapbox; fallback mock traffic runs locally.
- Geospatial: OpenStreetMap tiles in frontend; local simplified NCR GeoJSON in backend and frontend public assets.
- Bhuvan: abstraction is included for future official geospatial integration.

## Running Jobs

Manual:

```bash
curl -X POST http://127.0.0.1:8000/api/jobs/run/news
curl -X POST http://127.0.0.1:8000/api/jobs/run/weather
curl -X POST http://127.0.0.1:8000/api/jobs/run/traffic
curl -X POST http://127.0.0.1:8000/api/jobs/run/risk
curl -X POST http://127.0.0.1:8000/api/jobs/run/alerts
```

Scheduled local jobs:

```bash
ENABLE_SCHEDULER=true uvicorn main:app --reload
```

## Testing

```bash
cd backend
. .venv/bin/activate
pytest -q

cd ../frontend
npm run build
```

## Docker Compose

```bash
docker compose up --build
```

## Cloud Run Deployment

Set your project:

```bash
export PROJECT_ID=your-gcp-project
export REGION=asia-south1
./deploy-cloud-run.sh
```

This deploys:

- Backend Cloud Run service: `civiciq-api`
- Frontend Cloud Run service: `civiciq-web`

Build files:

- `cloudbuild.backend.yaml`
- `cloudbuild.frontend.yaml`
- `backend/Dockerfile`
- `frontend/Dockerfile`

## Google Cloud Architecture Mapping

- Cloud Run: FastAPI and Next.js services
- BigQuery: analytical civic and disaster data warehouse
- Cloud Storage: uploaded datasets, GeoJSON, incident exports
- Pub/Sub: real-time weather/news/traffic/incident ingestion
- Cloud Functions: event-driven ingestion and alert generation
- Vertex AI / Gemini: AI assistant and incident brief generation
- Vertex AI Search or vector database: production RAG retrieval
- AlloyDB / Cloud SQL: production operational database
- Looker: executive dashboards and reporting
- Agent Development Kit: future multi-step response workflows

## Responsible AI and Limitations

- CivicIQ is decision support only and does not issue official emergency orders.
- Provider data may be incomplete, delayed, rate-limited, or unavailable.
- Fallback mode uses synthetic/mock-live observations for demo reliability.
- Simplified NCR GeoJSON polygons are placeholders; production should use official NCR/Bhuvan/Survey of India/state GIS layers.
- Vulnerable population data is used only for service prioritization.
- Critical alerts should be verified by district control rooms and official authorities.

## Next Production Steps

- Replace simplified GeoJSON with official district boundaries.
- Persist provider observations in normalized SQLite/PostgreSQL tables.
- Add real Google/TomTom/Mapbox traffic adapters.
- Add official IMD feed ingestion.
- Add RBAC enforcement middleware on protected APIs.
- Add audit logs, refresh retries, and provider health monitoring.
- Move local SQLite to Cloud SQL or AlloyDB.
- Add PDF incident brief exports and signed URLs.
