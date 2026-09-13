import pandas as pd

from src.validation import data_quality_summary


def test_blanks_not_counted_as_valid_zeroes():
    frame = pd.DataFrame(
        {
            "order_date": [pd.Timestamp("2026-01-01"), pd.NaT],
            "customer_id": ["", "CUST-001"],
            "vehicle_make": [None, "Toyota"],
            "payment_method_normalized": ["Unknown", "Cash"],
            "service_category": ["Uncategorized", "Brakes"],
            "part_cost_recorded": [False, True],
            "labor_hours": [None, 0],
            "order_time": ["", "09:00"],
        }
    )
    quality = data_quality_summary(frame).set_index("field")
    assert quality.loc["Part Cost", "valid_records"] == 1
    assert quality.loc["Labor Hours", "valid_records"] == 1
    assert quality.loc["Customer ID", "valid_records"] == 1
