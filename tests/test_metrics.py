import pandas as pd
import pytest

from src.metrics import (
    average_ticket,
    collected_revenue,
    recorded_contribution,
    repeat_customer_revenue_share,
    top_five_customer_share,
)


@pytest.fixture
def orders():
    return pd.DataFrame(
        {
            "order_id": ["1", "2", "3", "4", "5", "6", "7"],
            "customer_id": ["A", "A", "B", "C", "D", "E", "F"],
            "is_paid": [True, True, True, True, True, True, False],
            "total_price": [100, 200, 300, 100, 100, 100, 900],
            "part_cost": [10, 20, 30, None, 10, 10, 1],
        }
    )


def test_core_metrics(orders):
    assert collected_revenue(orders) == 900
    assert average_ticket(orders) == 150
    assert recorded_contribution(orders) == 820
    assert repeat_customer_revenue_share(orders) == pytest.approx(1 / 3)
    assert top_five_customer_share(orders) == pytest.approx(1.0)
