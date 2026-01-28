import argparse
import boto3
import psycopg2
import json
import os
from io import BytesIO

# Config
BUCKET_NAME = "github-raw"
DB_NAME = "airflow"
DB_USER = "airflow"
DB_PASS = "airflow"
DB_HOST = "postgres"  # Running inside Docker network

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://minio:9000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )

def setup_table():
    """Create the raw table if it doesn't exist."""
    print("Ensuring 'raw' schema and 'github_issues' table exist...")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.github_issues (
            id SERIAL PRIMARY KEY,
            execution_date DATE NOT NULL,
            raw_data JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def load_data(date_str):
    s3 = get_s3_client()
    key = f"entity=issues/dt={date_str}/raw_data.json"
    
    print(f"Reading from s3://{BUCKET_NAME}/{key} ...")
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        data = json.load(obj['Body'])
    except s3.exceptions.NoSuchKey:
        print(f"No data found for {date_str}. Skipping load.")
        return

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Idempotency: Delete existing data for this date
    print(f"Clearing old data for {date_str}...")
    cur.execute("DELETE FROM raw.github_issues WHERE execution_date = %s", (date_str,))
    
    # Bulk Insert
    print(f"Inserting {len(data)} records...")
    
    # For JSONB, we usually insert row by row or use execute_values. 
    # For simplicity/readability, we loop.
    for issue in data:
        cur.execute(
            "INSERT INTO raw.github_issues (execution_date, raw_data) VALUES (%s, %s)",
            (date_str, json.dumps(issue))
        )
    
    conn.commit()
    print("Load complete.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    
    setup_table()
    load_data(args.date)
