"""Transparent rules that translate metrics into business actions."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Recommendation:
    title: str
    action: str
    rationale: str


def generate_recommendations(
    metrics: dict[str, float | int], service: pd.DataFrame, quality: pd.DataFrame
) -> list[Recommendation]:
    """Return the three highest-priority recommendations triggered by data."""
    candidates: list[tuple[int, Recommendation]] = []
    if float(metrics["part_cost_coverage"]) < 0.8:
        candidates.append(
            (
                100,
                Recommendation(
                    "Improve parts-cost capture",
                    "Record part cost explicitly on every eligible order before using contribution metrics for pricing decisions.",
                    f"Current part-cost coverage is {float(metrics['part_cost_coverage']):.1%}.",
                ),
            )
        )
    labor = quality.loc[quality["field"].eq("Labor Hours"), "coverage_pct"]
    if not labor.empty and labor.iloc[0] < 70:
        candidates.append(
            (
                95,
                Recommendation(
                    "Standardize labor-hour entry",
                    "Make labor-hour entry a required closeout step to unlock labor-productivity and scheduling analysis.",
                    f"Labor-hour coverage is {labor.iloc[0]:.1f}%.",
                ),
            )
        )
    if float(metrics["top_five_share"]) >= 0.5:
        candidates.append(
            (
                90,
                Recommendation(
                    "Reduce concentration risk",
                    "Expand acquisition beyond the current highest-value customer group while maintaining service for established customers.",
                    f"The top five customers contribute {float(metrics['top_five_share']):.1%} of identified-customer revenue.",
                ),
            )
        )
    if float(metrics["repeat_revenue_share"]) >= 0.3:
        candidates.append(
            (
                80,
                Recommendation(
                    "Prioritize retention",
                    "Use service reminders and maintenance follow-ups because returning customers are already a material revenue source.",
                    f"Repeat customers contribute {float(metrics['repeat_revenue_share']):.1%} of identified-customer revenue.",
                ),
            )
        )
    if not service.empty and service["collected_revenue"].sum() > 0:
        top = service.nlargest(1, "collected_revenue").iloc[0]
        share = top["collected_revenue"] / service["collected_revenue"].sum()
        if share >= 0.4:
            candidates.append(
                (
                    85,
                    Recommendation(
                        "Manage service-mix dependence",
                        f"Maintain capacity for {top['service_category']} while testing demand for adjacent services.",
                        f"This category contributes {share:.1%} of selected-period revenue.",
                    ),
                )
            )
    if len(candidates) < 3:
        candidates.extend(
            [
                (
                    30,
                    Recommendation(
                        "Review weekly performance",
                        "Use active-week revenue, order volume, and average ticket together when planning near-term capacity.",
                        "No single KPI fully explains revenue movement.",
                    ),
                ),
                (
                    20,
                    Recommendation(
                        "Protect classification quality",
                        "Review uncategorized descriptions and expand rules only when recurring patterns appear.",
                        "Rule-based categories remain auditable and reproducible.",
                    ),
                ),
            ]
        )
    return [item for _, item in sorted(candidates, key=lambda pair: pair[0], reverse=True)[:3]]
