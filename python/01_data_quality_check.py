from pathlib import Path
import pandas as pd

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# CSV 파일 목록
csv_files = sorted(RAW_DIR.glob("*.csv"))

print(f"총 {len(csv_files)}개 CSV 파일 발견\n")

for file in csv_files:
    print("=" * 70)
    print(f"파일: {file.name}")

    df = pd.read_csv(file)

    print(f"행 수: {len(df):,}")
    print(f"열 수: {len(df.columns)}")

    print("\n컬럼:")
    print(list(df.columns))

    print("\n데이터 타입:")
    print(df.dtypes)

    print("\n결측치:")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]

    if len(nulls) == 0:
        print("결측치 없음")
    else:
        print(nulls)

    print(f"\n중복 행: {df.duplicated().sum():,}")

    print("\n샘플:")
    print(df.head(3))