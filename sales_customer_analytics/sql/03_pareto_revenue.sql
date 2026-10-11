-- sales_customer_analytics/sql/03_pareto_revenue.sql
WITH category_revenue AS (
    SELECT
        COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_units_sold,
        ROUND(SUM(oi.price), 2) AS total_item_revenue,
        ROUND(SUM(oi.freight_value), 2) AS total_freight_revenue,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gross_value
    FROM fact_order_items oi
    INNER JOIN fact_orders o 
        ON oi.order_id = o.order_id
    INNER JOIN dim_products p 
        ON oi.product_id = p.product_id
    LEFT JOIN dim_category_translation t 
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 1
),

revenue_ranked AS (
    SELECT
        category_name,
        total_orders,
        total_units_sold,
        total_gross_value,
        ROUND(total_gross_value / SUM(total_gross_value) OVER () * 100, 2) AS pct_of_total_revenue,
        ROUND(
            SUM(total_gross_value) OVER (
                ORDER BY total_gross_value DESC 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) / SUM(total_gross_value) OVER () * 100, 
            2
        ) AS cumulative_revenue_pct
    FROM category_revenue
)

SELECT
    category_name,
    total_orders,
    total_units_sold,
    total_gross_value,
    pct_of_total_revenue,
    cumulative_revenue_pct,
    CASE 
        WHEN cumulative_revenue_pct <= 80.0 THEN 'Top 80% Driver'
        ELSE 'Tail 20%'
    END AS pareto_classification
FROM revenue_ranked
ORDER BY total_gross_value DESC;
