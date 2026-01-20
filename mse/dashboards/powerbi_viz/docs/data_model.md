# powerbi_viz — Sports Executive Case Study Data Model
## Case Study: “Winning the Margins”

This case study is executive-first: connect **performance**, **availability**, and **fan impact**.

---

## Recommended Data Sources (Portfolio-Safe)

### A) Performance (Games + Team)
Use one of:
- Kaggle: NBA game logs (team-level)
- Any public NBA/WNBA team game results dataset (CSV)

### B) Player impact (Minutes + Basic/Advanced)
Use one of:
- Kaggle: NBA player game logs
- Any public player season stats dataset

### C) Availability (proxy)
Use one of:
- Kaggle: NBA injuries / DNP datasets
- “games missed” computed from player logs (missing games = out)

### D) Attendance (proxy)
Use one of:
- Kaggle: NBA attendance datasets
- Team home attendance by date

---

## Star Schema (Power BI)

### Dimensions
**dim_date**
- date_key (YYYYMMDD int)
- date (date)
- season (text)
- month, week, day_name

**dim_team**
- team_id (text)
- team_name (text)
- conference (text, optional)

**dim_player**
- player_id (text)
- player_name (text)
- team_id (text, current/primary)

### Facts
**fact_games**
- game_id (text)
- date_key (int)
- team_id (text)
- opponent_team_id (text)
- is_home (0/1)
- points_for (int)
- points_against (int)
- win (0/1)
- possessions (optional)
- off_rating_proxy = 100 * points_for / possessions (if possessions available)
- def_rating_proxy = 100 * points_against / possessions

**fact_player_game**
- game_id (text)
- date_key (int)
- team_id (text)
- player_id (text)
- minutes (float)
- points (int)
- rebounds (int)
- assists (int)
- plus_minus (int, optional)
- usage_proxy (optional)
- impact_score_proxy (measure)

**fact_availability**
- date_key (int)
- team_id (text)
- player_id (text)
- status (text: Active, Out, DNP)
- reason (text, optional)
- games_missed_flag (0/1)

**fact_attendance**
- game_id (text)
- date_key (int)
- team_id (text)
- attendance (int)
- revenue_index (optional proxy measure)

---

## Relationships (Power BI)
- dim_date[date_key] 1:* fact_games[date_key]
- dim_team[team_id] 1:* fact_games[team_id]
- dim_team[team_id] 1:* fact_player_game[team_id]
- dim_player[player_id] 1:* fact_player_game[player_id]
- dim_date[date_key] 1:* fact_player_game[date_key]
- dim_date[date_key] 1:* fact_availability[date_key]
- dim_team[team_id] 1:* fact_attendance[team_id]
- fact_games[game_id] 1:* fact_attendance[game_id] (if available)

---

## Executive KPI Measures (DAX ideas)
### Wins + efficiency
- Win % = DIVIDE([Wins], [Games])
- Avg Point Diff = AVERAGE(fact_games[points_for] - fact_games[points_against])

### Availability
- Availability Rate = DIVIDE([Active Player-Games], [Total Player-Games])
- Games Missed = SUM(fact_availability[games_missed_flag])

### Fan impact
- Attendance Avg = AVERAGE(fact_attendance[attendance])
- Attendance Lift (Streak) = compare attendance on win-streak games vs baseline

---

## Notes
- You can deliver this with **one season** for clean storytelling.
- Executives care about **trends, deltas, and focus areas**, not perfect tracking data.
