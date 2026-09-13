# Data Dictionary

| Field | Type | Definition | Source | Transformation | Known Limitations |
|---|---|---|---|---|---|
| order_id | string | Anonymous unique order key | Generated | Sequential public ID | Not the private operational ID |
| order_date | date | Service-order date | Operational record | ISO date coercion | Invalid dates become missing |
| order_time | string | Recorded order time | Operational record | Formatting normalized only | Sparse; not used for demand analysis |
| customer_id | string | Stable anonymous customer key | Customer identifier | Deterministic mapping to CUST-NNN | Missing customers remain missing |
| vehicle_year | number | Model year | Vehicle description | Parsed first four-digit token | Free-text parsing may be incomplete |
| vehicle_make | string | Vehicle manufacturer | Vehicle description | Parsed and title-cased | Naming is not fully standardized |
| vehicle_model | string | Vehicle model | Vehicle description | Remaining parsed text | Trims may be embedded in model |
| job_description | string | Service work description | Job / Notes | Common identifiers redacted | Free text and inconsistent detail |
| service_category | string | Broad rule-based service group | Job and part text | Ordered keyword rules | Classification can be Other/Uncategorized |
| labor_charge | decimal | Customer labor charge | Labor | Numeric coercion | Not employee labor cost |
| labor_hours | decimal | Recorded labor duration | Labor Time | Numeric coercion | Insufficient coverage |
| trip_fee | decimal | Customer trip fee | Trip Fee | Numeric coercion | Missing may not mean zero |
| part_cost | decimal | Recorded part acquisition cost | Part Cost | Numeric coercion | Incomplete historical coverage |
| part_price | decimal | Customer part charge | Part Price | Numeric coercion | Missing may not mean zero |
| total_price | decimal | Total customer charge | Total Price | Numeric coercion | Revenue only when paid |
| payment_method | string | Normalized payment classification | Payment Method / Paid? | Cash, Zelle, unknown-paid, unpaid, unknown, other-paid | Historical paid flags may omit method |
| is_paid | boolean | Whether classification indicates paid | Normalized payment | Deterministic mapping | Depends on source labels |
| recorded_contribution | decimal | Paid Total Price less recorded Part Cost | Derived | Missing part cost treated as zero for amount only | Must be paired with coverage; not profit |
| part_cost_recorded | boolean | Whether Part Cost was explicitly present | Part Cost | Presence flag before numeric fill | Does not assess correctness |
