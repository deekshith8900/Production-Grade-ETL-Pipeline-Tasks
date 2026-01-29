# Production-Grade ETL Pipeline

A robust, containerized ETL pipeline that ingests data from the GitHub API, stores raw data in Object Storage (MinIO), and transforms it into a Dimensional Model in Postgres for analytics. Orchestrated by Apache Airflow.

![Architecture Diagram](https://mermaid.ink/img/pako:eNqNksFqwzAMhl_F6NRC-wI5DDaM0XYY7WWH4iS2G9vYyHZSStl7zzlttsF220GybP_3S0_QGiuRgr7Zq8Jq9OC84WdFj4_Pj4_39y_w8gS2g95a6ODsY9e11kF_clZ5-OLsE9Q1dPAZ_tMO7i-vL5dK1dDA0Vn4o2_eWqjhzVn4u29eK1XD2ln4q29eK9VAf2YV1fC7o0o1lM4qPqlSTW-qVEO1UqWaalap5u-qVEO9UqWaa1ap5u9VqumN_xqa9l9D0_5r_jT0_2-o_z-hBvr_F6r5_4RqqP8_oab_E2r-ruafhurnK8xLdC0s0B9iWqA_xLRAf4hpgf4Q0wL9IaYF-kNM8_9DTAu0n5gWaD8xLdB-Ylqg_cS0QPuJaYH2E9M8_xPT_P4npvnzT0zz65-Y5s8_Mc2ff2KaP__ENH_-Q0zz65-Y5tc_Mc2vf2KaP__ENH_-ianVq4Iq1CuCapCrgmqQ84JqkKuCStQrgkrUK4JqkKuCatQrgmrUK4Iq0SuCKtErgmrQq4Jq0KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCalCvgmpQr4JqUK-Calculated)

## 🚀 Tech Stack

- **Orchestration**: Apache Airflow
- **Language**: Python 3.9+
- **Data Lake (Raw)**: MinIO (S3 Compatible)
- **Data Warehouse**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git

## 🏗 Architecture

### 1. Extract
- **Source**: GitHub API (Issues endpoint).
- **Target**: MinIO Bucket `github-raw`.
- **Logic**: 
  - Incremental extraction based on execution date.
  - Handles rate limits (429) and pagination automatically.
  - Partitions data by date (`dt=YYYY-MM-DD`).

### 2. Load
- **Source**: MinIO JSON files.
- **Target**: Postgres Table `raw.github_issues`.
- **Logic**:
  - Idempotent load (deletes existing data for the date before inserting).
  - Uses `JSONB` column to store full fidelity raw data.

### 3. Transform
- **Source**: `raw.github_issues`.
- **Target**: Star Schema in `analytics` schema.
- **Logic**:
  - **`dim_users`**: Type 1 Dimension (Upsert logic).
  - **`fact_issues`**: Transactional Fact table (Full reload for partition).

## 🛠️ Setup & Running

**Prerequisites**: Docker Desktop installed.

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd Production-Grade-ETL-Pipeline-Tasks
   ```

2. **Configure Environment**:
   Duplicate `.env`:
   ```bash
   GITHUB_TOKEN=your_token_here
   ```

3. **Start Infrastructure**:
   ```bash
   docker compose up -d --build
   ```

4. **Access UI**:
   - Airflow: [http://localhost:8080](http://localhost:8080) (User/Pass: `admin`/`admin`)
   - MinIO: [http://localhost:9001](http://localhost:9001) (User/Pass: `minioadmin`/`minioadmin`)

## 📊 Data Model

### `analytics.fact_issues`
| Column | Type | Description |
|--------|------|-------------|
| `issue_id` | BIGINT | GitHub Issue ID (PK) |
| `user_id` | BIGINT | FK to dim_users |
| `state` | TEXT | open/closed |
| `comments_count` | INT | Number of comments |
| `execution_date` | DATE | Partition Key |

### `analytics.dim_users`
| Column | Type | Description |
|--------|------|-------------|
| `user_id` | BIGINT | GitHub User ID (PK) |
| `login` | TEXT | Username |
| `type` | TEXT | User/Organization |

## 🧪 Verification

To manually trigger a run:
```bash
docker compose exec airflow-webserver airflow dags trigger github_extraction
```

Check the results in Postgres:
```bash
docker compose exec postgres psql -U airflow -c "SELECT * FROM analytics.fact_issues LIMIT 5;"
```
