-- sales_customer_analytics/sql/01_monthly_cohorts.sql
WITH customer_first_order AS (
    SELECT
        c.customer_unique_id,
        MIN(DATE_TRUNC('month', o.order_purchase_timestamp)) AS cohort_month
    FROM fact_orders o
    INNER JOIN dim_customers c 
        ON o.customer_id = c.customer_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id
),

customer_activities AS (
    SELECT
        c.customer_unique_id,
        f.cohort_month,
        DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
        (EXTRACT(YEAR FROM DATE_TRUNC('month', o.order_purchase_timestamp)) - EXTRACT(YEAR FROM f.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM DATE_TRUNC('month', o.order_purchase_timestamp)) - EXTRACT(MONTH FROM f.cohort_month)) AS period_index
    FROM fact_orders o
    INNER JOIN dim_customers c 
        ON o.customer_id = c.customer_id
    INNER JOIN customer_first_order f 
        ON c.customer_unique_id = f.customer_unique_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_unique_id) AS cohort_size
    FROM customer_first_order
    GROUP BY cohort_month
),

cohort_retention AS (
    SELECT
        a.cohort_month,
        a.period_index,
        COUNT(DISTINCT a.customer_unique_id) AS active_customers
    FROM customer_activities a
    GROUP BY a.cohort_month, a.period_index
)

SELECT
    r.cohort_month::DATE AS cohort_month,
    s.cohort_size,
    r.period_index,
    r.active_customers,
    ROUND((r.active_customers::DOUBLE / s.cohort_size) * 100, 2) AS retention_rate_pct
FROM cohort_retention r
INNER JOIN cohort_sizes s 
    ON r.cohort_month = s.cohort_month
WHERE r.cohort_month >= '2017-01-01' AND r.cohort_month <= '2018-06-01'
ORDER BY r.cohort_month, r.period_index;
