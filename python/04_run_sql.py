from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"

con = duckdb.connect()

# 주문 상세 데이터
con.execute(f"""
    CREATE OR REPLACE VIEW order_details AS
    SELECT *
    FROM read_csv_auto('{PROCESSED_DIR / "order_details.csv"}')
""")

# 고객-주문 데이터
con.execute(f"""
    CREATE OR REPLACE VIEW orders_customers AS
    SELECT *
    FROM read_csv_auto('{PROCESSED_DIR / "orders_customers.csv"}')
""")

# sql 폴더의 SQL 파일을 순서대로 실행
sql_files = sorted(SQL_DIR.glob("*.sql"))

for sql_file in sql_files:

    print("\n" + "#" * 70)
    print(f"SQL FILE: {sql_file.name}")
    print("#" * 70)

    sql = sql_file.read_text(encoding="utf-8")

    queries = [
        query.strip()
        for query in sql.split(";")
        if query.strip()
    ]

    for index, query in enumerate(queries, start=1):

        print("\n" + "=" * 70)
        print(f"KPI {index}")
        print("=" * 70)

        result = con.execute(query)
        print(result.fetchall())
        print()

con.close()