-- sales_customer_analytics/sql/02_rfm_segments.sql
WITH reference_date AS (
    SELECT MAX(order_purchase_timestamp) + INTERVAL '1 day' AS max_date
    FROM fact_orders
    WHERE order_status NOT IN ('canceled', 'unavailable')
),

customer_aggregates AS (
    SELECT
        c.customer_unique_id,
        ROUND(DATE_PART('day', r.max_date - MAX(o.order_purchase_timestamp)), 0) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(p.payment_value), 2) AS monetary_value
    FROM fact_orders o
    INNER JOIN dim_customers c 
        ON o.customer_id = c.customer_id
    INNER JOIN fact_order_payments p 
        ON o.order_id = p.order_id
    CROSS JOIN reference_date r
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id, r.max_date
),

rfm_scores AS (
    SELECT
        customer_unique_id,
        recency_days,
        frequency,
        monetary_value,
        -- Recency: 5 = Most Recent, 1 = Oldest
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- Frequency: Discrete rule-based scoring (prevents NTILE ties on one-time buyers)
        CASE 
            WHEN frequency >= 4 THEN 5
            WHEN frequency = 3 THEN 4
            WHEN frequency = 2 THEN 3
            ELSE 1
        END AS f_score,
        -- Monetary: 5 = Highest GMV, 1 = Lowest GMV
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM customer_aggregates
)

SELECT
    customer_unique_id,
    recency_days,
    frequency,
    monetary_value,
    r_score,
    f_score,
    m_score,
    (r_score * 100 + f_score * 10 + m_score) AS rfm_combined,
    CASE 
        WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score = 1 THEN 'New / Recent One-Timers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At-Risk High-Value'
        WHEN r_score <= 2 AND f_score = 1 AND m_score >= 4 THEN 'Dormant Big Spenders'
        WHEN r_score = 1 AND f_score = 1 THEN 'Lost Low-Value'
        ELSE 'General / Potential'
    END AS customer_segment
FROM rfm_scores
ORDER BY monetary_value DESC;
