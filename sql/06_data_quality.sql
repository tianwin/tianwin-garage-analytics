-- Missing values and explicitly recorded zeroes remain distinct.
SELECT 'Order Date' AS field, count(order_date) AS valid_records, count(*) AS eligible_records FROM orders
UNION ALL SELECT 'Customer ID', count(*) FILTER (WHERE customer_id IS NOT NULL AND trim(customer_id) <> ''), count(*) FROM orders
UNION ALL SELECT 'Vehicle', count(*) FILTER (WHERE vehicle_make IS NOT NULL AND trim(vehicle_make) <> ''), count(*) FROM orders
UNION ALL SELECT 'Payment Classification', count(*) FILTER (WHERE payment_method_normalized <> 'Unknown'), count(*) FROM orders
UNION ALL SELECT 'Service Classification', count(*) FILTER (WHERE service_category NOT IN ('Uncategorized', 'Other')), count(*) FROM orders
UNION ALL SELECT 'Part Cost', count(*) FILTER (WHERE part_cost_recorded), count(*) FROM orders
UNION ALL SELECT 'Labor Hours', count(labor_hours), count(*) FROM orders
UNION ALL SELECT 'Order Time', count(*) FILTER (WHERE order_time IS NOT NULL AND trim(order_time) <> ''), count(*) FROM orders;
