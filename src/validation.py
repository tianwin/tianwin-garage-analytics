"""Schema and data-quality validation."""

from __future__ import annotations

import pandas as pd

from src.config import reliability_label

REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "order_time",
    "customer_id",
    "vehicle_year",
    "vehicle_make",
    "vehicle_model",
    "job_description",
    "service_category",
    "labor_charge",
    "labor_hours",
    "trip_fee",
    "part_cost",
    "part_price",
    "total_price",
    "payment_method",
    "is_paid",
    "recorded_contribution",
    "part_cost_recorded",
}


def validate_schema(frame: pd.DataFrame) -> None:
    """Raise a clear error when required public fields are missing."""
    missing = REQUIRED_COLUMNS - set(frame.columns.str.strip().str.lower())
    if missing:
        raise ValueError(f"Public dataset is missing required columns: {sorted(missing)}")


def _valid_text(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype(str).str.strip().ne("")


def data_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate coverage without treating numeric zero as missing or blank as valid."""
    missing = pd.Series(index=df.index, dtype="object")
    vehicle = (
        _valid_text(df.get("vehicle_make", missing))
        | _valid_text(df.get("vehicle_model", missing))
        | df.get("vehicle_year", missing).notna()
    )
    checks = {
        "Order Date": df["order_date"].notna(),
        "Customer ID": _valid_text(df["customer_id"]),
        "Vehicle": vehicle,
        "Payment Classification": df["payment_method_normalized"].ne("Unknown"),
        "Service Classification": ~df["service_category"].isin(["Uncategorized", ""]),
        "Part Cost": df["part_cost_recorded"].eq(True),  # noqa: E712
        "Labor Hours": df["labor_hours"].notna(),
        "Order Time": _valid_text(df["order_time"]),
    }
    rows = []
    eligible = len(df)
    for field, valid in checks.items():
        count = int(valid.sum())
        coverage = count / eligible * 100 if eligible else 0.0
        rows.append(
            {
                "field": field,
                "valid_records": count,
                "eligible_records": eligible,
                "coverage_pct": coverage,
                "reliability": reliability_label(coverage),
            }
        )
    return pd.DataFrame(rows)
