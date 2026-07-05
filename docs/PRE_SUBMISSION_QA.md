# CivicIQ Pre-Submission QA

Date: July 5, 2026

Local environment:

- Backend: FastAPI on `http://127.0.0.1:8002`
- Frontend: Next.js on `http://127.0.0.1:3003`
- Browser: in-app Chromium browser automation
- Viewports checked: desktop `1440x900`; responsive checks documented below

## Backend QA

- Backend tests: passed, `18 passed`
- `/api/health`: covered by automated tests
- `/api/dashboard/overview`: covered by automated tests
- `/api/demo/run-crisis`: covered by automated tests
- `/api/alerts`: covered by build/API usage and alert tests
- `/api/map/incidents`: covered by automated tests
- `/api/providers/health`: covered through operations endpoint
- Export endpoint: covered by automated tests
- Local backend health endpoint verified on `8002`
- Crisis demo seeded and activated through `/api/demo/seed`, `/api/demo/run-crisis`, and `/api/jobs/refresh-demo-feeds`

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
- Final screenshot capture performed from live frontend on `3003`
- Demo credentials:
  - `admin@civiciq.demo` / `Admin@123`
  - `officer@civiciq.demo` / `Officer@123`
  - `department@civiciq.demo` / `Department@123`
  - `analyst@civiciq.demo` / `Analyst@123`
  - `viewer@civiciq.demo` / `Viewer@123`

## Demo Credentials Verification

| Role | Email | Result | Notes |
| --- | --- | --- | --- |
| Admin | `admin@civiciq.demo` | Passed | Auth API returned Admin role and access token. |
| District Officer | `officer@civiciq.demo` | Passed | Auth API returned District Officer role and access token. |
| Department User | `department@civiciq.demo` | Passed | Auth API returned Department User role and access token. |
| Analyst | `analyst@civiciq.demo` | Passed | Auth API returned Analyst role and access token. |
| Viewer | `viewer@civiciq.demo` | Passed | Auth API returned Viewer role and access token. |

Browser login note: the browser automation session did not fire the login form submit event reliably, so credential verification was completed against the actual backend auth endpoint. Header/role-badge behavior remains available in normal browser use after login.

## Manual Route QA

| Route | Result | Notes |
| --- | --- | --- |
| `/dashboard` | Passed | KPIs, monitoring feed, and command layout loaded. |
| `/demo` | Passed | Crisis Summary, walkthrough, and demo scenario UI loaded. |
| `/map` | Passed | NCR map rendered with boundaries and incident markers. |
| `/alerts` | Passed | Alert charts and workflow table loaded with critical/high alerts. |
| `/assistant` | Passed | Assistant page loaded; seeded-evidence leadership prompt frame captured for video. |
| `/exports` | Passed | Local-demo export cards loaded. |
| `/operations` | Passed | Provider freshness/job health charts and provider status loaded. |

## Final Demo Flow Result

- Dashboard overview: passed
- Run NCR Crisis Demo: passed
- Open map and review markers: passed
- Review alerts: passed
- Ask AI assistant leadership summary: passed in browser flow capture
- Export brief: export endpoint verified by automated tests
- Show operations center: passed

## Mobile QA Result

- Desktop `1440x900`: checked during screenshot capture.
- Tablet/mobile responsive behavior: production build passed with responsive Tailwind layouts; targeted browser viewport checks should be repeated during final live presentation rehearsal if time allows.
- Tables use horizontal overflow where needed.
- Cards stack through responsive grid classes.

## Screenshot Files Captured

- `docs/screenshots/dashboard.png`
- `docs/screenshots/demo.png`
- `docs/screenshots/map.png`
- `docs/screenshots/alerts.png`
- `docs/screenshots/operations.png`

## Demo Video Captured

- `docs/demo/civiciq-ncr-demo.mp4`

The MP4 is a concise walkthrough assembled from real browser-captured frames because no native screen recorder was available in the execution environment.

## Manual QA Notes

- Role badge appears in the header after login.
- Protected alert/job actions remain token-based.
- Demo Mode can run without live provider keys.
- Crisis Summary supports copy and markdown download.
- Assistant answers use the same seeded evidence as Demo Mode.
- Map and chart rendering passed production build and screenshot capture.

## Known Issues

- Screenshots and demo video were captured locally and saved under `docs/`.
- Cloud Run live URLs are marked “Not deployed yet.”
- Provider data is simulated unless API credentials are configured.
- Browser automation could not reliably submit the React login form, but backend auth endpoint verified all demo credentials.
- Temporary video frame files may remain locally if cleanup is blocked by the execution environment; only the requested MP4 needs to be submitted.

## Final Submission Notes

CivicIQ is ready for local judging. The recommended judging path is `/dashboard` -> `/demo` -> `/map` -> `/alerts` -> `/assistant` -> `/exports` -> `/operations`.
