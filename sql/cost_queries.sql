-- 1. Spend by service
SELECT service, ROUND(SUM(total_cost),2) AS total_spend,
       ROUND(100.0*SUM(total_cost)/SUM(SUM(total_cost)) OVER(),2) AS pct
FROM billing_records GROUP BY service ORDER BY total_spend DESC;

-- 2. Daily trend (last 30 days)
SELECT DATE_TRUNC('day',ts)::DATE AS day,
       ROUND(SUM(total_cost),2) AS daily_spend,
       SUM(anomaly_flag::INT) AS anomaly_count
FROM billing_records WHERE ts >= NOW() - INTERVAL '30 days'
GROUP BY 1 ORDER BY 1;

-- 3. Top 10 cost drivers
SELECT team, service, resource_type, ROUND(SUM(total_cost),2) AS total_spend
FROM billing_records
GROUP BY team,service,resource_type ORDER BY total_spend DESC LIMIT 10;

-- 4. Anomaly impact by service
SELECT service,
       SUM(anomaly_flag::INT) AS anomaly_records,
       ROUND(100.0*SUM(anomaly_flag::INT)/COUNT(*),2) AS anomaly_rate_pct,
       ROUND(SUM(CASE WHEN anomaly_flag THEN total_cost ELSE 0 END),2) AS anomaly_spend
FROM billing_records GROUP BY service ORDER BY anomaly_spend DESC;

-- 5. 7-day rolling average (window function)
SELECT DATE_TRUNC('day',ts)::DATE AS day, service,
       ROUND(SUM(total_cost),2) AS daily_spend,
       ROUND(AVG(SUM(total_cost)) OVER (
           PARTITION BY service ORDER BY DATE_TRUNC('day',ts)
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),2) AS rolling_7d_avg
FROM billing_records GROUP BY DATE_TRUNC('day',ts), service ORDER BY day, service;
