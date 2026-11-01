-- ============================================================
-- UPI Transaction Success Rate Analysis — SQL Queries
-- Author: Anagh P.
-- Database: SQLite / PostgreSQL compatible
-- Table: upi_transactions
-- ============================================================

-- ── 1. Overall KPI Dashboard ─────────────────────────────────────────────────
SELECT
    COUNT(*)                                              AS total_transactions,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)  AS successful,
    SUM(CASE WHEN status = 'Failed'  THEN 1 ELSE 0 END)  AS failed,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                     AS success_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2)
                                                          AS total_volume_inr,
    ROUND(AVG(latency_ms), 0)                             AS avg_latency_ms
FROM upi_transactions;


-- ── 2. Bank-wise Success Rate (ranked worst → best) ──────────────────────────
SELECT
    bank,
    COUNT(*)                                             AS total_txns,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS success_count,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS success_rate_pct,
    ROUND(AVG(latency_ms), 0)                            AS avg_latency_ms
FROM upi_transactions
GROUP BY bank
ORDER BY success_rate_pct ASC;


-- ── 3. Merchant-level SR Analysis with Volume ────────────────────────────────
SELECT
    merchant,
    category,
    COUNT(*)                                             AS total_txns,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS success_count,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS success_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END), 2)
                                                         AS gmv_inr,
    -- Revenue at risk from failures
    ROUND(AVG(CASE WHEN status = 'Failed' THEN amount ELSE NULL END), 2)
                                                         AS avg_failed_txn_amount
FROM upi_transactions
GROUP BY merchant, category
ORDER BY success_rate_pct ASC;


-- ── 4. Platform-wise SR Analysis ─────────────────────────────────────────────
SELECT
    platform,
    COUNT(*)                                             AS total_txns,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS success_count,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS success_rate_pct,
    ROUND(AVG(latency_ms), 0)                            AS avg_latency_ms
FROM upi_transactions
GROUP BY platform
ORDER BY success_rate_pct ASC;


-- ── 5. Category-wise SR (E-commerce, Travel, Subscription…) ──────────────────
SELECT
    category,
    COUNT(*)                                              AS total_txns,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                     AS success_rate_pct,
    ROUND(SUM(amount), 2)                                 AS total_volume_inr
FROM upi_transactions
GROUP BY category
ORDER BY success_rate_pct ASC;


-- ── 6. Root Cause Analysis (RCA) — Failure Breakdown ────────────────────────
SELECT
    failure_reason,
    COUNT(*)                                              AS failure_count,
    ROUND(100.0 * COUNT(*) /
          SUM(COUNT(*)) OVER (), 2)                       AS pct_of_failures,
    ROUND(AVG(amount), 2)                                 AS avg_txn_amount,
    ROUND(AVG(latency_ms), 0)                             AS avg_latency_ms
FROM upi_transactions
WHERE status = 'Failed'
GROUP BY failure_reason
ORDER BY failure_count DESC;


-- ── 7. Hourly Bottleneck Detection (peak failure hours) ──────────────────────
SELECT
    hour,
    COUNT(*)                                             AS total_txns,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END)  AS failures,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS success_rate_pct,
    ROUND(AVG(latency_ms), 0)                            AS avg_latency_ms
FROM upi_transactions
GROUP BY hour
ORDER BY success_rate_pct ASC
LIMIT 10;   -- worst 10 hours


-- ── 8. Monthly SR Trend ───────────────────────────────────────────────────────
SELECT
    month,
    COUNT(*)                                             AS total_txns,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS success_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END) / 1e6, 2)
                                                         AS volume_mn_inr
FROM upi_transactions
GROUP BY month
ORDER BY MIN(date);


-- ── 9. SR Dip Detection (weeks below threshold) ───────────────────────────────
-- Identifies anomalous weeks for alerting / escalation
WITH weekly_sr AS (
    SELECT
        strftime('%W', date)                             AS week_num,
        COUNT(*)                                         AS total,
        ROUND(
            100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
        )                                                AS sr_pct
    FROM upi_transactions
    GROUP BY week_num
)
SELECT
    week_num,
    total,
    sr_pct,
    CASE
        WHEN sr_pct < 91   THEN 'CRITICAL — Escalate'
        WHEN sr_pct < 92.5 THEN 'WARNING — Monitor'
        ELSE                    'HEALTHY'
    END                                                  AS alert_status
FROM weekly_sr
WHERE sr_pct < 92.5          -- flag only anomalous weeks
ORDER BY sr_pct ASC;


-- ── 10. Bank × Platform Cross-analysis (bottleneck matrix) ──────────────────
SELECT
    bank,
    platform,
    COUNT(*)                                             AS total_txns,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS success_rate_pct
FROM upi_transactions
GROUP BY bank, platform
HAVING COUNT(*) > 50
ORDER BY success_rate_pct ASC
LIMIT 20;


-- ── 11. High-Value Failure Analysis (amount > ₹10,000) ───────────────────────
SELECT
    bank,
    merchant,
    failure_reason,
    COUNT(*)                                             AS high_value_failures,
    ROUND(SUM(amount), 2)                                AS revenue_at_risk_inr
FROM upi_transactions
WHERE status = 'Failed'
  AND amount > 10000
GROUP BY bank, merchant, failure_reason
ORDER BY revenue_at_risk_inr DESC
LIMIT 15;
