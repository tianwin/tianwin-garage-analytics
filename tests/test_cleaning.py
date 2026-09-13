import pandas as pd
import pytest

from src.cleaning import clean_orders, normalize_payment_method


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Zelle", "Zelle"),
        ("cash", "Cash"),
        ("Yes", "Paid - Method Unknown"),
        ("No", "Unpaid"),
        ("", "Unknown"),
        (None, "Unknown"),
        ("Paid - Method Unknown", "Paid - Method Unknown"),
        ("Unknown", "Unknown"),
    ],
)
def test_payment_normalization(raw, expected):
    assert normalize_payment_method(raw) == expected


def test_missing_cost_is_not_recorded_zero():
    frame = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "payment_method": ["cash", "cash"],
            "part_cost": [None, 0],
            "total_price": [100, 100],
            "vehicle_year": [2020, 2020],
        }
    )
    result = clean_orders(frame)
    assert result["part_cost_recorded"].tolist() == [False, True]
