DROP TABLE IF EXISTS billing_records CASCADE;

CREATE TABLE billing_records (
    record_id     UUID         PRIMARY KEY,
    ts            TIMESTAMPTZ  NOT NULL,
    account_id    VARCHAR(20)  NOT NULL,
    team          VARCHAR(50),
    service       VARCHAR(50),
    region        VARCHAR(30),
    resource_type VARCHAR(50),
    usage_hours   NUMERIC(10,2),
    unit_cost     NUMERIC(10,4),
    total_cost    NUMERIC(12,4),
    anomaly_flag  BOOLEAN      DEFAULT FALSE,
    ingested_at   TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX idx_billing_ts      ON billing_records (ts);
CREATE INDEX idx_billing_team    ON billing_records (team);
CREATE INDEX idx_billing_service ON billing_records (service);
CREATE INDEX idx_billing_anomaly ON billing_records (anomaly_flag) WHERE anomaly_flag = TRUE;

CREATE MATERIALIZED VIEW mv_daily_cost AS
SELECT DATE_TRUNC('day', ts) AS day, service, team, region,
       SUM(total_cost) AS total_cost, COUNT(*) AS record_count,
       SUM(anomaly_flag::INT) AS anomaly_count
FROM billing_records
GROUP BY 1,2,3,4 WITH DATA;
