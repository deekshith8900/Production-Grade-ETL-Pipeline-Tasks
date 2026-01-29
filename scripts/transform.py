import argparse
import psycopg2
import os

# Config
DB_NAME = "airflow"
DB_USER = "airflow"
DB_PASS = "airflow"
DB_HOST = "postgres"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )

def setup_schema():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("Setting up 'analytics' schema...")
    cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    
    # Dimension: Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics.dim_users (
            user_id BIGINT PRIMARY KEY,
            login TEXT NOT NULL,
            type TEXT,
            url TEXT,
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    # Fact: Issues
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics.fact_issues (
            issue_id BIGINT PRIMARY KEY,
            user_id BIGINT REFERENCES analytics.dim_users(user_id),
            state TEXT,
            title TEXT,
            comments_count INT,
            created_at TIMESTAMP,
            execution_date DATE,
            loaded_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def transform_data(date_str):
    conn = get_db_connection()
    cur = conn.cursor()
    
    print(f"Transforming data for {date_str}...")
    
    # 1. Populate dim_users from raw data
    # extracting 'user' object from the jsonb
    print("Updating Dimensions...")
    cur.execute("""
        INSERT INTO analytics.dim_users (user_id, login, type, url)
        SELECT DISTINCT
            (raw_data->'user'->>'id')::bigint,
            raw_data->'user'->>'login',
            raw_data->'user'->>'type',
            raw_data->'user'->>'url'
        FROM raw.github_issues
        WHERE execution_date = %s
        ON CONFLICT (user_id) DO UPDATE 
        SET login = EXCLUDED.login, updated_at = NOW();
    """, (date_str,))
    
    # 2. Populate fact_issues
    # Idempotency: delete first
    print("Updating Facts...")
    cur.execute("DELETE FROM analytics.fact_issues WHERE execution_date = %s", (date_str,))
    
    cur.execute("""
        INSERT INTO analytics.fact_issues 
        (issue_id, user_id, state, title, comments_count, created_at, execution_date)
        SELECT 
            (raw_data->>'id')::bigint,
            (raw_data->'user'->>'id')::bigint,
            raw_data->>'state',
            raw_data->>'title',
            (raw_data->>'comments')::int,
            (raw_data->>'created_at')::timestamp,
            %s
        FROM raw.github_issues
        WHERE execution_date = %s;
    """, (date_str, date_str))
    
    conn.commit()
    print("Transformation complete.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    
    setup_schema()
    transform_data(args.date)
