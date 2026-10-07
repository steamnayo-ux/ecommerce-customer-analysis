import pandas as pd
from pathlib import Path


# ============================================================
# 1. 파일 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_scored.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_segmented.csv"


# ============================================================
# 2. RFM 점수 데이터 불러오기
# ============================================================

rfm = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("RFM 고객 세그먼트 분석 시작")
print("=" * 60)

print(f"분석 고객 수: {len(rfm):,}")


# ============================================================
# 3. 고객 세그먼트 정의
# ============================================================

def assign_segment(row):

    r = row["r_score"]
    f = row["f_score"]
    m = row["m_score"]
    frequency = row["frequency"]

    # ----------------------------------------
    # 1. 핵심 고객
    # 최근 구매 + 반복 구매 + 높은 구매금액
    # ----------------------------------------
    if r >= 4 and f >= 3 and m >= 4:
        return "핵심 고객"

    # ----------------------------------------
    # 2. 충성 고객
    # 반복 구매 + 높은 구매금액
    # ----------------------------------------
    if f >= 2 and m >= 4:
        return "충성 고객"

    # ----------------------------------------
    # 3. 잠재 우수 고객
    # 최근 구매 + 높은 구매금액
    # 아직 반복 구매가 많지 않음
    # ----------------------------------------
    if r >= 4 and m >= 4:
        return "잠재 우수 고객"

    # ----------------------------------------
    # 4. 최근 1회 구매 고객
    # 1회 구매 + 최근 구매
    # ----------------------------------------
    if frequency == 1 and r >= 4:
        return "최근 1회 구매 고객"

    # ----------------------------------------
    # 5. 장기 미구매 고객
    # 1회 구매 + 오래전 구매
    # ----------------------------------------
    if frequency == 1 and r <= 2:
        return "장기 미구매 고객"

    # ----------------------------------------
    # 6. 일반 고객
    # ----------------------------------------
    return "일반 고객"


rfm["segment"] = rfm.apply(assign_segment, axis=1)


# ============================================================
# 4. 전체 구매금액
# ============================================================

total_monetary = rfm["monetary"].sum()


# ============================================================
# 5. 세그먼트별 구매 행동 분석
# ============================================================

segment_summary = (
    rfm.groupby("segment")
    .agg(
        customer_count=("customer_unique_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    )
    .reset_index()
)


# 고객 비율
segment_summary["customer_ratio"] = (
    segment_summary["customer_count"]
    / len(rfm)
    * 100
)


# 구매금액 비율
segment_summary["monetary_ratio"] = (
    segment_summary["total_monetary"]
    / total_monetary
    * 100
)


# 보기 좋은 순서로 컬럼 정리
segment_summary = segment_summary[
    [
        "segment",
        "customer_count",
        "customer_ratio",
        "avg_recency",
        "avg_frequency",
        "avg_monetary",
        "total_monetary",
        "monetary_ratio",
    ]
]


# ============================================================
# 6. 세그먼트별 고객 수
# ============================================================

print("\n" + "=" * 60)
print("세그먼트별 고객 수")
print("=" * 60)

print(
    segment_summary
    .sort_values("customer_count", ascending=False)
    .to_string(index=False)
)


# ============================================================
# 7. 세그먼트별 구매 행동
# ============================================================

print("\n" + "=" * 60)
print("세그먼트별 구매 행동")
print("=" * 60)

print(
    segment_summary
    .sort_values("total_monetary", ascending=False)
    .to_string(index=False)
)


# ============================================================
# 8. 세그먼트별 평균 RFM 점수
# ============================================================

segment_scores = (
    rfm.groupby("segment")
    .agg(
        avg_r_score=("r_score", "mean"),
        avg_f_score=("f_score", "mean"),
        avg_m_score=("m_score", "mean"),
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("세그먼트별 평균 RFM 점수")
print("=" * 60)

print(
    segment_scores
    .sort_values(
        ["avg_r_score", "avg_m_score"],
        ascending=False,
    )
    .to_string(index=False)
)


# ============================================================
# 9. 결과 저장
# ============================================================

rfm.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)


print("\n" + "=" * 60)
print("RFM 고객 세그먼트 분석 완료")
print("=" * 60)

print(f"결과 파일: {OUTPUT_PATH}")