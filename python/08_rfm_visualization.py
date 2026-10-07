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

INPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_segmented.csv"
IMAGE_DIR = BASE_DIR / "images"

IMAGE_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. 데이터 불러오기
# ============================================================

rfm = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("RFM 시각화 시작")
print("=" * 60)

print(f"분석 고객 수: {len(rfm):,}")


# ============================================================
# 3. 세그먼트별 집계
# ============================================================

segment_summary = (
    rfm.groupby("segment")
    .agg(
        customer_count=("customer_unique_id", "count"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    )
    .reset_index()
)


# 전체 기준값
total_customers = segment_summary["customer_count"].sum()
total_monetary = segment_summary["total_monetary"].sum()


# 비율 계산
segment_summary["customer_ratio"] = (
    segment_summary["customer_count"]
    / total_customers
    * 100
)

segment_summary["monetary_ratio"] = (
    segment_summary["total_monetary"]
    / total_monetary
    * 100
)


# ============================================================
# 4. 세그먼트 표시 순서
# ============================================================

segment_order = [
    "장기 미구매 고객",
    "신규 고객",
    "관망 고객",
    "이탈 위험 재구매 고객",
    "고가 이탈 고객",
    "잠재 우수 고객",
    "활성 재구매 고객",
]


segment_summary["segment"] = pd.Categorical(
    segment_summary["segment"],
    categories=segment_order,
    ordered=True,
)


segment_summary = segment_summary.sort_values("segment")


# ============================================================
# 5. 그래프 ①
# 세그먼트별 고객 비율
# ============================================================

plt.figure(figsize=(10, 6))

plot_data = segment_summary.sort_values(
    "customer_ratio",
    ascending=True,
)

bars = plt.barh(
    plot_data["segment"],
    plot_data["customer_ratio"],
)


plt.title("Customer Distribution by RFM Segment")
plt.xlabel("Customer Ratio (%)")
plt.ylabel("Customer Segment")


# 막대 끝에 수치 표시
for bar, value in zip(
    bars,
    plot_data["customer_ratio"],
):
    plt.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
    )


plt.xlim(
    0,
    plot_data["customer_ratio"].max() + 5,
)

plt.tight_layout()

output_path = IMAGE_DIR / "rfm_customer_ratio.png"

plt.savefig(
    output_path,
    dpi=150,
    bbox_inches="tight",
)

plt.close()

print(f"\n고객 비율 그래프 저장: {output_path}")


# ============================================================
# 6. 그래프 ②
# 세그먼트별 구매금액 비율
# ============================================================

plt.figure(figsize=(10, 6))

plot_data = segment_summary.sort_values(
    "monetary_ratio",
    ascending=True,
)

bars = plt.barh(
    plot_data["segment"],
    plot_data["monetary_ratio"],
)


plt.title("Revenue Contribution by RFM Segment")
plt.xlabel("Revenue Contribution (%)")
plt.ylabel("Customer Segment")


for bar, value in zip(
    bars,
    plot_data["monetary_ratio"],
):
    plt.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
    )


plt.xlim(
    0,
    plot_data["monetary_ratio"].max() + 5,
)

plt.tight_layout()

output_path = IMAGE_DIR / "rfm_monetary_ratio.png"

plt.savefig(
    output_path,
    dpi=150,
    bbox_inches="tight",
)

plt.close()

print(f"구매금액 비율 그래프 저장: {output_path}")


# ============================================================
# 7. 그래프 ③
# 세그먼트별 평균 구매금액
# ============================================================

plt.figure(figsize=(10, 6))

plot_data = segment_summary.sort_values(
    "avg_monetary",
    ascending=True,
)

bars = plt.barh(
    plot_data["segment"],
    plot_data["avg_monetary"],
)


plt.title("Average Purchase Amount by RFM Segment")
plt.xlabel("Average Purchase Amount")
plt.ylabel("Customer Segment")


for bar, value in zip(
    bars,
    plot_data["avg_monetary"],
):
    plt.text(
        bar.get_width() + 5,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}",
        va="center",
    )


plt.xlim(
    0,
    plot_data["avg_monetary"].max() + 70,
)

plt.tight_layout()

output_path = IMAGE_DIR / "rfm_avg_monetary.png"

plt.savefig(
    output_path,
    dpi=150,
    bbox_inches="tight",
)

plt.close()

print(f"평균 구매금액 그래프 저장: {output_path}")


# ============================================================
# 8. 완료
# ============================================================

print("\n" + "=" * 60)
print("RFM 시각화 완료")
print("=" * 60)