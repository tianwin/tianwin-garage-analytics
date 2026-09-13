# Methodology

## Business framing

The pipeline converts records created for day-to-day service work into consistent measures for revenue monitoring, service prioritization, retention, concentration, and data stewardship.

## Processing sequence

1. A local-only script strips identifying fields and creates stable anonymous customer IDs.
2. Schema validation prevents silent column drift.
3. Python standardizes payments, dates, numeric types, and explainable service categories.
4. The cleaned frame is registered as a DuckDB view.
5. Version-controlled SQL creates weekly, service, customer, payment, daily, and quality marts.
6. A centralized KPI layer calculates documented metrics.
7. Deterministic rules generate insights and recommendations.

## Reliability gating

Advanced analyses are not displayed when their required fields have insufficient coverage. Labor-efficiency and hourly-demand analysis are intentionally excluded because structured labor hours and order times do not meet the reliability threshold. Profitability, margin, geographic, status-funnel, and parts-status analysis are also excluded because their required costs, geography, or workflow states are incomplete or intentionally removed for privacy.

## Privacy

Names, phones, social IDs, exact addresses, VINs, plates, internal notes, credentials, and source order IDs are excluded. Repeat behavior is retained only through anonymous customer keys.
