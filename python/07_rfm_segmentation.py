import numpy as np
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
#
# 이 데이터는 1회 구매 고객이 약 97%이므로
# 먼저 "재구매 여부(Frequency)"로 고객을 나눈 뒤,
# 그 안에서 Recency, Monetary로 세분화한다.
#
# 모든 고객이 정확히 하나의 세그먼트에만 속하도록
# 조건이 서로 겹치지 않게 설계했다.
#
# [Recency 점수 기준]
#   r_score 5 : 0 ~ 91일      (매우 최근)
#   r_score 4 : 92 ~ 176일
#   r_score 3 : 177 ~ 267일
#   r_score 2 : 268 ~ 381일
#   r_score 1 : 382일 이상
#
# [재구매 고객: frequency >= 2]
#   활성 재구매 고객      : 최근 약 9개월 이내 구매 (r >= 3)
#   이탈 위험 재구매 고객 : 마지막 구매가 오래됨   (r <= 2)
#
# [1회 구매 고객: frequency == 1]
#   잠재 우수 고객   : 최근 구매 + 높은 구매금액 (r >= 4, m >= 4)
#   신규 고객        : 최근 구매 + 낮은/중간 구매금액 (r >= 4, m <= 3)
#   관망 고객        : 구매 후 6~9개월 경과, 이탈 징후 (r == 3)
#   고가 이탈 고객   : 오래전 구매 + 높은 구매금액 (r <= 2, m >= 4)
#                      -> 재방문 유도(Win-back) 우선 대상
#   장기 미구매 고객 : 오래전 구매 + 낮은/중간 구매금액 (r <= 2, m <= 3)
#

r = rfm["r_score"]
m = rfm["m_score"]
frequency = rfm["frequency"]

conditions = [
    (frequency >= 2) & (r >= 3),
    (frequency >= 2) & (r <= 2),
    (frequency == 1) & (r >= 4) & (m >= 4),
    (frequency == 1) & (r >= 4) & (m <= 3),
    (frequency == 1) & (r == 3),
    (frequency == 1) & (r <= 2) & (m >= 4),
    (frequency == 1) & (r <= 2) & (m <= 3),
]

segment_names = [
    "활성 재구매 고객",
    "이탈 위험 재구매 고객",
    "잠재 우수 고객",
    "신규 고객",
    "관망 고객",
    "고가 이탈 고객",
    "장기 미구매 고객",
]

rfm["segment"] = np.select(
    conditions,
    segment_names,
    default="미분류",
)


# 모든 고객이 세그먼트에 배정되었는지 확인
unassigned = (rfm["segment"] == "미분류").sum()

print(f"\n세그먼트 미배정 고객 수: {unassigned:,}")

if unassigned > 0:
    raise ValueError(
        "세그먼트에 배정되지 않은 고객이 있습니다. "
        "조건을 다시 확인하세요."
    )


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