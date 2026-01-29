import psycopg2
import os

try:
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="localhost", 
        port="5432"
    )
    cur = conn.cursor()
    
    print("--- Analytics Schema Verification ---")
    
    # Check Users
    cur.execute("SELECT count(*) FROM analytics.dim_users")
    user_count = cur.fetchone()[0]
    print(f"dim_users count: {user_count}")
    
    # Check Facts
    cur.execute("SELECT count(*) FROM analytics.fact_issues")
    fact_count = cur.fetchone()[0]
    print(f"fact_issues count: {fact_count}")

    if fact_count > 0:
        cur.execute("""
            SELECT f.issue_id, f.title, u.login, f.created_at
            FROM analytics.fact_issues f
            JOIN analytics.dim_users u ON f.user_id = u.user_id
            LIMIT 1
        """)
        row = cur.fetchone()
        print(f"Sample Joined Row: {row}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
