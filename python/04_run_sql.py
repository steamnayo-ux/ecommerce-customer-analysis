from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"


con = duckdb.connect()

con.execute(f"""
    CREATE OR REPLACE VIEW order_details AS
    SELECT *
    FROM read_csv_auto('{PROCESSED_DIR / "order_details.csv"}')
""")


sql_file = SQL_DIR / "01_sales_kpi.sql"
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