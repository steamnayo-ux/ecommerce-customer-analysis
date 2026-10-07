import pandas as pd
from pathlib import Path


# ============================================================
# 1. 파일 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "order_details.csv"

COUNT_OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "cohort_customer_counts.csv"
)

RETENTION_OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "cohort_retention.csv"
)


# ============================================================
# 2. 데이터 불러오기
# ============================================================

df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("Cohort 분석 시작")
print("=" * 60)

print(f"전체 데이터 행 수: {len(df):,}")


# ============================================================
# 3. 분석 대상 필터링
# ============================================================
#
# 기존 분석과 동일하게 delivered 주문만 사용한다.
#

df = df[df["order_status"] == "delivered"].copy()

print("\n" + "=" * 60)
print("분석 대상")
print("=" * 60)

print(f"Delivered 상품 상세 행: {len(df):,}")
print(f"Delivered 고유 주문: {df['order_id'].nunique():,}")
print(f"Delivered 고객 수: {df['customer_unique_id'].nunique():,}")


# ============================================================
# 4. 구매일 형식 변환
# ============================================================

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"]
)


# ============================================================
# 5. 주문 단위 데이터 생성
# ============================================================
#
# order_details.csv는 상품 단위 데이터이기 때문에
# 한 주문에 여러 상품이 있으면 여러 행이 존재한다.
#
# Cohort에서는 상품 개수가 아니라 "주문"을 기준으로
# 고객의 구매를 계산해야 한다.
#
# 따라서 고객 + 주문 기준으로 중복을 제거한다.
#

orders = (
    df[
        [
            "order_id",
            "customer_unique_id",
            "order_purchase_timestamp",
        ]
    ]
    .drop_duplicates(subset=["order_id"])
    .copy()
)


print("\n" + "=" * 60)
print("주문 단위 데이터")
print("=" * 60)

print(f"고유 주문 수: {len(orders):,}")
print(
    f"고유 고객 수: "
    f"{orders['customer_unique_id'].nunique():,}"
)


# ============================================================
# 6. Cohort Month 계산
# ============================================================
#
# 각 고객의 최초 delivered 주문이 발생한 월을
# Cohort Month로 정의한다.
#

first_purchase = (
    orders
    .groupby("customer_unique_id")[
        "order_purchase_timestamp"
    ]
    .min()
    .reset_index()
)

first_purchase["cohort_month"] = (
    first_purchase["order_purchase_timestamp"]
    .dt.to_period("M")
)


print("\n" + "=" * 60)
print("Cohort 기준")
print("=" * 60)

print(
    f"첫 구매 고객 수: "
    f"{len(first_purchase):,}"
)

print(
    f"첫 Cohort 월: "
    f"{first_purchase['cohort_month'].min()}"
)

print(
    f"마지막 Cohort 월: "
    f"{first_purchase['cohort_month'].max()}"
)


# ============================================================
# 7. 고객별 월별 구매 데이터 생성
# ============================================================
#
# 같은 고객이 같은 달에 여러 번 주문하더라도
# 해당 월에는 "활성 구매 고객 1명"으로 계산한다.
#

customer_month = (
    orders[
        [
            "customer_unique_id",
            "order_purchase_timestamp",
        ]
    ]
    .copy()
)

customer_month["activity_month"] = (
    customer_month["order_purchase_timestamp"]
    .dt.to_period("M")
)

customer_month = (
    customer_month[
        [
            "customer_unique_id",
            "activity_month",
        ]
    ]
    .drop_duplicates()
)


# ============================================================
# 8. Cohort Month 결합
# ============================================================

customer_month = customer_month.merge(
    first_purchase[
        [
            "customer_unique_id",
            "cohort_month",
        ]
    ],
    on="customer_unique_id",
    how="left",
)


# ============================================================
# 9. 월차(Month Index) 계산
# ============================================================
#
# 예:
#
# 첫 구매 2017-01
# 구매     2017-01 → 0개월
# 구매     2017-02 → 1개월
# 구매     2017-03 → 2개월
#
# 이렇게 첫 구매 이후 몇 개월이 지났는지를 계산한다.
#

customer_month["month_index"] = (
    (
        customer_month["activity_month"]
        .dt.year
        - customer_month["cohort_month"].dt.year
    )
    * 12
    + (
        customer_month["activity_month"]
        .dt.month
        - customer_month["cohort_month"].dt.month
    )
)


# ============================================================
# 10. Cohort별 월차 구매 고객 수
# ============================================================

cohort_counts = (
    customer_month
    .groupby(
        [
            "cohort_month",
            "month_index",
        ]
    )["customer_unique_id"]
    .nunique()
    .reset_index(name="customer_count")
)


# ============================================================
# 11. Cohort별 고객 수
# ============================================================
#
# month_index = 0의 고객 수가
# 해당 Cohort의 전체 고객 수가 된다.
#

cohort_sizes = (
    cohort_counts[
        cohort_counts["month_index"] == 0
    ][
        [
            "cohort_month",
            "customer_count",
        ]
    ]
    .rename(
        columns={
            "customer_count": "cohort_size"
        }
    )
)


# ============================================================
# 12. Cohort 고객 수 Pivot
# ============================================================

cohort_count_matrix = (
    cohort_counts
    .pivot(
        index="cohort_month",
        columns="month_index",
        values="customer_count",
    )
    .sort_index()
)


cohort_count_matrix.index = (
    cohort_count_matrix.index.astype(str)
)

cohort_count_matrix.columns.name = None


# ============================================================
# 13. Retention Rate 계산
# ============================================================
#
# 각 월차의 구매 고객 수를
# Cohort 전체 고객 수로 나눈다.
#
# 예:
#
# Cohort 고객 1,000명
# 1개월 후 구매 50명
#
# → Retention = 5%
#

cohort_retention_matrix = (
    cohort_count_matrix
    .div(
        cohort_count_matrix[0],
        axis=0,
    )
    * 100
)


# ============================================================
# 14. Retention Rate 반올림
# ============================================================

cohort_retention_matrix = (
    cohort_retention_matrix.round(2)
)


# ============================================================
# 15. 결과 출력
# ============================================================

print("\n" + "=" * 60)
print("Cohort별 고객 수")
print("=" * 60)

print(
    cohort_count_matrix
    .to_string()
)


print("\n" + "=" * 60)
print("Cohort Retention Rate (%)")
print("=" * 60)

print(
    cohort_retention_matrix
    .to_string()
)


# ============================================================
# 16. 초기 재구매율 확인
# ============================================================
#
# 1개월차 Retention이 전체적으로 어느 정도인지 확인한다.
#
# 데이터가 존재하는 Cohort만 대상으로 계산한다.
#

if 1 in cohort_retention_matrix.columns:

    month_1_retention = (
        cohort_retention_matrix[1]
        .dropna()
    )

    print("\n" + "=" * 60)
    print("1개월차 Retention")
    print("=" * 60)

    print(
        f"평균: "
        f"{month_1_retention.mean():.2f}%"
    )

    print(
        f"중앙값: "
        f"{month_1_retention.median():.2f}%"
    )


# ============================================================
# 17. 결과 저장
# ============================================================

cohort_count_matrix.to_csv(
    COUNT_OUTPUT_PATH,
    encoding="utf-8-sig",
)

cohort_retention_matrix.to_csv(
    RETENTION_OUTPUT_PATH,
    encoding="utf-8-sig",
)


# ============================================================
# 18. 완료
# ============================================================

print("\n" + "=" * 60)
print("Cohort 분석 완료")
print("=" * 60)

print(
    f"고객 수 결과: "
    f"{COUNT_OUTPUT_PATH}"
)

print(
    f"Retention 결과: "
    f"{RETENTION_OUTPUT_PATH}"
)