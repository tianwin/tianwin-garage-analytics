-- Anonymous customer activity supports retention and concentration analysis.
SELECT customer_id, count(DISTINCT order_id) AS orders,
       coalesce(sum(total_price) FILTER (WHERE is_paid), 0) AS collected_revenue,
       max(order_date) AS last_order_date,
       coalesce(sum(total_price - coalesce(part_cost, 0)) FILTER (WHERE is_paid), 0) AS recorded_contribution
FROM orders WHERE customer_id IS NOT NULL AND trim(customer_id) <> ''
GROUP BY 1 ORDER BY collected_revenue DESC;
