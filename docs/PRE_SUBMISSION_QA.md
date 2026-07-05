# CivicIQ Pre-Submission QA

Date: July 5, 2026

## Backend QA

- Backend tests: passed, `18 passed`
- `/api/health`: covered by automated tests
- `/api/dashboard/overview`: covered by automated tests
- `/api/demo/run-crisis`: covered by automated tests
- `/api/alerts`: covered by build/API usage and alert tests
- `/api/map/incidents`: covered by automated tests
- `/api/providers/health`: covered through operations endpoint
- Export endpoint: covered by automated tests

## Frontend QA

- Frontend build: passed, `npm run build`
- Key pages checked by build-time rendering:
  - `/dashboard`
  - `/demo`
  - `/map`
  - `/alerts`
  - `/operations`
  - `/assistant`
  - `/exports`
- Demo credentials:
  - `admin@civiciq.demo` / `Admin@123`
  - `officer@civiciq.demo` / `Officer@123`
  - `department@civiciq.demo` / `Department@123`
  - `analyst@civiciq.demo` / `Analyst@123`
  - `viewer@civiciq.demo` / `Viewer@123`

## Manual QA Notes

- Role badge appears in the header after login.
- Protected alert/job actions remain token-based.
- Demo Mode can run without live provider keys.
- Crisis Summary supports copy and markdown download.
- Assistant answers use the same seeded evidence as Demo Mode.
- Map and chart rendering passed production build; browser responsive mode should be checked during screenshot/video capture.

## Known Issues

- Screenshots and demo video are placeholders until captured locally.
- Cloud Run live URLs are marked “Not deployed yet.”
- Provider data is simulated unless API credentials are configured.

## Final Submission Notes

CivicIQ is ready for local judging. The recommended judging path is `/dashboard` -> `/demo` -> `/map` -> `/alerts` -> `/assistant` -> `/exports` -> `/operations`.
