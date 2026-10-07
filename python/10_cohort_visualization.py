import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 한글 폰트 설정
# ============================================================

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 1. 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "cohort_retention.csv"
)

IMAGE_DIR = BASE_DIR / "images"

IMAGE_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. Cohort Retention 데이터 불러오기
# ============================================================

retention = pd.read_csv(
    INPUT_PATH,
    index_col=0,
)

print("=" * 60)
print("Cohort Retention 시각화 시작")
print("=" * 60)

print(f"전체 Cohort 수: {len(retention):,}")


# ============================================================
# 2-1. 표본이 적은 초기 Cohort 제외
# ============================================================
#
# 2016-09, 2016-10, 2016-12 Cohort는 서비스 초기 데이터로
# 고객 수가 1~262명 수준이다.
#
# 특히 2016-09, 2016-12 Cohort는 고객이 1명뿐이어서
# 그 고객이 다시 구매하면 유지율이 100%로 표시된다.
#
# 따라서 2017-01 이후 Cohort만 시각화한다.
# (분석 데이터 cohort_retention.csv 자체는 수정하지 않는다.)
#

MIN_COHORT_MONTH = "2017-01"

excluded = retention.index[retention.index < MIN_COHORT_MONTH]

retention = retention.loc[
    retention.index >= MIN_COHORT_MONTH
].copy()

print(f"제외한 Cohort: {', '.join(excluded)}")
print(f"시각화 Cohort 수: {len(retention):,}")


# ============================================================
# 3. 컬럼 이름 정리
# ============================================================
#
# CSV에서 읽은 month_index가 문자열일 수 있으므로
# 숫자형으로 변환한다.
#

retention.columns = [
    int(column)
    for column in retention.columns
]


# ============================================================
# 3-1. 빠진 월차 컬럼 채우기
# ============================================================
#
# cohort_retention.csv는 "재구매한 고객이 한 명이라도 있는
# 월차"만 컬럼으로 가진다. 그래서 어느 월차(예: 18개월)에
# 재구매 고객이 아무도 없으면 컬럼 자체가 사라지고,
# 히트맵 X축이 17 -> 19처럼 건너뛰게 된다.
#
# 데이터의 마지막 달은 가장 늦은 Cohort 월과 같다고 보고,
# 가장 이른 Cohort(2017-01)가 관측할 수 있는 마지막 월차까지
# 0개월부터 모든 컬럼을 만들어 준다.
# (제외한 2016년 Cohort에만 있던 월차 컬럼은 함께 사라진다.)
#

cohort_periods = pd.PeriodIndex(
    retention.index,
    freq="M",
)

last_month = cohort_periods.max()

max_month_index = (last_month - cohort_periods.min()).n

retention = retention.reindex(
    columns=range(0, max_month_index + 1)
)

print(f"데이터 마지막 월: {last_month}")
print(f"최대 월차: {max_month_index}")


# ============================================================
# 3-2. "재구매 0%"와 "아직 관측 불가" 구분하기
# ============================================================
#
# 빈칸(NaN)에는 두 가지 의미가 섞여 있다.
#
#   (1) 관측 가능한 기간인데 재구매 고객이 0명  -> 0%
#   (2) 데이터 마지막 달 이후라서 아직 알 수 없음 -> 빈칸 유지
#
# Cohort마다 "마지막 달 - Cohort 월" 까지가 관측 가능한 월차다.
#
# 예: 마지막 달이 2018-08일 때
#     2018-06 Cohort -> 0, 1, 2개월까지 관측 가능
#     2018-08 Cohort -> 0개월만 관측 가능
#

observable_months = np.array(
    [
        (last_month - period).n
        for period in cohort_periods
    ]
)

month_indexes = np.array(retention.columns)

observable = (
    month_indexes[np.newaxis, :]
    <= observable_months[:, np.newaxis]
)

retention = retention.where(~observable, retention.fillna(0))


# ============================================================
# 3-3. 0개월차 제외
# ============================================================
#
# 0개월차는 모든 Cohort가 100%이다.
# 이 값이 색상 범위의 최댓값을 차지하면
# 실제로 보고 싶은 1개월차 이후(0.1~0.7%대)가
# 모두 같은 색으로 보이게 된다.
#
# 따라서 히트맵은 1개월차부터 그린다.
#

retention = retention.drop(columns=[0])

# 0개월차만 관측 가능한 마지막 Cohort(2018-08)는
# 1개월차 이후 값이 하나도 없으므로 빈 행으로 남지 않게 뺀다.
retention = retention.dropna(how="all")

print(f"시각화 Cohort 수(최종): {len(retention):,}")

print(f"히트맵 월차 범위: {retention.columns.min()} ~ {retention.columns.max()}")


# ============================================================
# 4. Heatmap 그리기
# ============================================================
#
# 색상 최댓값은 실제 데이터 최댓값을 0.1 단위로 올림한다.
#

vmax = np.ceil(np.nanmax(retention.values) * 10) / 10

plt.figure(
    figsize=(16, 9)
)

cmap = plt.get_cmap("YlGnBu").copy()
cmap.set_bad("white")

image = plt.imshow(
    np.ma.masked_invalid(retention.values),
    aspect="auto",
    interpolation="nearest",
    cmap=cmap,
    vmin=0,
    vmax=vmax,
)


# ============================================================
# 5. 축 설정
# ============================================================

plt.title(
    "Cohort Retention Rate (%) - 1+ Months After First Purchase",
    fontsize=16,
    pad=15,
)

plt.xlabel(
    "Months Since First Purchase",
    fontsize=11,
)

plt.ylabel(
    "Cohort Month",
    fontsize=11,
)


# X축
plt.xticks(
    range(len(retention.columns)),
    retention.columns,
)


# Y축
plt.yticks(
    range(len(retention.index)),
    retention.index,
)


# ============================================================
# 6. 색상 범례
# ============================================================

colorbar = plt.colorbar(image)

colorbar.set_label(
    "Retention Rate (%)",
    rotation=270,
    labelpad=15,
)


# ============================================================
# 7. 값 표시
# ============================================================
#
# 각 셀에 Retention 값을 표시한다.
#
# NaN(아직 관측 불가)은 표시하지 않는다.
# 배경이 진한 셀은 흰색 글씨, 연한 셀은 검은색 글씨로 표시한다.
#

for row in range(len(retention.index)):

    for column in range(len(retention.columns)):

        value = retention.iloc[
            row,
            column,
        ]

        if pd.notna(value):

            text_color = (
                "white"
                if value > vmax * 0.6
                else "black"
            )

            plt.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color=text_color,
            )


# ============================================================
# 8. 레이아웃
# ============================================================

plt.tight_layout()


# ============================================================
# 9. 이미지 저장
# ============================================================

output_path = (
    IMAGE_DIR
    / "cohort_retention_heatmap.png"
)

plt.savefig(
    output_path,
    dpi=150,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# 10. 완료
# ============================================================

print("\n" + "=" * 60)
print("Cohort Retention 시각화 완료")
print("=" * 60)

print(
    f"결과 이미지: {output_path}"
)