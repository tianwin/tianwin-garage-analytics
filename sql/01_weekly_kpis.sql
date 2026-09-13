-- Weekly revenue, volume, average ticket, and recorded contribution.
SELECT CAST(date_trunc('week', order_date) AS DATE) AS week_start,
       count(*) FILTER (WHERE is_paid) AS paid_orders,
       coalesce(sum(total_price) FILTER (WHERE is_paid), 0) AS collected_revenue,
       coalesce(avg(total_price) FILTER (WHERE is_paid), 0) AS average_ticket,
       coalesce(sum(total_price - coalesce(part_cost, 0)) FILTER (WHERE is_paid), 0) AS recorded_contribution
FROM orders WHERE order_date IS NOT NULL GROUP BY 1 ORDER BY 1;
