# 📊 Mystics Insight Hub  
### An Executive-Grade WNBA Analytics Platform (Washington Mystics)

---

## 🏀 Overview

**Mystics Insight Hub** is a high-fidelity, executive-level analytics application built with **Django** and **Chart.js**, designed to deliver **decision-ready insights** into WNBA team and player performance.

The platform centers on the **Washington Mystics** while supporting **league-wide analysis and comparisons**, interactive dashboards, and storytelling-driven visualizations suitable for:

- Front-office executives  
- Coaching and analytics staff  
- Scouts and basketball operations  
- Senior software, data, and analytics engineering roles  

This application prioritizes **clarity, reliability, and production realism**, closely mirroring internal analytics tools used by professional sports organizations.

---

## ✨ Key Features

### 🧠 Executive Dashboard
A purpose-built command center for leadership and strategy:
- **Mystics Points Per Game (PPG)** — filled line chart (game-by-game)
- **Season comparison (2024 vs 2025)** — bar chart
- **Team vs Team comparison**
  - Select any two WNBA teams
  - Generate:
    - Line chart (points trend over time)
    - Bar chart (average PPG)
- Optimized for fast interpretation and executive briefings

---

### 👥 Player Intelligence
- Full league player directory
- Team and name filtering
- Individual player profiles with:
  - Season averages (PPG, RPG, APG, etc.)
  - Monthly scoring trends
  - Last 10 game performance logs

---

### 🏟 Team Analysis
- League-wide team directory
- Team detail pages featuring:
  - Active roster
  - Recent games
  - Game-derived scoring trendlines
- Designed to function **without reliance on restricted APIs**

---

### ⚡ Data Reliability by Design
- Uses **official game scores** as the primary data source
- Player and team box stats are **optional enhancements**
- Dashboards remain functional even when advanced stats endpoints are unavailable
- Cached API responses for performance and stability

---

## 🛠 Technology Stack

| Layer | Tools |
|---|---|
| Backend | Django 4.x |
| Database | SQLite (dev) / PostgreSQL-ready |
| Frontend | Django Templates + Vanilla JavaScript |
| Visualization | Chart.js (theme-aware) |
| Data Source | BALLDONTLIE WNBA API |
| Caching | Django `cache_page` |
| Styling | Custom CSS (dark/light mode, glassmorphism) |

---

## 🧱 Architecture (Diagram-Style)

```text
        
        ┌──────────────────────┐     ┌──────────────────────────────┐     ┌──────────────────────────────┐
│     Web Browser      │     │     Django Templates (UI)    │     │     Internal JSON APIs       │
│ (Exec / Analyst UI)  │────▶│                              │────▶│                              │
│                      │     │  • home / dashboard          │     │  • /api/mystics/ppg          │
│  • Dark / Light UI   │     │  • executive_dashboard       │     │  • /api/compare/teams        │
│  • Chart.js visuals  │     │  • players / teams           │     │  • /api/team/<id>/trend      │
│  • Fast read views   │     │                              │     │                              │
│                      │     │  Note: UI stays functional   │     │  Note: APIs are read-only,   │
│                      │     │  even if APIs are limited    │     │  deterministic, and safe     │
└──────────────────────┘     └──────────────┬───────────────┘     └──────────────┬───────────────┘
                                            │   JSON fetch (cached)               │
                                            ▼                                     ▼
                                ┌──────────────────────────────┐     ┌──────────────────────────────┐
                                │      Django ORM Layer        │◀────│        Cached Querysets       │
                                │                              │     │        (cache_page)          │
                                │  Models:                     │     │                              │
                                │   • Team                     │     │  • Reduces API calls         │
                                │   • Player                   │     │  • Stabilizes dashboards     │
                                │   • Game                     │     │  • Improves page latency     │
                                │   • PlayerStat* (optional)   │     │                              │
                                │                              │     │  * Critical for exec demos   │
                                └──────────────┬───────────────┘     └──────────────────────────────┘
                                               │
                                               ▼
                                ┌──────────────────────────────┐     ┌──────────────────────────────┐
                                │        Local Database        │────▶│     BALLDONTLIE WNBA API     │
                                │                              │     │                              │
                                │  • SQLite (dev)              │     │  • Teams                     │
                                │  • PostgreSQL-ready          │     │  • Players                   │
                                │                              │     │  • Games                     │
                                │  Note: Game-level data is    │     │  • Player stats (optional)   │
                                │  the primary source of truth │     │                              │
                                │                              │     │  Note: Core analytics do     │
                                │                              │     │  NOT depend on premium stats │
                                └──────────────────────────────┘     └──────────────────────────────┘
```
---

## 🔄 Data Synchronization

Data ingestion is handled via a custom Django management command:
`python manage.py mystics_sync --season 2024 --no-stats
`python manage.py mystics_sync --season 2025 --no-stats
Due to API_Key free tier limitation , stats data cannot be fetched.

## 🚀 Ideal Use Cases

- Sports analytics portfolios
- Senior software / data engineering interviews
- Analytics engineering demonstrations
- Internal dashboards for basketball operations

## 📌 Future Enhancements

- Playoff vs regular-season splits
- Quarterly scoring breakdowns
- Win-probability modeling
- Shot distribution and efficiency visuals
- Role-based access (executive vs analyst)

## 👤 Author

Francoise Elis Mbazoa Okala
Software Engineer | Data & Sports Analytics
Washington, DC