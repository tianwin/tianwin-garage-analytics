-- Daily revenue and paid-method composition for the calendar.
SELECT CAST(order_date AS DATE) AS order_date, count(DISTINCT order_id) AS orders,
       coalesce(sum(total_price) FILTER (WHERE is_paid), 0) AS collected_revenue,
       coalesce(sum(total_price) FILTER (WHERE payment_method_normalized = 'Cash'), 0) AS cash_revenue,
       coalesce(sum(total_price) FILTER (WHERE payment_method_normalized = 'Zelle'), 0) AS zelle_revenue,
       coalesce(sum(total_price) FILTER (WHERE payment_method_normalized IN ('Paid - Method Unknown', 'Other Paid')), 0) AS other_paid_revenue
FROM orders WHERE order_date IS NOT NULL GROUP BY 1 ORDER BY 1;
