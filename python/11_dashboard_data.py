import pandas as pd
from pathlib import Path


# ============================================================
# 1. 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ORDER_DETAILS_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "order_details.csv"
)

RFM_SEGMENTED_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "rfm_segmented.csv"
)

DASHBOARD_DIR = BASE_DIR / "dashboard"

DASHBOARD_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. 데이터 불러오기
# ============================================================

order_details = pd.read_csv(
    ORDER_DETAILS_PATH,
    parse_dates=["order_purchase_timestamp"],
)

rfm = pd.read_csv(
    RFM_SEGMENTED_PATH
)


print("=" * 60)
print("대시보드용 데이터 생성 시작")
print("=" * 60)


# ============================================================
# 3. 배송완료 데이터만 사용
# ============================================================

delivered = order_details[
    order_details["order_status"] == "delivered"
].copy()


print(f"배송완료 상세 데이터: {len(delivered):,}행")
print(
    f"배송완료 주문 수: "
    f"{delivered['order_id'].nunique():,}건"
)
print(
    f"배송완료 고객 수: "
    f"{delivered['customer_unique_id'].nunique():,}명"
)


# ============================================================
# 4. 월별 매출 데이터
# ============================================================

delivered["month"] = (
    delivered["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)


monthly_sales = (
    delivered
    .groupby("month")
    .agg(
        sales_amount=("sales_amount", "sum"),
        order_count=("order_id", "nunique"),
    )
    .reset_index()
)


monthly_sales["sales_amount"] = (
    monthly_sales["sales_amount"]
    .round(2)
)


monthly_sales.to_csv(
    DASHBOARD_DIR / "monthly_sales.csv",
    index=False,
    encoding="utf-8-sig",
)


print("\n[1] monthly_sales.csv 생성")
print(monthly_sales.head())


# ============================================================
# 5. 1회 구매 vs 재구매 고객
# ============================================================

customer_order_count = (
    delivered
    .groupby("customer_unique_id")["order_id"]
    .nunique()
)


customer_purchase_type = pd.DataFrame({
    "purchase_type": (
        customer_order_count
        .apply(
            lambda x:
            "1회 구매"
            if x == 1
            else "재구매"
        )
    )
})


customer_purchase_type = (
    customer_purchase_type
    .groupby("purchase_type")
    .size()
    .reset_index(name="customer_count")
)


total_customers = (
    customer_purchase_type["customer_count"]
    .sum()
)


customer_purchase_type["customer_ratio"] = (
    customer_purchase_type["customer_count"]
    / total_customers
    * 100
).round(2)


# 보기 좋은 순서로 정렬
purchase_order = {
    "1회 구매": 0,
    "재구매": 1,
}

customer_purchase_type["sort_order"] = (
    customer_purchase_type["purchase_type"]
    .map(purchase_order)
)


customer_purchase_type = (
    customer_purchase_type
    .sort_values("sort_order")
    .drop(columns="sort_order")
    .reset_index(drop=True)
)


customer_purchase_type.to_csv(
    DASHBOARD_DIR / "customer_purchase_type.csv",
    index=False,
    encoding="utf-8-sig",
)


print("\n[2] customer_purchase_type.csv 생성")
print(customer_purchase_type)


# ============================================================
# 6. RFM 세그먼트 요약
# ============================================================

rfm_segment_summary = (
    rfm
    .groupby("segment")
    .agg(
        customer_count=("customer_unique_id", "count"),
        total_monetary=("monetary", "sum"),
        avg_monetary=("monetary", "mean"),
    )
    .reset_index()
)


total_rfm_customers = (
    rfm_segment_summary["customer_count"]
    .sum()
)

total_rfm_monetary = (
    rfm_segment_summary["total_monetary"]
    .sum()
)


rfm_segment_summary["customer_ratio"] = (
    rfm_segment_summary["customer_count"]
    / total_rfm_customers
    * 100
).round(2)


rfm_segment_summary["monetary_ratio"] = (
    rfm_segment_summary["total_monetary"]
    / total_rfm_monetary
    * 100
).round(2)


rfm_segment_summary["total_monetary"] = (
    rfm_segment_summary["total_monetary"]
    .round(2)
)


rfm_segment_summary["avg_monetary"] = (
    rfm_segment_summary["avg_monetary"]
    .round(2)
)


rfm_segment_summary.to_csv(
    DASHBOARD_DIR / "rfm_segment_summary.csv",
    index=False,
    encoding="utf-8-sig",
)


print("\n[3] rfm_segment_summary.csv 생성")
print(rfm_segment_summary)


# ============================================================
# 7. 결과 요약
# ============================================================

print("\n" + "=" * 60)
print("대시보드용 데이터 생성 완료")
print("=" * 60)

print(
    f"생성 위치: {DASHBOARD_DIR}"
)

print(
    "\n생성된 파일:"
)

print(
    "1. dashboard/monthly_sales.csv"
)

print(
    "2. dashboard/customer_purchase_type.csv"
)

print(
    "3. dashboard/rfm_segment_summary.csv"
)