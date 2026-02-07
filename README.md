# Production-Grade ETL Pipeline

A **production-style, end-to-end ETL pipeline** that ingests data from the **GitHub API**, stores raw data in **object storage**, and transforms it into an **analytics-ready dimensional data model**. The pipeline is designed with **reliability, idempotency, and scalability** in mind and is orchestrated using **Apache Airflow**.

---

## 🏗 Architecture Overview

GitHub API
↓
Python Ingestion Layer
↓
Object Storage (MinIO / S3) — Raw Layer
↓
Apache Airflow Orchestration
↓
PostgreSQL — Analytics Warehouse


This architecture follows a **modern data lake + warehouse pattern**, where raw ingestion is decoupled from transformation and analytics. **Apache Airflow** manages scheduling, dependencies, retries, and observability to ensure production-grade reliability.

![Architecture Diagram](https://mermaid.ink/img/pako:eNqNksFqwzAMhl_F6NRC-wI5DDaM0XYY7WWH4iS2G9vYyHZSStl7zzlttsF220GybP_3S0_QGiuRgr7Zq8Jq9OC84WdFj4_Pj4_39y_w8gS2g95a6ODsY9e11kF_clZ5-OLsE9Q1dPAZ_tMO7i-vL5dK1dDA0Vn4o2_eWqjhzVn4u29eK1XD2ln4q29eK9VAf2YV1fC7o0o1lM4qPqlSTW-qVEO1UqWaalap5u-qVEO9UqWaa1ap5u9VqumN_xqa9l9D0_5r_jT0_2-o_z-hBvr_F6r5_4RqqP8_oab_E2r-ruafhurnK8xLdC0s0B9iWqA_xLRAf4hpgf4Q0wL9IaYF-kNM8_9DTAu0n5gWaD8xLdB-Ylqg_cS0QPuJaYH2E9M8_xPT_P4npvnzT0zz65-Y5s8_Mc2ff2KaP__ENH_-Q0zz65-Y5tc_Mc2vf2KaP__ENH_-ianVq4Iq1CuCapCrgmqQ84JqkKuCStQrgkrUK4JqkKuCatQrgmrUK4Iq0SuCKtErgmrQq4Jq0KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCatSrgmrUq4Jq1KuCalCvgmpQr4JqUK-Calculated)

---

## 🚀 Tech Stack

- **Language**: Python 3.9+
- **Orchestration**: Apache Airflow
- **Object Storage (Raw Layer)**: MinIO (S3-Compatible)
- **Data Warehouse**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git

---

## 🔄 Data Flow

1. **Extract** data from the GitHub API using Python, handling pagination and API rate limits.
2. **Store** raw API responses as JSON files in object storage, partitioned by execution date.
3. **Load** raw JSON data into a staging table in PostgreSQL while preserving full data fidelity.
4. **Transform** staged data into analytics-ready fact and dimension tables using a **star schema**.
5. **Validate** data post-load to ensure completeness and consistency.

---

## 🧩 Airflow DAG Design

- The pipeline is orchestrated using a **modular Apache Airflow DAG**.
- Tasks are designed to be **independently retryable**.
- Dependencies enforce correct execution order.
- Retries and failure handling are configured at the task level.
- DAG runs are **safe to re-execute** due to idempotent load logic.

This design enables **operational safety and production readiness**.

---

## 🔁 Incremental & Idempotent Processing

- Incremental extraction is driven by the **Airflow execution date**.
- Raw data is partitioned by date in object storage (`dt=YYYY-MM-DD`).
- Load steps implement **idempotent logic** by removing existing records for a partition before inserting new data.
- Supports safe re-runs, historical backfills, and recovery from partial failures.

---

## 📊 Data Model

### `analytics.fact_issues`

| Column | Type | Description |
|------|------|-------------|
| `issue_id` | BIGINT | GitHub Issue ID (Primary Key) |
| `user_id` | BIGINT | Foreign Key to `dim_users` |
| `state` | TEXT | Issue state (open/closed) |
| `comments_count` | INT | Number of comments |
| `execution_date` | DATE | Partition Key |

### `analytics.dim_users`

| Column | Type | Description |
|------|------|-------------|
| `user_id` | BIGINT | GitHub User ID (Primary Key) |
| `login` | TEXT | GitHub username |
| `type` | TEXT | User or Organization |

---

## 🛡 Data Quality & Reliability

- Schema validation during ingestion
- Idempotent load logic to prevent duplicate records
- Controlled retries for transient API and infrastructure failures
- Separation of raw and analytics layers to support reprocessing

These practices align with **production data engineering standards**.

---

## 🛠 Setup & Running

**Prerequisites**: Docker Desktop installed

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd Production-Grade-ETL-Pipeline-Tasks


2. **Configure environment variables**
   ```bash
   GITHUB_TOKEN=your_token_here

3. **Start infrastructure**
   ```bash
   docker compose up -d --build
  

4. **Access UIs**

Airflow: http://localhost:8080
 (admin / admin)

MinIO: http://localhost:9001
 (minioadmin / minioadmin)





**🧠 Key Design Decisions**

Object storage decouples ingestion from transformation for scalability and fault tolerance.

PostgreSQL simulates a cloud-based analytical warehouse suitable for dimensional modeling.

Apache Airflow provides scheduling, retries, observability, and dependency management.

Idempotent pipelines ensure safe reprocessing and production reliability.

**🔮 Future Improvements**

Migrate analytics warehouse to Amazon Redshift

Add automated data quality checks (e.g., Great Expectations)

Implement monitoring and alerting for DAG failures

Add CI/CD validation for Airflow DAGs

 
