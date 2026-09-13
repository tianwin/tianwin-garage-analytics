#!/usr/bin/env python3
"""Build a privacy-safe public dataset from a private operational CSV.

The raw file is read locally and is never copied into this repository.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cleaning import normalize_payment_method  # noqa: E402
from src.service_classification import classify_service  # noqa: E402


def _number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")


def _column(frame: pd.DataFrame, name: str) -> pd.Series:
    """Return a source column or an aligned missing-value series."""
    return frame[name] if name in frame else pd.Series(index=frame.index, dtype="object")


def _redact_text(value: object) -> str | None:
    """Remove common identifiers that may have leaked into service text."""
    if pd.isna(value) or not str(value).strip():
        return None
    text = str(value).strip()
    text = re.sub(r"\b[A-HJ-NPR-Z0-9]{17}\b", "[REDACTED]", text, flags=re.I)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[REDACTED]", text)
    text = re.sub(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)", "[REDACTED]", text)
    return text


def _vehicle_parts(value: object) -> tuple[float | None, str | None, str | None]:
    if pd.isna(value) or not str(value).strip():
        return None, None, None
    tokens = str(value).strip().split()
    year = float(tokens.pop(0)) if tokens and re.fullmatch(r"(?:19|20)\d{2}", tokens[0]) else None
    make = tokens.pop(0).title() if tokens else None
    model = " ".join(tokens).title() or None
    return year, make, model


def build_public_dataset(source: Path) -> pd.DataFrame:
    """Transform the private operational export into the public schema."""
    raw = pd.read_csv(source)
    raw = raw[raw["Date"].notna() & raw["Date"].astype(str).str.strip().ne("")].copy()
    raw = raw.reset_index(drop=True)
    customer_keys = raw["Customer"].fillna("").astype(str).str.strip().str.casefold()
    identified = sorted(key for key in customer_keys.unique() if key)
    mapping = {key: f"CUST-{index:03d}" for index, key in enumerate(identified, 1)}
    payment_source = raw["Payment Method"].where(raw["Payment Method"].notna(), raw["Paid?"])
    normalized_payment = payment_source.map(normalize_payment_method)
    vehicles = raw["Vehicle (Year Make Model)"].map(_vehicle_parts)
    part_cost = _number(raw["Part Cost"])
    total_price = _number(raw["Total Price"])
    paid = normalized_payment.isin(["Cash", "Zelle", "Paid - Method Unknown", "Other Paid"])
    public = pd.DataFrame(
        {
            "order_id": [f"ORD-{index:04d}" for index in range(1, len(raw) + 1)],
            "order_date": pd.to_datetime(raw["Date"], errors="coerce").dt.strftime("%Y-%m-%d"),
            "order_time": raw["Time"].where(raw["Time"].notna(), None),
            "customer_id": customer_keys.map(mapping).where(customer_keys.ne(""), None),
            "vehicle_year": [item[0] for item in vehicles],
            "vehicle_make": [item[1] for item in vehicles],
            "vehicle_model": [item[2] for item in vehicles],
            "job_description": raw["Job / Notes"].map(_redact_text),
            "service_category": [
                classify_service(job, part, notes)
                for job, part, notes in zip(raw["Job / Notes"], raw["Part Name"], raw["Part Notes"], strict=True)
            ],
            "labor_charge": _number(raw["Labor"]),
            "labor_hours": _number(_column(raw, "Labor Time")),
            "trip_fee": _number(_column(raw, "Trip Fee")),
            "part_cost": part_cost,
            "part_price": _number(raw["Part Price"]),
            "total_price": total_price,
            "payment_method": normalized_payment,
            "is_paid": paid,
            "recorded_contribution": total_price.where(paid, 0).fillna(0) - part_cost.fillna(0),
            "part_cost_recorded": raw["Part Cost"].notna() & raw["Part Cost"].astype(str).str.strip().ne(""),
        }
    )
    return public


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Private source CSV (never copied)")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "public_orders.csv")
    args = parser.parse_args()
    public = build_public_dataset(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    public.to_csv(args.output, index=False)
    print(f"Wrote {len(public)} anonymized records to {args.output}")


if __name__ == "__main__":
    main()
