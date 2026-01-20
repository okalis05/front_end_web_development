# Power BI Build — Executive Overview (Report #1)
## “Winning the Margins” — Boardroom Snapshot

This report is designed to answer:
1) Are we winning efficiently?
2) What changed recently?
3) Where should leaders focus?

---

## Data prep
1. Import CSV tables (dim_date, dim_team, dim_player, fact_games, fact_player_game, fact_availability, fact_attendance).
2. Confirm types:
   - date_key as whole number
   - dates as Date
3. Create relationships as in docs/data_model.md

---

## Core DAX Measures (starter set)
### Games
Games =
COUNTROWS(fact_games)

Wins =
SUM(fact_games[win])

Win % =
DIVIDE([Wins], [Games])

Avg PF =
AVERAGE(fact_games[points_for])

Avg PA =
AVERAGE(fact_games[points_against])

Avg Point Diff =
AVERAGEX(fact_games, fact_games[points_for] - fact_games[points_against])

### Availability
Player-Games =
COUNTROWS(fact_player_game)

Games Missed =
SUM(fact_availability[games_missed_flag])

Availability Rate =
VAR total =
COUNTROWS(fact_availability)
VAR active =
COUNTROWS(FILTER(fact_availability, fact_availability[status] = "Active"))
RETURN DIVIDE(active, total)

### Attendance
Avg Attendance =
AVERAGE(fact_attendance[attendance])

Attendance vs Baseline =
VAR baseline =
CALCULATE([Avg Attendance], ALL(dim_date))
RETURN [Avg Attendance] - baseline

---

## Pages
### Page 1 — Executive Overview (single-screen)
Visuals:
1. KPI Cards (top row)
   - Win %
   - Avg Point Diff
   - Availability Rate
   - Avg Attendance

2. Trend line (last N games)
   - Line: Avg Point Diff by date
   - Add Win/Loss markers using conditional formatting if desired

3. “What changed” delta panel
   - Show last 10 games vs previous 10 games:
     - Win %
     - Point Diff
     - Availability Rate
     - Attendance

4. Focus Table (right)
   - Teams or players driving deltas
   - Example:
     - Player impact proxy (minutes * plus_minus proxy)

Filters:
- Season
- Team
- Date range

---

## Publish
1) Publish to Power BI Service
2) Use “Publish to web” (portfolio-safe but public)
3) Copy the iframe embed URL and place it in Django settings:
POWERBI_VIZ_REPORTS["executive_overview"]["embed_url"] = "..."

Repeat for the other pillars later.
