#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID first}"
REGION="${REGION:-asia-south1}"
BACKEND_SERVICE="${BACKEND_SERVICE:-civiciq-api}"
FRONTEND_SERVICE="${FRONTEND_SERVICE:-civiciq-web}"

gcloud builds submit --config cloudbuild.backend.yaml --substitutions "_REGION=${REGION},_SERVICE=${BACKEND_SERVICE}" .

BACKEND_URL="$(gcloud run services describe "${BACKEND_SERVICE}" --region "${REGION}" --format='value(status.url)')"

gcloud builds submit --config cloudbuild.frontend.yaml --substitutions "_REGION=${REGION},_SERVICE=${FRONTEND_SERVICE},_API_URL=${BACKEND_URL}" .

echo "Backend: ${BACKEND_URL}"
echo "Frontend: $(gcloud run services describe "${FRONTEND_SERVICE}" --region "${REGION}" --format='value(status.url)')"
