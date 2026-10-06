-- 1. 총 매출
SELECT
    SUM(total_amount) AS total_sales
FROM order_details;


-- 2. 총 주문 수
SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM order_details;


-- 3. 평균 주문 금액 (AOV)
SELECT
    AVG(order_total) AS aov
FROM (
    SELECT
        order_id,
        SUM(total_amount) AS order_total
    FROM order_details
    GROUP BY order_id
) AS orders;


-- 4. 월별 매출
SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    SUM(total_amount) AS monthly_sales
FROM order_details
GROUP BY 1
ORDER BY 1;


-- 5. 월별 주문 수
SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    COUNT(DISTINCT order_id) AS monthly_orders
FROM order_details
GROUP BY 1
ORDER BY 1;