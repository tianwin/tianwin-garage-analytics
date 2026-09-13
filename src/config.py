"""Shared application configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "public_orders.csv"
SQL_DIR = ROOT / "sql"
DATASET_LABEL = "Anonymized operational data"

PALETTE = {
    "primary": "#1F5A7A",
    "positive": "#2F7D62",
    "warning": "#B7791F",
    "negative": "#A33A3A",
    "muted": "#718096",
    "light": "#E7EEF2",
}

RELIABILITY_THRESHOLDS = (
    (90.0, "Strong"),
    (70.0, "Usable with caution"),
    (40.0, "Limited"),
    (0.0, "Insufficient"),
)


def reliability_label(coverage: float) -> str:
    """Return the documented reliability label for a percentage."""
    return next(label for minimum, label in RELIABILITY_THRESHOLDS if coverage >= minimum)
