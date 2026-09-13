"""Deterministic executive insight generation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.metrics import repeat_customer_revenue_share, top_five_customer_share


@dataclass(frozen=True)
class Insight:
    title: str
    statement: str
    metric: str
    severity: str = "info"


def _change(current: float, prior: float) -> float | None:
    return (current - prior) / prior if prior else None


def revenue_trend_insight(weekly: pd.DataFrame) -> Insight:
    """Compare the latest four active weeks with the preceding four."""
    active = weekly[weekly["paid_orders"] > 0].sort_values("week_start")
    current, prior = active.tail(4), active.iloc[-8:-4]
    if prior.empty or current.empty:
        return Insight(
            "Revenue Trend",
            "More active weeks are needed for a reliable four-week comparison.",
            "Insufficient history",
            "warning",
        )
    revenue_change = _change(current["collected_revenue"].sum(), prior["collected_revenue"].sum())
    volume_change = _change(current["paid_orders"].sum(), prior["paid_orders"].sum())
    ticket_change = _change(
        current["collected_revenue"].sum() / current["paid_orders"].sum(),
        prior["collected_revenue"].sum() / prior["paid_orders"].sum(),
    )
    direction = "increased" if revenue_change is not None and revenue_change >= 0 else "decreased"
    statement = f"Collected revenue {direction} {abs(revenue_change or 0):.1%} versus the previous four active weeks."
    if volume_change is not None and ticket_change is not None:
        if volume_change > 0 and ticket_change > 0:
            statement += " The change coincided with both higher order volume and a higher average ticket."
        elif abs(volume_change) > abs(ticket_change):
            statement += " Order-volume movement was larger than average-ticket movement over the comparison."
        else:
            statement += " Average-ticket movement was larger than order-volume movement over the comparison."
    return Insight(
        "Revenue Trend",
        statement,
        f"{revenue_change or 0:+.1%}",
        "positive" if (revenue_change or 0) >= 0 else "warning",
    )


def repeat_customer_insight(df: pd.DataFrame) -> Insight:
    share = repeat_customer_revenue_share(df)
    return Insight(
        "Customer Retention",
        f"Repeat customers generated {share:.1%} of identified-customer revenue during the selected period.",
        f"{share:.1%}",
    )


def customer_concentration_insight(df: pd.DataFrame) -> Insight:
    share = top_five_customer_share(df)
    level = "high" if share >= 0.5 else "moderate" if share >= 0.3 else "relatively low"
    return Insight(
        "Customer Concentration",
        f"The top five customers generated {share:.1%} of identified-customer revenue, indicating {level} concentration in this dataset.",
        f"{share:.1%}",
        "warning" if share >= 0.5 else "info",
    )


def service_mix_insight(service: pd.DataFrame) -> Insight:
    if service.empty:
        return Insight(
            "Service Mix", "No paid service activity is available in the selected period.", "No data", "warning"
        )
    revenue = service.loc[service["collected_revenue"].idxmax(), "service_category"]
    frequency = service.loc[service["orders"].idxmax(), "service_category"]
    ticket = service.loc[service["average_ticket"].idxmax(), "service_category"]
    return Insight(
        "Service Mix",
        f"{revenue} generated the most collected revenue; {frequency} had the most orders; and {ticket} had the highest average ticket.",
        str(revenue),
    )


def revenue_interpretation(weekly: pd.DataFrame) -> str:
    """Describe recent revenue, volume, and ticket movements without causality claims."""
    active = weekly[weekly["paid_orders"] > 0].sort_values("week_start").tail(6)
    if len(active) < 2:
        return "Additional active weeks are needed to interpret recent performance."
    first, last = active.iloc[0], active.iloc[-1]
    revenue_up = last["collected_revenue"] >= first["collected_revenue"]
    volume_up = last["paid_orders"] >= first["paid_orders"]
    ticket_up = last["average_ticket"] >= first["average_ticket"]
    return (
        f"Across the visible active-week comparison, revenue {'increased' if revenue_up else 'decreased'}. "
        f"Paid-order volume {'rose' if volume_up else 'fell'}, while average ticket {'rose' if ticket_up else 'fell'}, showing how both components moved alongside revenue."
    )
