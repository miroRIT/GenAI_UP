#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID before deploying}"
: "${REGION:=asia-south1}"
: "${BACKEND_SERVICE:=civiciq-api}"

gcloud builds submit --config cloudbuild.backend.yaml --project "$PROJECT_ID"
gcloud run deploy "$BACKEND_SERVICE" \
  --image "gcr.io/$PROJECT_ID/civiciq-api" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --project "$PROJECT_ID"
