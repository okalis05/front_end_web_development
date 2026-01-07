# MSE Dashboard App — Executive Healthcare Analytics

## Overview
The `dashboard` app is an executive-grade analytics suite designed to support healthcare leadership decisions by connecting **clinical outcomes (readmissions)** with **utilization-driven exposure signals**. It presents a boardroom-ready narrative using embedded Tableau dashboards within a secure Django application.

**Case Study:**  
**Reducing Hospital Readmissions While Controlling Healthcare Costs**

## Business Value
Readmissions create a dual-impact problem:
- **Clinical**: poorer outcomes and avoidable re-hospitalization
- **Financial**: increased utilization and potential CMS penalty pressure

This app enables leaders to:
- identify **at-risk facilities**
- prioritize **high-volume exposure**
- track **condition-level drivers**
- align operational actions with strategic outcomes

## Data Source
Primary dataset: CMS Provider Data — Hospital Readmissions  
https://data.cms.gov/provider-data/dataset/9n3s-kdb3

### Fields Used (As-Is)
- End Date
- Excess Readmission Ratio
- Expected Readmission Rate
- Facility Name
- Facility ID
- Measure Name
- Number of Discharges
- Number of Readmissions
- Predicted Readmission Rate
- Start Date
- State

## App Pages
- `/dashboard/` — Executive landing & narrative
- `/dashboard/executive/` — Board KPIs + geographic risk + priority facilities
- `/dashboard/readmissions/` — Condition drivers + expected vs predicted
- `/dashboard/cost-impact/` — Exposure proxy + volume-risk quadrant
- `/dashboard/hospital/<facility_id>/` — Facility drill-through profile
- `/dashboard/data/` — Governance, definitions, and security posture

## Tableau Integration
Dashboards are embedded securely via:
- **Host allowlisting** (CSP `frame-src`)
- **HTTPS enforcement**
- **Sandboxed iframe**
- Referrer policy hardening

Environment variables:
- `TABLEAU_EMBED_ALLOWED_HOSTS`
- `TABLEAU_VIEW_EXECUTIVE_OVERVIEW`
- `TABLEAU_VIEW_READMISSIONS`
- `TABLEAU_VIEW_COST_IMPACT`
- `TABLEAU_VIEW_HOSPITAL_PROFILE`

## Security Posture
- This application denies being framed by external sites (`X_FRAME_OPTIONS=DENY`).
- Tableau is embedded inside the app via a strict CSP allowlist.
- Iframes are sandboxed with minimal privileges.

## Optional: Load CMS CSV into SQLite
This app includes an importer to operationalize the dataset locally.

1. Download the CMS CSV from the dataset page
2. Run:
   ```bash
   python manage.py makemigrations dashboard
   python manage.py migrate
   python manage.py import_readmissions_csv --path /path/to/file.csv
