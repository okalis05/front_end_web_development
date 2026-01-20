from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


# ----------------------------
# Sample dataset (bright demo)
# ----------------------------
# A small, realistic-ish healthcare readmissions dataset:
# - Subject matter: reducing readmissions (mission)
# - Fields mirror your earlier Tableau work: Facility ID/Name, State, Measure, dates, ratios/rates, discharges, readmissions
READMISSIONS_ROWS: List[Dict[str, Any]] = [
    # CA
    {"facility_id": "050001", "facility": "Sunrise Medical Center", "state": "CA", "measure": "Heart Failure", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.14, "expected_rate": 18.2, "predicted_rate": 20.9, "discharges": 840, "readmissions": 164},
    {"facility_id": "050002", "facility": "Bayview General", "state": "CA", "measure": "Pneumonia", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.05, "expected_rate": 16.8, "predicted_rate": 17.6, "discharges": 760, "readmissions": 119},
    {"facility_id": "050003", "facility": "Cedar Heights Hospital", "state": "CA", "measure": "COPD", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 0.96, "expected_rate": 19.6, "predicted_rate": 18.8, "discharges": 690, "readmissions": 123},

    # NY
    {"facility_id": "330001", "facility": "Hudson Peak Health", "state": "NY", "measure": "Heart Failure", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.22, "expected_rate": 17.4, "predicted_rate": 21.3, "discharges": 910, "readmissions": 192},
    {"facility_id": "330002", "facility": "Riverside Memorial", "state": "NY", "measure": "Pneumonia", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.10, "expected_rate": 16.2, "predicted_rate": 18.0, "discharges": 830, "readmissions": 150},
    {"facility_id": "330003", "facility": "Evergreen City Hospital", "state": "NY", "measure": "COPD", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 0.99, "expected_rate": 20.1, "predicted_rate": 19.9, "discharges": 640, "readmissions": 124},

    # TX
    {"facility_id": "450001", "facility": "Lone Star Regional", "state": "TX", "measure": "Heart Failure", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.08, "expected_rate": 18.9, "predicted_rate": 19.8, "discharges": 880, "readmissions": 165},
    {"facility_id": "450002", "facility": "Bluebonnet Medical", "state": "TX", "measure": "Pneumonia", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 0.93, "expected_rate": 17.1, "predicted_rate": 15.9, "discharges": 790, "readmissions": 118},
    {"facility_id": "450003", "facility": "Prairie View Hospital", "state": "TX", "measure": "COPD", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.16, "expected_rate": 20.8, "predicted_rate": 24.1, "discharges": 720, "readmissions": 173},

    # FL
    {"facility_id": "100001", "facility": "Palm Coast Health", "state": "FL", "measure": "Heart Failure", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.03, "expected_rate": 18.0, "predicted_rate": 18.5, "discharges": 860, "readmissions": 149},
    {"facility_id": "100002", "facility": "Gulfside Medical Center", "state": "FL", "measure": "Pneumonia", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 1.19, "expected_rate": 15.9, "predicted_rate": 19.0, "discharges": 805, "readmissions": 153},
    {"facility_id": "100003", "facility": "Coral Springs Hospital", "state": "FL", "measure": "COPD", "start": "2025-01-01", "end": "2025-03-31",
     "excess_ratio": 0.91, "expected_rate": 21.2, "predicted_rate": 19.3, "discharges": 610, "readmissions": 116},
]


# ----------------------------
# Dashboard schema
# ----------------------------
@dataclass(frozen=True)
class KPI:
    label: str
    value: str
    hint: str


@dataclass(frozen=True)
class VizBlock:
    # Every visualization is a "scene" that advances the dashboard mission.
    title: str
    sub_question: str
    chart_type: str
    # Payload is chart-type specific; the JS knows how to render each.
    payload: Dict[str, Any]
    kpis: List[KPI]
    insights: List[str]
    mission_link: str  # Required: explicit link to mission


@dataclass(frozen=True)
class CaseStudy:
    slug: str
    title: str
    mission: str  # subject matter for entire dashboard
    hero_tagline: str
    dataset_note: str
    blocks: List[VizBlock]
    final_answer_title: str
    final_answer: str
    recommendations: List[str]
    next_steps: List[str]


def get_case_studies() -> List[CaseStudy]:
    # CASE STUDY 1 (Healthcare)
    healthcare = CaseStudy(
        slug="readmissions-priority-engine",
        title="Readmissions Priority Engine",
        hero_tagline="A bright, executive case study that turns readmission metrics into a focused intervention plan.",
        mission="How do we reduce readmissions by prioritizing the highest-impact facilities, measures, and regions?",
        dataset_note="Sample dataset (demo) shaped like CMS readmissions fields: facility, state, measure, predicted vs expected, excess ratio, discharges, readmissions.",
        blocks=[
            VizBlock(
                title="Scene 1 — The Mission Baseline (Volume vs Risk)",
                sub_question="Where do high volume and high risk collide (the true intervention hotspots)?",
                chart_type="bubble_volume_risk",
                payload={
                    "rows": READMISSIONS_ROWS,
                    "x": "discharges",
                    "y": "excess_ratio",
                    "size": "readmissions",
                    "color": "measure",
                    "hover": ["facility", "state", "measure", "predicted_rate", "expected_rate"],
                },
                kpis=[
                    KPI("Priority Lens", "Volume × Risk", "Focus on discharges + excess ratio"),
                    KPI("Hotspot Definition", "High X & High Y", "High discharges + high excess ratio"),
                    KPI("Action", "Target first", "Start where impact is largest"),
                ],
                insights=[
                    "Hotspots are not always the worst ratio — they’re where ratio meets volume.",
                    "A moderate excess ratio can outrank a severe one if discharges are far higher.",
                    "Measure segmentation helps avoid one-size-fits-all interventions.",
                ],
                mission_link="This pinpoints *where* to focus first (highest impact), directly enabling targeted readmission reduction.",
            ),
            VizBlock(
                title="Scene 2 — Leaderboard of Concern (Top Facilities)",
                sub_question="Which facilities should be prioritized first based on combined impact?",
                chart_type="leaderboard_impact",
                payload={
                    "rows": READMISSIONS_ROWS,
                    "score_formula": "impact = discharges * max(0, excess_ratio - 1)",
                    "top_n": 8,
                },
                kpis=[
                    KPI("Metric", "Impact Score", "Discharges × excess above 1.0"),
                    KPI("Output", "Ranked Targets", "Top facilities by intervention value"),
                    KPI("Use", "Resource allocation", "Start with highest leverage"),
                ],
                insights=[
                    "The ranking separates ‘high-risk but small’ from ‘high-impact’ facilities.",
                    "This list is the operational starting point for quality teams.",
                    "Use it to structure pilot programs and staffing decisions.",
                ],
                mission_link="This produces a prioritized list of facilities to target, making the mission actionable.",
            ),
            VizBlock(
                title="Scene 3 — Measure Lens (Which conditions drive risk?)",
                sub_question="Which measures appear most associated with excess readmission risk and impact?",
                chart_type="measure_risk_bars",
                payload={
                    "rows": READMISSIONS_ROWS,
                    "group_by": "measure",
                },
                kpis=[
                    KPI("View", "By Measure", "Condition-level risk view"),
                    KPI("Read", "Avg Excess Ratio", "Risk signal per condition"),
                    KPI("Plan", "Intervention playbooks", "Tailor by condition"),
                ],
                insights=[
                    "Different measures respond to different operational levers (discharge planning, follow-up care, education).",
                    "A condition with slightly lower ratio can still dominate impact via volume.",
                    "Measure breakdown prevents misaligned interventions.",
                ],
                mission_link="This tells us *what type* of interventions to design (by measure), supporting mission-aligned action.",
            ),
            VizBlock(
                title="Scene 4 — Geographic Signal (State Hotspots)",
                sub_question="Which states show the strongest combination of risk and volume?",
                chart_type="state_heatmap",
                payload={
                    "rows": READMISSIONS_ROWS,
                    "group_by": "state",
                },
                kpis=[
                    KPI("Scope", "Regional", "State-level prioritization"),
                    KPI("Signal", "Risk × Volume", "Where to scale efforts"),
                    KPI("Benefit", "Rollout strategy", "Phased interventions"),
                ],
                insights=[
                    "Regional patterns can reveal staffing constraints, access-to-care, or follow-up gaps.",
                    "State-level signal helps plan rollout and training coverage.",
                    "Use geography to align partnerships and care coordination programs.",
                ],
                mission_link="This guides *where to deploy interventions* geographically, reducing readmissions efficiently.",
            ),
        ],
        final_answer_title="Final Answer — What should we do to reduce readmissions?",
        final_answer=(
            "Reduce readmissions by targeting the highest-impact facilities first: those with high discharges and excess ratio above 1.0. "
            "Then tailor interventions by measure (condition) and scale by state hotspots. "
            "This approach converts readmission metrics into a staged, resource-aware intervention plan."
        ),
        recommendations=[
            "Start with the Top 3–5 facilities by Impact Score and run a 6–8 week intervention pilot.",
            "Create measure-specific playbooks (Heart Failure, Pneumonia, COPD) with discharge + follow-up workflows.",
            "Scale to states showing both high volume and elevated excess ratios after early wins.",
        ],
        next_steps=[
            "Replace sample rows with your real CMS extract (or your cleaned dataset).",
            "Add facility type/ownership and patient demographics if available to sharpen drivers.",
            "Introduce time-series (quarterly) to validate improvement after interventions.",
        ],
    )

    # CASE STUDY 2 (FinTech-style)
    fintech = CaseStudy(
        slug="credit-risk-clarity-board",
        title="Credit Risk Clarity Board",
        hero_tagline="A bright, executive case study that turns loan risk signals into approval and pricing strategy.",
        mission="How do we approve more loans safely by identifying risk tiers and the strongest drivers of default?",
        dataset_note="This dashboard uses synthetic demo signals (for structure). Plug in LendingClub-style data when ready.",
        blocks=[
            VizBlock(
                title="Scene 1 — Risk Tier Map (Probability vs Amount)",
                sub_question="Where do we see high loan amounts combined with high default probability?",
                chart_type="synthetic_risk_scatter",
                payload={"seed": 7, "n": 240},
                kpis=[
                    KPI("Axes", "Probability × Amount", "Risk and exposure in one view"),
                    KPI("Goal", "Approve safely", "Shift portfolio to safer tiers"),
                    KPI("Use", "Policy design", "Define tier cutoffs"),
                ],
                insights=[
                    "High exposure + high probability clusters are the first policy targets.",
                    "Tiering makes approval decisions explainable and consistent.",
                    "Use this to set guardrails before model deployment.",
                ],
                mission_link="This reveals risk-exposure hotspots so we can approve more safely by adjusting policy tiers.",
            ),
            VizBlock(
                title="Scene 2 — Driver Waterfall (Why risk changes)",
                sub_question="Which features most push risk up or down for the portfolio?",
                chart_type="synthetic_driver_waterfall",
                payload={"seed": 11},
                kpis=[
                    KPI("Format", "Waterfall", "Driver contribution story"),
                    KPI("Outcome", "Explainability", "Executive-friendly reasoning"),
                    KPI("Action", "Policy levers", "Adjust thresholds"),
                ],
                insights=[
                    "Waterfall charts translate model logic into business levers.",
                    "Use top drivers to revise underwriting and pricing rules.",
                    "This is the bridge between analytics and policy.",
                ],
                mission_link="This identifies the strongest drivers so we can safely loosen approvals where drivers indicate stability.",
            ),
            VizBlock(
                title="Scene 3 — Tier Leaderboard (Portfolio composition)",
                sub_question="How much of our portfolio sits in each tier, and where should we rebalance?",
                chart_type="synthetic_tier_bars",
                payload={"seed": 19},
                kpis=[
                    KPI("View", "Tier Mix", "Portfolio distribution"),
                    KPI("Goal", "Rebalance", "Shift away from risk-heavy tiers"),
                    KPI("Impact", "Default control", "Reduce losses"),
                ],
                insights=[
                    "Portfolio shape matters as much as individual approvals.",
                    "Tier mix helps align business growth targets with risk appetite.",
                    "Use this to set quarterly risk limits.",
                ],
                mission_link="This shows how to rebalance tiers to approve more loans while controlling defaults.",
            ),
        ],
        final_answer_title="Final Answer — How do we approve more loans safely?",
        final_answer=(
            "Approve more loans safely by introducing clear risk tiers based on probability and exposure, "
            "tightening rules only in high-exposure/high-probability zones, and loosening where driver signals indicate stability. "
            "Use tier mix targets to keep portfolio risk within appetite while expanding approvals."
        ),
        recommendations=[
            "Define 4–5 tiers (Prime → Caution) and assign pricing/approval rules per tier.",
            "Use the top drivers (waterfall) to adjust thresholds rather than blanket rule changes.",
            "Set portfolio tier-mix caps and monitor weekly.",
        ],
        next_steps=[
            "Replace synthetic generator with LendingClub CSV ingestion.",
            "Add model score + calibration chart to validate probability quality.",
            "Track drift and tier migration over time.",
        ],
    )

    return [healthcare, fintech]


def get_case_by_slug(slug: str) -> CaseStudy | None:
    for c in get_case_studies():
        if c.slug == slug:
            return c
    return None
