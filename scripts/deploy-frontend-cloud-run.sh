#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID before deploying}"
: "${REGION:=asia-south1}"
: "${FRONTEND_SERVICE:=civiciq-web}"
: "${NEXT_PUBLIC_API_BASE_URL:?Set NEXT_PUBLIC_API_BASE_URL to the deployed backend URL}"

gcloud builds submit --config cloudbuild.frontend.yaml --project "$PROJECT_ID" --substitutions "_NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL"
gcloud run deploy "$FRONTEND_SERVICE" \
  --image "gcr.io/$PROJECT_ID/civiciq-web" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --project "$PROJECT_ID"
