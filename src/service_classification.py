"""Explainable rule-based service classification."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

# Ordered precedence is intentional: distinctive multi-word phrases are evaluated first.
CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("AC / HVAC", ("air conditioning", "a/c", "ac compressor", "ac relay", "hvac")),
    ("Cooling System", ("crossover pipe", "water pump", "thermostat", "radiator", "coolant")),
    ("Suspension / Steering", ("control arm", "sway bar", "cv axle", "strut", "suspension", "steering", "axle")),
    ("Glass / Mirror / Body", ("windshield", "mirror", "window", "seal", "wiper")),
    ("Diagnostic", ("check engine", "diagnostic", "diagnosis", "inspection")),
    ("Roadside / Tire", ("roadside", "tire", "patch", "rotation")),
    ("Battery / Electrical", ("battery", "alternator", "starter", "electrical")),
    ("Oil / Fluids", ("oil change", "transmission oil", "differential", "brake fluid", "fluid", "flush")),
    ("Brakes", ("brake", "brakes", "pad", "pads", "rotor", "rotors", "caliper")),
    ("Ignition / Engine", ("spark plug", "spark plugs", "ignition", "coil", "tensioner", "belt", "engine")),
)


def classify_service(*values: Any) -> str:
    """Classify combined free text using documented keyword precedence."""
    pieces = [str(value).lower() for value in values if not pd.isna(value) and str(value).strip()]
    if not pieces:
        return "Uncategorized"
    text = re.sub(r"\s+", " ", " ".join(pieces))
    for category, terms in CATEGORY_RULES:
        if any(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) for term in terms):
            return category
    return "Other"
