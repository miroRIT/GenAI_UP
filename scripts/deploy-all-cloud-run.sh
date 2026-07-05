#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID before deploying}"
: "${REGION:=asia-south1}"

scripts/deploy-backend-cloud-run.sh

if [[ -z "${NEXT_PUBLIC_API_BASE_URL:-}" ]]; then
  NEXT_PUBLIC_API_BASE_URL="$(gcloud run services describe "${BACKEND_SERVICE:-civiciq-api}" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')"
  export NEXT_PUBLIC_API_BASE_URL
fi

scripts/deploy-frontend-cloud-run.sh
