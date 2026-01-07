# Enterprise Data Pipeline Command Center

## Executive Overview

The **Enterprise Data Pipeline Command Center** is a real-time orchestration and observability platform designed to manage, monitor, and scale modern data pipelines with executive-level clarity.

It serves as a **single control plane** for transforming raw data into trusted, analytics-ready assets by combining:
- **Prefect** for orchestration and workflow execution  
- **dbt** for transformations, tests, and analytics modeling  
- **Django + Channels** for secure access, real-time updates, and operational governance  

This application is built for **technical leadership, analytics leaders, and data-driven executives** who need confidence, transparency, and speed in data operations.

---

## Core Capabilities

### 🔁 End-to-End Pipeline Orchestration
- Trigger pipelines on demand with configurable parameters
- Execute dbt builds and documentation generation
- Integrate seamlessly with Prefect deployments

### 📊 Executive-Grade Visibility
- Live pipeline health scoring (success rate, SLA adherence, reliability)
- Clear run statuses mapped from technical states to business-friendly outcomes
- Historical audit trail of all pipeline executions

### ⚡ Real-Time Monitoring
- WebSocket-powered live updates for pipeline and run status
- Automatic UI refresh during execution (no manual reloads)
- Graceful fallback to polling when WebSockets are unavailable

### 🧪 Data Quality & Artifacts
- Automatic ingestion of dbt artifacts (manifests, run results)
- Visibility into test failures and transformation outcomes
- Centralized artifact storage per run for traceability

### 🔐 Governance & Control
- Role-based permissions for viewing and triggering pipelines
- Admin-controlled pipeline configuration
- Secure, auditable execution history

---

## Application Walkthrough

### 1. Command Center (Home Dashboard)
The **Command Center** provides a high-level operational overview:
- List of all active pipelines
- Recent pipeline runs across the organization
- Visual indicators for system scale, activity, and health

This page is designed for **at-a-glance executive insight**.

---

### 2. Pipeline Detail View
Selecting a pipeline opens its **Pipeline Detail** page:
- Pipeline metadata (name, slug, status)
- Health summary (grade, success rate, recent performance)
- Trigger controls for launching new runs
- Table of recent runs with status, timing, and Prefect state

This view is ideal for **pipeline owners and technical leads**.

---

### 3. Triggering a Pipeline
Authorized users can:
- Trigger a pipeline with optional dbt `--select` arguments
- Enable or disable dbt documentation generation
- Launch Prefect flow runs directly from the UI

Each trigger creates a fully tracked **Pipeline Run**.

---

### 4. Run Detail View
Each pipeline run has a dedicated **Run Detail** page:
- Executive status (Completed, Running, Failed, Cancelled)
- Prefect execution state
- Start time, finish time, and duration
- Live refresh and real-time updates
- dbt test failures (if any)
- Collected artifacts for audit and diagnostics

This page provides **deep operational transparency**.

---

## How to Use the App

### Admin Setup
1. Create Pipelines in the Django Admin:
   - Define pipeline name, slug, SLA, and Prefect deployment name
   - Configure health thresholds and UI accents
2. Assign user permissions:
   - `can_view_pipeline`
   - `can_trigger_pipeline`

### Running Pipelines
1. Navigate to the **Command Center**
2. Select a pipeline
3. Trigger a run with optional parameters
4. Monitor execution in real time
5. Review artifacts and outcomes after completion

### Monitoring Health
- Health scores are automatically calculated from recent runs
- SLA breaches, failures, and inactivity are reflected in grades
- Executives can quickly assess pipeline reliability without technical context

---

## Technical Architecture (High Level)

- **Backend:** Django, Django Channels
- **Orchestration:** Prefect (API-driven)
- **Transformations:** dbt
- **Real-Time:** WebSockets with polling fallback
- **Storage:** Relational database (runs, pipelines, artifacts)
- **UI:** Executive-grade dashboards with animations and live state

---

## Designed For

- Data Engineering Leaders
- Analytics & BI Teams
- Technical Executives
- Organizations scaling data operations with confidence

---

## Philosophy

**Data pipelines should be observable, governable, and trusted — not opaque.**  

---

## Status

**Production-ready • Scalable • Executive-grade**

## Author
Francoise Elis Okala|Software Engineer|Washington,DC USA