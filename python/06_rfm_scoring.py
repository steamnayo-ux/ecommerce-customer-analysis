import pandas as pd
from pathlib import Path


# ============================================================
# 1. 파일 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_base.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_scored.csv"


# ============================================================
# 2. RFM 데이터 불러오기
# ============================================================

rfm = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("RFM 점수화 시작")
print("=" * 60)

print(f"분석 고객 수: {len(rfm):,}")


# ============================================================
# 3. Recency 점수
# ============================================================
# Recency는 값이 작을수록 최근 구매를 의미한다.
#
# 따라서:
# 최근 구매 고객 → 높은 점수
# 오래된 구매 고객 → 낮은 점수
#
# qcut 결과를 역순으로 5~1점으로 변환한다.

rfm["r_score"] = pd.qcut(
    rfm["recency"],
    q=5,
    labels=[5, 4, 3, 2, 1],
    duplicates="drop",
)


# ============================================================
# 4. Monetary 점수
# ============================================================
# 구매 금액이 높을수록 높은 점수.
#
# 분위수를 기준으로 1~5점 부여.

rfm["m_score"] = pd.qcut(
    rfm["monetary"],
    q=5,
    labels=[1, 2, 3, 4, 5],
    duplicates="drop",
)


# ============================================================
# 5. Frequency 점수
# ============================================================
# Frequency는 현재 데이터에서 1회 구매 고객이 97%이므로
# 일반적인 5분위수 방식을 사용하지 않는다.
#
# 실제 구매 횟수를 기준으로 점수를 부여한다.

def frequency_score(frequency):
    if frequency == 1:
        return 1
    elif frequency == 2:
        return 2
    elif frequency == 3:
        return 3
    elif frequency == 4:
        return 4
    else:
        return 5


rfm["f_score"] = rfm["frequency"].apply(frequency_score)


# ============================================================
# 6. 숫자형으로 변환
# ============================================================

rfm["r_score"] = rfm["r_score"].astype(int)
rfm["f_score"] = rfm["f_score"].astype(int)
rfm["m_score"] = rfm["m_score"].astype(int)


# ============================================================
# 7. RFM Score 생성
# ============================================================
# 예:
# R=5, F=2, M=4
# → 524

rfm["rfm_score"] = (
    rfm["r_score"].astype(str)
    + rfm["f_score"].astype(str)
    + rfm["m_score"].astype(str)
)


# ============================================================
# 8. RFM Total Score 생성
# ============================================================
# 세 지표의 합계.
#
# 범위:
# 최소 3점
# 최대 15점

rfm["rfm_total_score"] = (
    rfm["r_score"]
    + rfm["f_score"]
    + rfm["m_score"]
)


# ============================================================
# 9. 결과 컬럼 정리
# ============================================================

rfm = rfm[
    [
        "customer_unique_id",
        "last_purchase_date",
        "recency",
        "frequency",
        "monetary",
        "r_score",
        "f_score",
        "m_score",
        "rfm_score",
        "rfm_total_score",
    ]
]


# ============================================================
# 10. 점수 분포 확인
# ============================================================

print("\n" + "=" * 60)
print("R 점수 분포")
print("=" * 60)

print(
    rfm["r_score"]
    .value_counts()
    .sort_index()
    .to_string()
)


print("\n" + "=" * 60)
print("F 점수 분포")
print("=" * 60)

print(
    rfm["f_score"]
    .value_counts()
    .sort_index()
    .to_string()
)


print("\n" + "=" * 60)
print("M 점수 분포")
print("=" * 60)

print(
    rfm["m_score"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# 11. RFM Total Score 분포
# ============================================================

print("\n" + "=" * 60)
print("RFM Total Score 분포")
print("=" * 60)

print(
    rfm["rfm_total_score"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# 12. 주요 RFM Score 확인
# ============================================================

print("\n" + "=" * 60)
print("RFM Score 상위 빈도")
print("=" * 60)

print(
    rfm["rfm_score"]
    .value_counts()
    .head(20)
    .to_string()
)


# ============================================================
# 13. 결과 저장
# ============================================================

rfm.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)


print("\n" + "=" * 60)
print("RFM 점수화 완료")
print("=" * 60)

print(f"결과 파일: {OUTPUT_PATH}")