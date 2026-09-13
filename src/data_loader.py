"""Public data loading entry point."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.cleaning import clean_orders
from src.config import DATA_PATH
from src.service_classification import classify_service
from src.validation import validate_schema


def load_orders(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load, validate, normalize, and classify the public order dataset."""
    raw = pd.read_csv(path, keep_default_na=True)
    validate_schema(raw)
    cleaned = clean_orders(raw)
    combined = cleaned.apply(
        lambda row: classify_service(row.get("job_description"), row.get("part_name"), row.get("part_notes")),
        axis=1,
    )
    cleaned["service_category"] = cleaned["service_category"].where(
        cleaned["service_category"].notna() & cleaned["service_category"].astype(str).str.strip().ne(""),
        combined,
    )
    return cleaned
