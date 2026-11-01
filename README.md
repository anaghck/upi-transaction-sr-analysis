# UPI Transaction Success Rate Analysis

**Tools:** Python · Pandas · Matplotlib · Seaborn · SQL  
**Dataset:** 50,000 synthetic UPI transactions (Jan–Dec 2024)  
**Domain:** Fintech · Digital Payments · Business Analysis

---

## Project Overview

Analyzed 50,000 UPI payment transactions across 15 merchants, 10 banks, 7 industry categories, and 4 platforms to identify success rate bottlenecks, investigate root causes of payment failures, and generate actionable recommendations to improve transaction reliability.

---

## Key Findings

| Metric | Value |
|---|---|
| Total Transactions | 50,000 |
| Overall Success Rate | **93.03%** |
| Total Payment Volume | ₹6.37 Cr |
| Average Latency | 1,135 ms |
| Critical Failure Mode | Bank Downtime (20% of failures) |

---

## Analysis Performed

### 1. Bank-wise Success Rate Analysis
- Ranked all 10 issuer banks by SR
- Identified **Yes Bank (89.5%)** and **IDFC First (90.5%)** as critical underperformers — 3.5% below the overall average
- HDFC (94.8%) and ICICI (94.8%) consistently above benchmark

### 2. Merchant-level SR Analysis
- IRCTC and Meesho flagged as critical merchants (SR < 91%) requiring escalation
- Netflix and Spotify showed highest SR (>94%) — low failure rate correlates with recurring/saved mandates
- Identified average failed transaction amount per merchant to quantify revenue at risk

### 3. Platform-wise SR Analysis
- **Third-Party Integrations (88.7%)** underperformed by 4.3% vs iOS App (93.7%)
- Web Browser at 91.7% — recommended SDK upgrade and API timeout review
- Root cause: Third-party integrations have higher latency (2,500+ ms avg on failures)

### 4. Category-wise SR Analysis
- **Travel (91.9%)** and **Others (91.3%)** below threshold — IRCTC peak-load congestion identified as primary driver
- **Subscription (94.4%)** leads — mandate-based payments require no real-time bank auth
- Recommended mandate-based payment flows for high-frequency Travel merchants

### 5. Root Cause Analysis (RCA)
Top 3 failure reasons account for **54% of all failures**:
1. Bank Downtime — 20.0%
2. Incorrect PIN — 18.0%
3. Insufficient Funds — 16.0%

RCA-driven recommendations:
- Route transactions to backup banks during downtime windows
- Add real-time PIN retry nudge in the UX flow
- Implement pre-debit balance check where bank API allows

### 6. Hourly & Weekly Anomaly Detection
- Built automated SR dip alerts: weeks below 91% flagged as CRITICAL, 91–92.5% as WARNING
- Identified 9 PM–11 PM as peak failure window (SR drops ~1.2%)
- Salary credit days (1st–3rd of month) show 0.6% SR dip due to volume surge

---

## Visualizations

| Chart | Insight |
|---|---|
| `01_bank_sr.png` | Bank-wise SR ranking with benchmark line |
| `02_category_sr.png` | Category performance vs overall SR |
| `03_platform_sr.png` | Platform SR comparison |
| `04_failure_rca.png` | Root cause breakdown of failures |
| `05_hourly_heatmap.png` | Day × Hour SR heatmap — bottleneck detection |
| `06_weekly_trend.png` | SR trend with anomaly annotations |
| `07_merchant_sr.png` | Merchant SR with critical/watch/healthy zones |

---

## SQL Queries Included

11 production-style SQL queries covering:
- KPI dashboard (overall SR, volume, latency)
- Bank / merchant / platform / category drill-downs
- Failure RCA with window functions
- Anomaly detection with threshold-based alerting
- High-value transaction failure analysis

---

## Files

```
upi_transactions.csv    — 50,000 transaction records
generate_data.py        — Dataset generation script
analysis.py             — Full Python EDA + 7 visualizations
sql_queries.sql         — 11 analytical SQL queries
charts/                 — All output charts (PNG)
README.md               — This file
```

---

## Business Impact

- Estimated ₹82L+ revenue at risk from Third-Party Integration failures
- Identified 2 banks and 2 merchants for priority escalation
- Dip detection logic reduces anomaly response time from manual daily review to real-time alerts
- Category routing recommendation (mandate-based for Travel) projected to improve category SR by ~1.5%
