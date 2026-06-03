\COPY billing_records (record_id,ts,account_id,team,service,region,
    resource_type,usage_hours,unit_cost,total_cost,anomaly_flag)
FROM '/absolute/path/to/data/raw/billing_data.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',', ENCODING 'UTF8');

REFRESH MATERIALIZED VIEW mv_daily_cost;
SELECT COUNT(*) AS total_rows, SUM(anomaly_flag::INT) AS anomaly_rows FROM billing_records;
