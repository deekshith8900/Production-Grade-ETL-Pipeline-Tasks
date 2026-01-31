# Cloud Deployment Guide (AWS EC2)

This guide walks you through deploying the ETL pipeline to a live AWS EC2 instance.

## Prerequisites
- An AWS Account.
- Your GitHub Token.

## Step 1: Launch EC2 Instance
1. Log into AWS Console -> **EC2** -> **Launch Instance**.
2. **Name**: `Airflow-ETL-Server`
3. **OS Image**: `Ubuntu Server 22.04 LTS` (Free Tier eligible).
4. **Instance Type**: `t2.medium` (2 vCPU, 4GB RAM).
   > ⚠️ **Warning**: Do NOT use `t2.micro` (1GB RAM). Airflow will crash. `t2.medium` costs ~$0.046/hour.
5. **Key Pair**: Create a new key pair (e.g., `airflow-key`) and download the `.pem` file.
6. **Network Settings** -> **Create security group**:
   - Allow SSH traffic from `My IP`.
   - Allow Custom TCP `8080` (Airflow) from `Anywhere` (`0.0 .0.0/0`).
   - Allow Custom TCP `9001` (MinIO UI) from `Anywhere` (`0.0.0.0/0`).
7. **Storage**: Set to 20 GB gp3.
8. Click **Launch Instance**.

## Step 2: Connect to Instance
Open your terminal (Mac/Linux) or Git Bash (Windows):
```bash
chmod 400 path/to/airflow-key.pem
ssh -i "path/to/airflow-key.pem" ubuntu@<PUBLIC_IP_ADDRESS>
```
*(Replace `<PUBLIC_IP_ADDRESS>` with the IP from AWS Console)*

## Step 3: Run Setup Script
Once connected to the server, copy and paste this command block to run the automated setup:

```bash
curl -fsSL https://raw.githubusercontent.com/deekshith8900/Production-Grade-ETL-Pipeline-Tasks/main/deployment/init-server.sh -o init-server.sh
chmod +x init-server.sh
./init-server.sh
```

Follow the prompts:
- It will ask for your `GITHUB_TOKEN`. Paste it and hit Enter.

## Step 4: Verify Deployment
1. Wait a few minutes for Docker to build/pull images.
2. Open your browser to: `http://<PUBLIC_IP_ADDRESS>:8080`
3. Login with `admin` / `admin`.

## Step 5: Cost Management
**Important**: When you are not demonstrating the project (e.g., sleeping), **Stop** the instance in AWS Console to stop being charged for compute.
- **Stop**: Pauses billing for compute (you only pay small storage fee).
- **Terminate**: Deletes everything (stops all billing).
