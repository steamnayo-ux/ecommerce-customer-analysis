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
# 그 고객이 다시 구매하면 유지율이 100%로 표시되고,
# 히트맵 전체의 색상 범위를 왜곡한다.
#
# 따라서 2017-01 이후 Cohort만 시각화한다.
# (분석 데이터 cohort_retention.csv 자체는 수정하지 않는다.)
#

MIN_COHORT_MONTH = "2017-01"

excluded = retention.index[retention.index < MIN_COHORT_MONTH]

retention = retention.loc[
    retention.index >= MIN_COHORT_MONTH
]

print(f"제외한 Cohort: {', '.join(excluded)}")
print(f"시각화 Cohort 수: {len(retention):,}")
print(f"최대 관찰 개월: {retention.shape[1] - 1}")


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
# 4. Heatmap 그리기
# ============================================================

plt.figure(
    figsize=(16, 10)
)

image = plt.imshow(
    retention,
    aspect="auto",
    interpolation="nearest",
)


# ============================================================
# 5. 축 설정
# ============================================================

plt.title(
    "Cohort Retention Rate (%)",
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
# NaN은 표시하지 않는다.
#

for row in range(len(retention.index)):

    for column in range(len(retention.columns)):

        value = retention.iloc[
            row,
            column,
        ]

        if pd.notna(value):

            plt.text(
                column,
                row,
                f"{value:.1f}",
                ha="center",
                va="center",
                fontsize=7,
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