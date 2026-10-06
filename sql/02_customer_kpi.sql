-- 1. 전체 고객 수
SELECT
    COUNT(DISTINCT customer_unique_id) AS total_customers
FROM orders_customers;


-- 2. 1회 구매 고객 vs 재구매 고객
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders_customers
    GROUP BY customer_unique_id
)

SELECT
    CASE
        WHEN order_count = 1 THEN 'one_time'
        ELSE 'repeat'
    END AS customer_type,
    COUNT(*) AS customer_count
FROM customer_orders
GROUP BY 1
ORDER BY 1;


-- 3. 재구매 고객 비율
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders_customers
    GROUP BY customer_unique_id
)

SELECT
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE order_count >= 2)
        / COUNT(*),
        2
    ) AS repeat_customer_rate
FROM customer_orders;


-- 4. 고객당 평균 주문 횟수
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders_customers
    GROUP BY customer_unique_id
)

SELECT
    ROUND(AVG(order_count), 2) AS avg_orders_per_customer
FROM customer_orders;

-- 5. 고객 유형별 매출
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders_customers
    GROUP BY customer_unique_id
),
customer_revenue AS (
    SELECT
        customer_unique_id,
        SUM(total_amount) AS revenue
    FROM order_details
    GROUP BY customer_unique_id
)

SELECT
    CASE
        WHEN co.order_count = 1 THEN 'one_time'
        ELSE 'repeat'
    END AS customer_type,
    ROUND(SUM(cr.revenue), 2) AS total_revenue
FROM customer_orders co
JOIN customer_revenue cr
    ON co.customer_unique_id = cr.customer_unique_id
GROUP BY 1
ORDER BY total_revenue DESC;


-- 6. 재구매 고객 매출 기여율
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders_customers
    GROUP BY customer_unique_id
),
customer_revenue AS (
    SELECT
        customer_unique_id,
        SUM(total_amount) AS revenue
    FROM order_details
    GROUP BY customer_unique_id
)

SELECT
    ROUND(
        100.0 * SUM(
            CASE
                WHEN co.order_count >= 2 THEN cr.revenue
                ELSE 0
            END
        ) / SUM(cr.revenue),
        2
    ) AS repeat_customer_revenue_rate
FROM customer_orders co
JOIN customer_revenue cr
    ON co.customer_unique_id = cr.customer_unique_id;
