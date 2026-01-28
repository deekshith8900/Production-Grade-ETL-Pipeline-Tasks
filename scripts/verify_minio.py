import boto3
import os

try:
    s3 = boto3.client('s3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        region_name='us-east-1'
    )

    # List objects in github-raw
    response = s3.list_objects_v2(Bucket='github-raw')
    if 'Contents' in response:
        print(f"SUCCESS: Found {len(response['Contents'])} files.")
        for obj in response['Contents']:
            print(f" - {obj['Key']}")
    else:
        print("Bucket is empty (DAG might still be running or failed).")
except Exception as e:
    print(f"Error: {e}")
