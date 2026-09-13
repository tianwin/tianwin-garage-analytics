"""Centralized, testable KPI definitions."""

from __future__ import annotations

import pandas as pd


def collected_revenue(df: pd.DataFrame) -> float:
    """Total price from paid orders."""
    return float(df.loc[df["is_paid"], "total_price"].fillna(0).sum())


def paid_orders(df: pd.DataFrame) -> int:
    """Number of orders classified as paid."""
    return int(df["is_paid"].sum())


def average_ticket(df: pd.DataFrame) -> float:
    """Collected revenue divided by paid orders."""
    count = paid_orders(df)
    return collected_revenue(df) / count if count else 0.0


def recorded_contribution(df: pd.DataFrame) -> float:
    """Paid revenue less recorded part cost; not net profit."""
    paid = df[df["is_paid"]]
    return float((paid["total_price"].fillna(0) - paid["part_cost"].fillna(0)).sum())


def customer_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Return revenue and order counts for identified customers."""
    identified = df[df["customer_id"].notna() & df["customer_id"].astype(str).str.strip().ne("")]
    return identified.groupby("customer_id", as_index=False).agg(
        orders=("order_id", "nunique"),
        collected_revenue=("total_price", lambda s: float(s[identified.loc[s.index, "is_paid"]].fillna(0).sum())),
    )


def repeat_customer_revenue_share(df: pd.DataFrame) -> float:
    """Revenue from customers with >=2 orders / identified-customer revenue."""
    customers = customer_revenue(df)
    total = customers["collected_revenue"].sum()
    return float(customers.loc[customers["orders"] >= 2, "collected_revenue"].sum() / total) if total else 0.0


def top_five_customer_share(df: pd.DataFrame) -> float:
    """Top-five customer revenue / identified-customer revenue."""
    customers = customer_revenue(df)
    total = customers["collected_revenue"].sum()
    return float(customers.nlargest(5, "collected_revenue")["collected_revenue"].sum() / total) if total else 0.0


def part_cost_coverage(df: pd.DataFrame) -> float:
    """Share of eligible orders with an explicitly recorded part cost."""
    return float(df["part_cost_recorded"].sum() / len(df)) if len(df) else 0.0


def summary_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    """Calculate dashboard KPIs from one filtered order set."""
    customers = customer_revenue(df)
    return {
        "collected_revenue": collected_revenue(df),
        "paid_orders": paid_orders(df),
        "average_ticket": average_ticket(df),
        "recorded_contribution": recorded_contribution(df),
        "repeat_revenue_share": repeat_customer_revenue_share(df),
        "top_five_share": top_five_customer_share(df),
        "part_cost_coverage": part_cost_coverage(df),
        "identified_customers": int(len(customers)),
        "repeat_customer_count": int((customers["orders"] >= 2).sum()),
    }
