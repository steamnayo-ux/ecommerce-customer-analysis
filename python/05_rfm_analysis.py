import pandas as pd
from pathlib import Path


# ============================================================
# 1. 파일 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "order_details.csv"


# ============================================================
# 2. 데이터 불러오기
# ============================================================

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("RFM 분석 시작")
print("=" * 60)

print(f"데이터 행 수: {len(df):,}")
print(f"고유 주문 수: {df['order_id'].nunique():,}")
print(f"고유 고객 수: {df['customer_unique_id'].nunique():,}")


# ============================================================
# 3. 분석 대상 필터링
# ============================================================
# 실제 구매 행동 분석이 목적이므로
# delivered 주문만 분석 대상으로 사용한다.

df = df[df["order_status"] == "delivered"].copy()

print("\n[분석 대상]")
print(f"Delivered 상품 상세 행: {len(df):,}")
print(f"Delivered 고유 주문: {df['order_id'].nunique():,}")
print(f"Delivered 고객 수: {df['customer_unique_id'].nunique():,}")


# ============================================================
# 4. 날짜 데이터 변환
# ============================================================

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"]
)


# ============================================================
# 5. 기준일(Snapshot Date) 설정
# ============================================================
# 실제 분석 데이터에서 가장 마지막 구매일을 기준으로 한다.
#
# Recency:
# 기준일 - 고객의 마지막 구매일
#
# 기준일 당일 구매 고객은 Recency = 0이 된다.

snapshot_date = df["order_purchase_timestamp"].max()

print("\n[기준일]")
print(f"Snapshot Date: {snapshot_date}")


# ============================================================
# 6. 고객별 RFM 계산
# ============================================================

rfm = (
    df.groupby("customer_unique_id")
    .agg(
        last_purchase_date=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("sales_amount", "sum"),
    )
    .reset_index()
)


# ============================================================
# 7. Recency 계산
# ============================================================

rfm["recency"] = (
    snapshot_date - rfm["last_purchase_date"]
).dt.days


# ============================================================
# 8. 컬럼 순서 정리
# ============================================================

rfm = rfm[
    [
        "customer_unique_id",
        "last_purchase_date",
        "recency",
        "frequency",
        "monetary",
    ]
]


# ============================================================
# 9. 기본 결과 확인
# ============================================================

print("\n" + "=" * 60)
print("RFM 계산 결과")
print("=" * 60)

print(f"분석 고객 수: {len(rfm):,}")

print("\n[상위 10명]")
print(
    rfm
    .sort_values("monetary", ascending=False)
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 10. RFM 통계 확인
# ============================================================

print("\n" + "=" * 60)
print("RFM 통계")
print("=" * 60)

print(
    rfm[
        ["recency", "frequency", "monetary"]
    ].describe()
)


# ============================================================
# 11. Frequency 분포 확인
# ============================================================

print("\n" + "=" * 60)
print("Frequency 분포")
print("=" * 60)

frequency_distribution = (
    rfm["frequency"]
    .value_counts()
    .sort_index()
)

print(frequency_distribution.to_string())


# ============================================================
# 12. 주요 비율 확인
# ============================================================

one_time_customers = (rfm["frequency"] == 1).sum()
repeat_customers = (rfm["frequency"] >= 2).sum()

one_time_ratio = one_time_customers / len(rfm) * 100
repeat_ratio = repeat_customers / len(rfm) * 100

print("\n" + "=" * 60)
print("고객 구매 유형")
print("=" * 60)

print(f"1회 구매 고객: {one_time_customers:,}명 ({one_time_ratio:.1f}%)")
print(f"재구매 고객:   {repeat_customers:,}명 ({repeat_ratio:.1f}%)")


# ============================================================
# 13. Monetary 분포 확인
# ============================================================

print("\n" + "=" * 60)
print("Monetary 주요 분위수")
print("=" * 60)

monetary_quantiles = rfm["monetary"].quantile(
    [0.25, 0.5, 0.75, 0.90, 0.95, 0.99]
)

print(monetary_quantiles.to_string())


# ============================================================
# 14. Recency 주요 분위수
# ============================================================

print("\n" + "=" * 60)
print("Recency 주요 분위수")
print("=" * 60)

recency_quantiles = rfm["recency"].quantile(
    [0.25, 0.5, 0.75, 0.90, 0.95, 0.99]
)

print(recency_quantiles.to_string())


# ============================================================
# 15. 결과 저장
# ============================================================
# 아직 세그먼트나 점수는 만들지 않는다.
# 실제 RFM 분포를 확인한 뒤 다음 단계에서 추가한다.

OUTPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_base.csv"

rfm.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)

print("\n" + "=" * 60)
print("RFM 분석 완료")
print("=" * 60)

print(f"결과 파일: {OUTPUT_PATH}")