"""Data normalization functions for public service-order records."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

PAID_UNKNOWN = {"yes", "paid"}
UNPAID = {"no", "unpaid", "not paid", "pending"}
KNOWN_PAID = {"cash": "Cash", "zelle": "Zelle"}


def normalize_payment_method(value: Any) -> str:
    """Normalize inconsistent historical payment labels."""
    if pd.isna(value) or not str(value).strip():
        return "Unknown"
    cleaned = re.sub(r"\s+", " ", str(value).strip().lower())
    if cleaned == "unknown":
        return "Unknown"
    if cleaned == "paid - method unknown":
        return "Paid - Method Unknown"
    if cleaned == "other paid":
        return "Other Paid"
    if cleaned in KNOWN_PAID:
        return KNOWN_PAID[cleaned]
    if cleaned in PAID_UNKNOWN:
        return "Paid - Method Unknown"
    if cleaned in UNPAID:
        return "Unpaid"
    return "Other Paid"


def clean_orders(frame: pd.DataFrame) -> pd.DataFrame:
    """Coerce the public schema and derive normalized analytical fields."""
    df = frame.copy()
    df.columns = [str(column).strip().lower() for column in df.columns]
    for column in ("order_date", "week_start"):
        if column in df:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    numeric = [
        "vehicle_year",
        "labor_charge",
        "labor_hours",
        "trip_fee",
        "part_cost",
        "part_price",
        "total_price",
        "recorded_contribution",
    ]
    for column in numeric:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    source = df.get("payment_method", pd.Series(index=df.index, dtype="object"))
    df["payment_method_normalized"] = source.map(normalize_payment_method)
    df["is_paid"] = df["payment_method_normalized"].isin(["Cash", "Zelle", "Paid - Method Unknown", "Other Paid"])
    df["part_cost_recorded"] = (
        df.get("part_cost_recorded", df.get("part_cost", pd.Series(index=df.index)).notna()).fillna(False).astype(bool)
    )
    df["recorded_contribution"] = df["total_price"].where(df["is_paid"], 0).fillna(0) - df["part_cost"].fillna(0)
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["week_start"] = df["order_date"] - pd.to_timedelta(df["order_date"].dt.weekday, unit="D")
    df["weekday"] = df["order_date"].dt.day_name()
    current_year = pd.Timestamp.today().year
    df["vehicle_age"] = current_year - df["vehicle_year"]
    return df
