import psycopg2
import os

try:
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="localhost", # When running from host
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM raw.github_issues")
    count = cur.fetchone()[0]
    print(f"SUCCESS: Postgres table 'raw.github_issues' has {count} rows.")
    
    cur.execute("SELECT execution_date, created_at FROM raw.github_issues LIMIT 1")
    row = cur.fetchone()
    print(f"Sample Row: {row}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
