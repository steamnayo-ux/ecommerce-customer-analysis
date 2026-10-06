from pathlib import Path
import pandas as pd


# ==========================================
# 1. 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. 데이터 불러오기
# ==========================================

customers = pd.read_csv(
    RAW_DIR / "olist_customers_dataset.csv"
)

orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv"
)

order_items = pd.read_csv(
    RAW_DIR / "olist_order_items_dataset.csv"
)

products = pd.read_csv(
    RAW_DIR / "olist_products_dataset.csv"
)

category_translation = pd.read_csv(
    RAW_DIR / "product_category_name_translation.csv"
)


# ==========================================
# 3. 주문 데이터 전처리
# ==========================================

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column])


# 배송 완료 주문만 분석 대상으로 사용
orders_delivered = orders[
    orders["order_status"] == "delivered"
].copy()


# ==========================================
# 4. 고객 정보 연결
# ==========================================

orders_customers = orders_delivered.merge(
    customers[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state"
        ]
    ],
    on="customer_id",
    how="left"
)


# ==========================================
# 5. 상품 정보 연결
# ==========================================

order_items_products = order_items.merge(
    products[
        [
            "product_id",
            "product_category_name"
        ]
    ],
    on="product_id",
    how="left"
)


# ==========================================
# 6. 카테고리 영문명 연결
# ==========================================

order_items_products = order_items_products.merge(
    category_translation,
    on="product_category_name",
    how="left"
)


# ==========================================
# 7. 주문 + 상품 데이터 연결
# ==========================================

order_details = orders_customers.merge(
    order_items_products[
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "price",
            "freight_value",
            "product_category_name",
            "product_category_name_english"
        ]
    ],
    on="order_id",
    how="left"
)


# ==========================================
# 8. 분석용 매출 컬럼 생성
# ==========================================

order_details["sales_amount"] = order_details["price"]

order_details["total_amount"] = (
    order_details["price"]
    + order_details["freight_value"]
)


# ==========================================
# 9. 분석용 데이터 저장
# ==========================================

orders_customers.to_csv(
    PROCESSED_DIR / "orders_customers.csv",
    index=False
)

order_details.to_csv(
    PROCESSED_DIR / "order_details.csv",
    index=False
)


# ==========================================
# 10. 결과 확인
# ==========================================

print("=" * 70)
print("전처리 완료")
print("=" * 70)

print(f"배송 완료 주문 수: {orders_delivered['order_id'].nunique():,}")
print(f"분석 고객 수: {orders_customers['customer_unique_id'].nunique():,}")
print(f"상품 주문 행 수: {len(order_details):,}")

print("\n생성된 파일:")

print(PROCESSED_DIR / "orders_customers.csv")
print(PROCESSED_DIR / "order_details.csv")

print("\norder_details 컬럼:")
print(list(order_details.columns))