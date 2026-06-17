# AI Cost Optimization Portfolio

> **End-to-end data analytics & ML portfolio project** demonstrating cloud cost anomaly detection, root-cause analysis, and a real-time optimization dashboard — targeting Data Analytics, MLOps, and Applied AI roles.

Project Portfolio Page: https://copilot.microsoft.com/shares/artifacts/JwDtbU3goEGgncCUCJf7c?expand=true
---

## 📌 Project Overview

Cloud infrastructure costs can spiral quickly across multi-tenant environments. This project simulates a realistic cloud billing dataset, performs exploratory data analysis, builds anomaly-detection models, and surfaces insights via a Streamlit dashboard — all backed by a PostgreSQL data warehouse.

| Layer | Technology |
|---|---|
| Data Generation | Python 3.10+,  NumPy, pandas |
| Storage | PostgreSQL 15, CSV (raw/processed) |
| Analysis | Jupyter, pandas, seaborn, matplotlib |
| ML / Anomaly Detection | scikit-learn, Isolation Forest, DBSCAN |
| Dashboard | Streamlit, Plotly |
| CI | GitHub Actions |

---

## 🗂️ Repository Structure

```
ai-cost-optimization-portfolio/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── synthetic_generator/
│   │   └── synth_generator.py
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_anomaly_detection.ipynb
│   └── 03_cost_attribution.ipynb
├── sql/
│   ├── schema.sql
│   ├── load_data.sql
│   └── cost_queries.sql
├── dashboard/
│   └── app.py
├── models/
├── tests/
│   └── test_synth_generator.py
└── .github/
    └── workflows/
        └── ci.yml
```

---

## 🚀 Quick Start

### 1 — Clone & set up environment

```bash
git clone https://github.com/your-username/ai-cost-optimization-portfolio.git
cd ai-cost-optimization-portfolio
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Configure environment variables

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3 — Generate synthetic billing data

```bash
python data/synthetic_generator/synth_generator.py \
    --rows 50000 \
    --out data/raw/billing_data.csv
```

### 4 — Load data into PostgreSQL

```bash
psql -U $PGUSER -d $PGDATABASE -f sql/schema.sql
psql -U $PGUSER -d $PGDATABASE -f sql/load_data.sql
```

### 5 — Run the EDA notebook

```bash
jupyter lab notebooks/01_EDA.ipynb
```

### 6 — Launch the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE billing_records (
    record_id       UUID        PRIMARY KEY,
    ts              TIMESTAMPTZ NOT NULL,
    account_id      VARCHAR(20) NOT NULL,
    team            VARCHAR(50),
    service         VARCHAR(50),
    region          VARCHAR(30),
    resource_type   VARCHAR(50),
    usage_hours     NUMERIC(10,2),
    unit_cost       NUMERIC(10,4),
    total_cost      NUMERIC(12,4),
    anomaly_flag    BOOLEAN     DEFAULT FALSE,
    ingested_at     TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🧑‍💻 Author
**Bidhu Kar** — Sr Data Analyst  
Portfolio project · June 2026

## 📄 License
MIT License
