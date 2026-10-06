-- 1. 카테고리별 상품 매출
SELECT
    COALESCE(
        product_category_name_english,
        'unknown'
    ) AS category,
    ROUND(SUM(sales_amount), 2) AS product_sales
FROM order_details
GROUP BY 1
ORDER BY product_sales DESC;


-- 2. 카테고리별 주문 수
SELECT
    COALESCE(
        product_category_name_english,
        'unknown'
    ) AS category,
    COUNT(DISTINCT order_id) AS order_count
FROM order_details
GROUP BY 1
ORDER BY order_count DESC;


-- 3. 상위 10개 카테고리
SELECT
    COALESCE(
        product_category_name_english,
        'unknown'
    ) AS category,
    ROUND(SUM(sales_amount), 2) AS product_sales
FROM order_details
GROUP BY 1
ORDER BY product_sales DESC
LIMIT 10;


-- 4. 카테고리별 평균 주문 금액
WITH category_orders AS (
    SELECT
        product_category_name_english AS category,
        order_id,
        SUM(sales_amount) AS order_sales
    FROM order_details
    GROUP BY 1, 2
)

SELECT
    COALESCE(category, 'unknown') AS category,
    ROUND(AVG(order_sales), 2) AS avg_order_sales
FROM category_orders
GROUP BY 1
ORDER BY avg_order_sales DESC;