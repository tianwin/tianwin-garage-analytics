import pytest

from src.service_classification import classify_service


@pytest.mark.parametrize(
    ("text", "category"),
    [
        ("rear brake pads", "Brakes"),
        ("oil change", "Oil / Fluids"),
        ("water pump", "Cooling System"),
        ("battery replacement", "Battery / Electrical"),
        ("tire patch", "Roadside / Tire"),
        ("AC compressor", "AC / HVAC"),
    ],
)
def test_service_rules(text, category):
    assert classify_service(text) == category
