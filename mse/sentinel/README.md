# Sentinel  
### Executive Decision Intelligence Platform  
*A real-time, anomaly-driven intelligence layer for financial, operational, and risk leadership*

---

## Executive Summary

**Sentinel** is an executive-grade decision intelligence platform built to **surface critical signals before they become material risk or lost opportunity**.

Sentinel continuously ingests operational metrics, detects statistically significant anomalies, and presents **clear, actionable insights** through a cinematic, board-ready interface. It is designed for **financially regulated, risk-sensitive environments** where early detection, transparency, and explainability matter.

This implementation is a **first-class Django application** embedded inside the broader `mse` platform and demonstrates **senior-level system design, data engineering, and product thinking**.

---

## What Problem Sentinel Solves

Modern organizations suffer from:
- Delayed awareness of risk and performance degradation
- Dashboards that describe the past instead of warning about the future
- Fragmented signals across teams and systems
- Lack of explainability when metrics move unexpectedly

**Sentinel addresses this by acting as a real-time control tower**, continuously answering:

 *“What is changing right now, why does it matter, and what should leadership do next?”*

---

## Core Capabilities

### 1. Signal Ingestion
- Continuous background ingestion of domain KPIs
- Industry-specific baselines and distributions
- Deterministic, auditable metric storage

### 2. Anomaly Detection
- Rolling statistical anomaly detection (z-score based)
- Severity scoring (1–5) aligned with executive urgency
- Transparent math — no black-box decisions

### 3. Event Intelligence
- Automatic generation of alert events
- Contextual explanations tied to domain KPIs
- Clear separation between **signal**, **event**, and **decision**

### 4. Executive Visualization
- Minimal, high-signal dashboards
- Live KPI tiles and alert streams
- Language tailored to executive stakeholders, not engineers

### 5. Industry-Driven Architecture
- One core system
- Multiple industry “worlds” unlocked via configuration
- Zero duplicated logic across domains

---

## Supported Industries (Config-Driven)

Sentinel currently supports four industry domains, each with its own KPIs, alerts, and executive actions:

| Industry | Focus |
|-------|------|
| **Sports** | Performance, fatigue risk, lineup efficiency |
| **Mortgage / FinTech** | Pipeline health, underwriting risk, revenue leakage |
| **Retail** | Conversion, fulfillment, inventory risk |
| **Healthcare** | Capacity, safety, throughput |

Each industry is defined by **configuration**, not code branching — enabling rapid expansion into new verticals.

---

## User Experience

### Wave Portal (Landing Experience)
- A cinematic sand-and-ocean wave animation
- Wave direction changes → color shifts → industry option appears
- Hovering an option **instantly unlocks** that industry’s Sentinel world
- No clutter, no dashboards — intentional executive calm

### Industry World
Once inside an industry:
- Live KPIs update continuously
- Anomalies surface automatically
- Recommended actions are presented alongside signals
- The **full scope of the platform is “unleashed”** for that domain

---

## Architecture Overview

Django (Monolith)
│
├── Sentinel App
│ ├── Portal (Wave UI)
│ ├── Industry Registry (Configs)
│ ├── Signals (Metrics + Events)
│ ├── Pipeline (Celery ingestion)
│ └── Dashboard (Executive UI)
│
├── Redis (Task broker)
└── Celery (Background processing)


**Why this architecture works:**
- Strong boundaries without microservice overhead
- Deterministic behavior (critical for fintech)
- Clear upgrade path to streaming and ML systems

---

## Data Flow (End-to-End)

1. **Celery Beat** schedules industry ingestion ticks
2. **Pipeline** generates or ingests KPI values
3. **Anomaly Engine** evaluates deviations from baseline
4. **Events** are created with severity and explanation
5. **Executive UI** polls APIs and renders live intelligence

No user action is required to “run” Sentinel — it is always on.

---

## How to Use Sentinel
Hover over the revealed industry option to enter its world.

---

### 2. Explore each Industry's World(`Sports,Healthcare , Retail , Mortgage`)

You will see:
- Live KPIs
- Alert stream
- Recommended executive actions
- Full platform scope documentation

---

### 3. Administrative Control (Optional)
Use Django Admin to:
- Inspect metrics and events
- Audit anomaly history
- Validate severity scoring

---

## Management Commands

### Seed Baseline Data
Initial baselines are required for anomaly detection.

```bash
python manage.py seed_sentinel
```
This command:
- Seeds historical KPI distributions
- Initializes each industry world
-Is idempotent and safe to re-run

### Background Processing
- Start Redis:
```bash
redis-server
```
- Start Celery Worker:
```bash
celery -A mse worker -l INFO
```
- Start Celery Beat:
```bash
celery -A mse beat -l INFO
```
Sentinel will begin producing live signals immediately.

## FinTech & Enterprise Design Principles

Sentinel is intentionally designed around:
- Explainability over black-box models
- Auditability over opaque dashboards
- Early detection over reactive reporting
- Executive clarity over raw data exposure
These principles align with:
- Financial risk management
- Regulatory scrutiny
- Board-level decision workflows

## Final Note

Sentinel is not a demo dashboard.
It is a decision intelligence platform — the kind built internally at financial institutions, fintech leaders, and high-stakes enterprises to ensure leadership is never surprised by critical change.

## Author
Francoise Elis Okala | Software Engineer | Washington,DC,USA