-- Normalized payment-method mix.
SELECT payment_method_normalized AS payment_method,
       count(DISTINCT order_id) AS orders,
       coalesce(sum(total_price) FILTER (WHERE is_paid), 0) AS collected_revenue
FROM orders GROUP BY 1 ORDER BY collected_revenue DESC, orders DESC;
