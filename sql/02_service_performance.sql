-- Service-category performance based on paid-order revenue.
SELECT service_category, count(DISTINCT order_id) AS orders,
       count(DISTINCT order_id) FILTER (WHERE is_paid) AS paid_orders,
       coalesce(sum(total_price) FILTER (WHERE is_paid), 0) AS collected_revenue,
       coalesce(avg(total_price) FILTER (WHERE is_paid), 0) AS average_ticket,
       coalesce(sum(total_price - coalesce(part_cost, 0)) FILTER (WHERE is_paid), 0) AS recorded_contribution
FROM orders GROUP BY 1 ORDER BY collected_revenue DESC, orders DESC;
