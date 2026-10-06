# Legislative & Regulatory Reporting POC

**Proof of concept** — Vue 3 + Quasar frontend, Django REST Framework backend, PostgreSQL, Docker.

This is **not** a copy of any client system. It is a focused demo aligned to their reporting requirements so we can show:

> *I prepared a small Vue 3 + Django/DRF reporting proof of concept specifically around your requirements: filtering, aggregation, comparison views, saved configurations, and export.*

---

## Scope (intentionally narrow)

| In scope | Out of scope |
|----------|----------------|
| Legislative Inventory Builder | Full product / CMS |
| Regulatory Comparison Builder | Real Keycloak / SSO integration |
| Filter · sort · paginate · include/exclude | Production hardening |
| CSV / Excel export | Their proprietary data model |
| Saved comparison configs | Full authz / multi-tenant |
| Mock legal data (DE / FR / UK) | Rebuilding existing SSO |

**Auth:** mock Keycloak-style Bearer token only. The client already has SSO; this POC does not rebuild it.

---

## Stack

- **Frontend:** Vue 3, Quasar, Vite, Pinia, Vue Router  
- **Backend:** Django 4.2+, Django REST Framework, django-filter, openpyxl  
- **DB:** PostgreSQL 16  
- **Runtime:** Docker Compose  

---

## Quick start (Docker)

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:9000 |
| API | http://localhost:8000 |
| Postgres | localhost:5432 (`legis` / `legis` / `legis_poc`) |

**Login (mock):** any username + any non-empty password → issues `poc-demo-token`.

---

## Screens

### 1. Legislative Inventory Builder
- Filters: **jurisdiction** / **topic** / **status**
- Sorting & pagination
- Include / exclude records (checkbox)
- Export **CSV** or **Excel** via `/api/reports/inventory`

### 2. Regulatory Comparison Builder
- Multi-jurisdiction selection
- Side-by-side **structured field** matrix
- **Save** comparison configuration
- **Export Excel**

---

## API

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/auth/login/` | Mock SSO token |
| `GET` | `/api/auth/me/` | Current mock user |
| `GET` | `/api/legislation` | Paginated legislation list |
| `GET` | `/api/legislation/meta` | Filter / field catalogs |
| `GET` | `/api/reports/inventory` | Inventory report (+ `format=csv\|xlsx`) |
| `GET/POST` | `/api/comparisons` | List / create saved configs |
| `POST` | `/api/comparisons/preview` | Build matrix (optional Excel) |
| `GET` | `/api/comparisons/{id}/export` | Excel for saved config |

Auth header: `Authorization: Bearer poc-demo-token`

### Example

```bash
TOKEN=poc-demo-token

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/legislation?jurisdiction=Germany&topic=AI"

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/reports/inventory?status=Active&format=csv" -o inventory.csv

curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"jurisdictions":["Germany","France","UK"],"topic":"AI"}' \
  http://localhost:8000/api/comparisons/preview
```

---

## Mock data

Jurisdictions: **Germany**, **France**, **UK**  
Topics: **AI**, **Data Protection**, **Payments**  
Statuses: **Active**, **Proposed**, **Repealed**

Seeded automatically on container start (`seed_legislation`).

---

## Tests

```bash
# inside backend container or local venv with USE_SQLITE=1
cd backend
set USE_SQLITE=1   # Windows PowerShell: $env:USE_SQLITE=1
pip install -r requirements.txt
python manage.py migrate
python manage.py test reports comparisons
```

Coverage focuses on **reporting logic**: filters, include/exclude, aggregates, comparison matrix.

---

## Local dev (without Docker frontend)

```bash
# Backend (SQLite shortcut)
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:USE_SQLITE="1"
python manage.py migrate
python manage.py seed_legislation
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:9000 (proxies `/api` → `:8000`)

---

## Project layout

```
backend/          Django + DRF
  legislation/    Mock legislative records
  reports/        Inventory filter / aggregate / export
  comparisons/    Matrix builder + saved configs
  config/         Settings + mock Keycloak auth
frontend/         Vue 3 + Quasar
docker-compose.yml
```

---

## Talking point for the client

This POC demonstrates the **reporting slice** they care about — inventory filtering and aggregation, multi-jurisdiction comparison matrices, persisted comparison configs, and CSV/Excel export — on the **Vue 3 + Django/DRF** stack they asked to see, without pretending to replicate their full platform or SSO.
