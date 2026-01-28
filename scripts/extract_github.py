import os
import argparse
import requests
import boto3
import json
import time
from datetime import datetime

# Configuration
GITHUB_API_BASE = "https://api.github.com"
REPO = "apache/airflow"  # Target repo
BUCKET_NAME = "github-raw"

def get_s3_client():
    """Create a boto3 client for MinIO/S3."""
    return boto3.client(
        's3',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:9000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

def fetch_github_issues(start_date, end_date, limit=None):
    """Fetch issues from GitHub API with pagination."""
    url = f"{GITHUB_API_BASE}/repos/{REPO}/issues"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    else:
        print("WARNING: No GITHUB_TOKEN found. Rate limits will be strict (60/hr).")
    
    params = {
        "state": "all",
        "since": start_date,  # ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
        "per_page": 100,
        "page": 1,
        "sort": "created",
        "direction": "asc"
    }

    all_issues = []
    
    while True:
        print(f"Fetching page {params['page']}...")
        try:
            response = requests.get(url, headers=headers, params=params)
            
            # Rate Limit Handling
            if response.status_code == 403 and "rate limit" in response.text.lower():
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                sleep_seconds = max(reset_time - time.time(), 0) + 1
                print(f"Rate limit hit. Sleeping for {sleep_seconds} seconds.")
                time.sleep(sleep_seconds)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
                
            # Filter by date if needed (API 'since' only handles updates)
            # For this MVP, we accept 'since' behavior as sufficient for incremental loads
            all_issues.extend(data)

            if limit and len(all_issues) >= limit:
                all_issues = all_issues[:limit]
                break
            
            if len(data) < 100:
                break
                
            params["page"] += 1
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            raise

    return all_issues

def upload_to_s3(data, date_str):
    """Upload raw JSON data to S3/MinIO partitioned by date."""
    if not data:
        print("No data to upload.")
        return

    s3 = get_s3_client()
    
    # Path: entity=issues/dt=YYYY-MM-DD/data.json
    file_key = f"entity=issues/dt={date_str}/raw_data.json"
    
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        print(f"Successfully uploaded {len(data)} records to s3://{BUCKET_NAME}/{file_key}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        # Check if bucket exists, if not try to create (for local dev resilience)
        try:
            s3.create_bucket(Bucket=BUCKET_NAME)
            print(f"Bucket {BUCKET_NAME} created. Retrying upload...")
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            print(f"Successfully uploaded on retry.")
        except Exception as bucket_e:
            print(f"Critical error uploading to S3: {bucket_e}")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Date to fetch data for (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Limit number of issues to fetch for testing")
    args = parser.parse_args()
    
    # For a daily run, we fetch data updated ON that day.
    # GitHub 'since' is inclusive. 
    # To be precise for a daily batch, we might fetch everything since 'date' 
    # and filter, but for simplicity we rely on 'since' for now.
    
    target_date = args.date
    print(f"Starting extraction for {target_date}...")
    
    # Convert YYYY-MM-DD to ISO 8601
    start_ts = f"{target_date}T00:00:00Z"
    
    issues = fetch_github_issues(start_ts, None, limit=args.limit)
    upload_to_s3(issues, target_date)
