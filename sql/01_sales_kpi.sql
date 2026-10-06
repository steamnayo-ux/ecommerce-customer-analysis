-- 1. 총 상품 매출
SELECT
    ROUND(SUM(sales_amount), 2) AS total_product_sales
FROM order_details;


-- 2. 총 주문 금액 (상품 + 배송비)
SELECT
    ROUND(SUM(total_amount), 2) AS total_order_value
FROM order_details;


-- 3. 총 주문 수
SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM order_details;


-- 4. 평균 주문 금액 (상품 매출 기준)
WITH orders AS (
    SELECT
        order_id,
        SUM(sales_amount) AS order_sales
    FROM order_details
    GROUP BY order_id
)
SELECT
    ROUND(AVG(order_sales), 2) AS aov
FROM orders;


-- 5. 월별 상품 매출
SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    ROUND(SUM(sales_amount), 2) AS monthly_product_sales
FROM order_details
GROUP BY 1
ORDER BY 1;


-- 6. 월별 주문 수
SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    COUNT(DISTINCT order_id) AS monthly_orders
FROM order_details
GROUP BY 1
ORDER BY 1;