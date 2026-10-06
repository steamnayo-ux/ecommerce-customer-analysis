from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
order_items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")

print("=" * 70)
print("1. 주문 상태")
print("=" * 70)

print(orders["order_status"].value_counts())

print("\n주문 상태 비율 (%)")
print(
    orders["order_status"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("=" * 70)
print("2. 주문 날짜 범위")
print("=" * 70)

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

print("첫 주문:", orders["order_purchase_timestamp"].min())
print("마지막 주문:", orders["order_purchase_timestamp"].max())

print("=" * 70)
print("3. 주요 ID 개수")
print("=" * 70)

print("전체 주문 수:", orders["order_id"].nunique())
print("전체 고객 레코드:", customers["customer_id"].nunique())
print("실제 고객 수:", customers["customer_unique_id"].nunique())
print("주문 상품 행:", len(order_items))
print("상품 수:", order_items["product_id"].nunique())
print("판매자 수:", order_items["seller_id"].nunique())

print("=" * 70)
print("4. 고객의 재구매 여부")
print("=" * 70)

customer_order_count = (
    orders
    .merge(
        customers[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="left"
    )
    .groupby("customer_unique_id")["order_id"]
    .nunique()
)

print("1회 구매 고객:", (customer_order_count == 1).sum())
print("2회 이상 구매 고객:", (customer_order_count >= 2).sum())

print("\n구매 횟수별 고객 수:")
print(customer_order_count.value_counts().sort_index().head(10))

print("=" * 70)
print("5. JOIN 가능 여부")
print("=" * 70)

print(
    "orders → customers:",
    orders["customer_id"].isin(customers["customer_id"]).mean() * 100,
    "%"
)

print(
    "order_items → orders:",
    order_items["order_id"].isin(orders["order_id"]).mean() * 100,
    "%"
)

print(
    "payments → orders:",
    payments["order_id"].isin(orders["order_id"]).mean() * 100,
    "%"
)