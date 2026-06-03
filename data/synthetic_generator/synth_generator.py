"""
synth_generator.py
==================
Generates a synthetic cloud billing dataset.

Usage:
    python synth_generator.py --rows 50000 --out ../../data/raw/billing_data.csv
"""

import argparse, uuid, random, logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

fake = Faker()
Faker.seed(42); np.random.seed(42); random.seed(42)

TEAMS = ["platform-eng","ml-infra","data-engineering","backend-services",
         "frontend","security","finops","research"]

SERVICES = {
    "Compute":   ["vm-standard","vm-memory-optimized","vm-gpu","spot-instance"],
    "Storage":   ["blob-storage","object-store","cold-archive","file-share"],
    "ML":        ["training-job","inference-endpoint","feature-store","notebook-instance"],
    "Database":  ["postgres-managed","mysql-managed","cosmos-db","redis-cache"],
    "Network":   ["load-balancer","cdn","vpn-gateway","private-link"],
    "Analytics": ["dataflow-job","bigquery-slot","spark-cluster","data-factory"],
    "Serverless":["function-app","cloud-run","event-grid","api-gateway"],
}

REGIONS = ["us-east-1","us-west-2","eu-west-1","eu-central-1",
           "ap-southeast-1","ap-northeast-1","us-central-1"]

UNIT_COST_RANGES = {
    "Compute":   (0.05, 2.50), "Storage":   (0.001,0.08),
    "ML":        (0.20, 8.00), "Database":  (0.10, 3.00),
    "Network":   (0.01, 0.50), "Analytics": (0.05, 4.00),
    "Serverless":(0.001,0.30),
}

ANOMALY_RATE = 0.03
ANOMALY_SPIKE = (5, 20)


def random_timestamp(days_back=90):
    now = datetime.now(tz=timezone.utc)
    return now - timedelta(seconds=random.randint(0, days_back * 86_400))


def pick_service_and_resource():
    service = random.choice(list(SERVICES.keys()))
    return service, random.choice(SERVICES[service])


def compute_cost(service, usage_hours, is_anomaly):
    lo, hi = UNIT_COST_RANGES[service]
    unit_cost = round(random.uniform(lo, hi), 4)
    total_cost = round(usage_hours * unit_cost, 4)
    if is_anomaly:
        total_cost = round(total_cost * random.uniform(*ANOMALY_SPIKE), 4)
    return unit_cost, total_cost


def generate_billing_data(n_rows):
    logger.info("Generating %d billing records …", n_rows)
    account_pool = ["acct-" + uuid.uuid4().hex[:8] for _ in range(30)]
    records = []
    for i in range(n_rows):
        is_anomaly = random.random() < ANOMALY_RATE
        service, resource_type = pick_service_and_resource()
        usage_hours = round(abs(np.random.lognormal(mean=2.5, sigma=1.2)), 2)
        unit_cost, total_cost = compute_cost(service, usage_hours, is_anomaly)
        records.append({
            "record_id": str(uuid.uuid4()),
            "timestamp": random_timestamp().isoformat(),
            "account_id": random.choice(account_pool),
            "team": random.choice(TEAMS),
            "service": service, "region": random.choice(REGIONS),
            "resource_type": resource_type, "usage_hours": usage_hours,
            "unit_cost": unit_cost, "total_cost": total_cost,
            "anomaly_flag": is_anomaly,
        })
        if (i + 1) % 10_000 == 0:
            logger.info("  … %d / %d rows", i + 1, n_rows)
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--out",  type=str, default="data/raw/billing_data.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    np.random.seed(args.seed); random.seed(args.seed); Faker.seed(args.seed)
    df = generate_billing_data(args.rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    logger.info("Saved %d rows → %s", len(df), out.resolve())
    print(f"\nTotal rows : {len(df):,}")
    print(f"Anomalies  : {df['anomaly_flag'].sum():,} ({100*df['anomaly_flag'].mean():.2f}%)")
    print(f"Total cost : ${df['total_cost'].sum():,.2f}")

if __name__ == "__main__":
    main()
