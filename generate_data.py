"""
UPI Transaction Dataset Generator
Generates ~50,000 realistic UPI transaction records based on RBI payment data patterns.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

N = 50000
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

BANKS = {
    "SBI":        {"weight": 0.22, "sr_base": 0.921},
    "HDFC":       {"weight": 0.18, "sr_base": 0.943},
    "ICICI":      {"weight": 0.15, "sr_base": 0.938},
    "Axis":       {"weight": 0.10, "sr_base": 0.930},
    "Kotak":      {"weight": 0.07, "sr_base": 0.935},
    "Yes Bank":   {"weight": 0.06, "sr_base": 0.885},
    "IDFC First": {"weight": 0.05, "sr_base": 0.897},
    "PNB":        {"weight": 0.08, "sr_base": 0.905},
    "BOB":        {"weight": 0.05, "sr_base": 0.912},
    "Canara":     {"weight": 0.04, "sr_base": 0.908},
}

MERCHANTS = {
    "Amazon":      {"category": "E-commerce",    "weight": 0.12, "sr_mod": +0.02},
    "Flipkart":    {"category": "E-commerce",    "weight": 0.10, "sr_mod": +0.015},
    "Meesho":      {"category": "E-commerce",    "weight": 0.06, "sr_mod": -0.01},
    "MakeMyTrip":  {"category": "Travel",        "weight": 0.07, "sr_mod": +0.01},
    "IRCTC":       {"category": "Travel",        "weight": 0.08, "sr_mod": -0.025},
    "RedBus":      {"category": "Travel",        "weight": 0.04, "sr_mod": -0.005},
    "Netflix":     {"category": "Subscription",  "weight": 0.05, "sr_mod": +0.025},
    "Spotify":     {"category": "Subscription",  "weight": 0.04, "sr_mod": +0.02},
    "Swiggy":      {"category": "Food Delivery", "weight": 0.09, "sr_mod": +0.01},
    "Zomato":      {"category": "Food Delivery", "weight": 0.08, "sr_mod": +0.008},
    "BigBasket":   {"category": "Grocery",       "weight": 0.06, "sr_mod": 0.0},
    "Blinkit":     {"category": "Grocery",       "weight": 0.05, "sr_mod": -0.005},
    "PhonePe P2P": {"category": "P2P Transfer",  "weight": 0.08, "sr_mod": +0.015},
    "Paytm P2P":   {"category": "P2P Transfer",  "weight": 0.05, "sr_mod": +0.005},
    "Other":       {"category": "Others",        "weight": 0.03, "sr_mod": -0.015},
}

PLATFORMS  = ["Android App", "iOS App", "Web Browser", "Third-Party Integration"]
PLT_WEIGHTS = [0.52, 0.28, 0.12, 0.08]
PLT_SR_MOD  = [+0.01, +0.015, -0.005, -0.03]

FAILURE_REASONS = [
    "Bank Downtime", "Incorrect PIN", "Insufficient Funds",
    "Network Timeout", "Duplicate Transaction", "Daily Limit Exceeded",
    "PSP Unavailable", "VPA Not Registered", "Unknown Error",
]
FAIL_WEIGHTS = [0.20, 0.18, 0.16, 0.14, 0.10, 0.08, 0.07, 0.04, 0.03]

bank_names    = list(BANKS.keys())
bank_weights  = [BANKS[b]["weight"] for b in bank_names]
merch_names   = list(MERCHANTS.keys())
merch_weights = [MERCHANTS[m]["weight"] for m in merch_names]

def random_timestamp():
    delta = end_date - start_date
    secs  = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=secs)

records = []
for i in range(N):
    ts       = random_timestamp()
    bank     = random.choices(bank_names, weights=bank_weights)[0]
    merchant = random.choices(merch_names, weights=merch_weights)[0]
    plt_idx  = random.choices(range(4), weights=PLT_WEIGHTS)[0]
    platform = PLATFORMS[plt_idx]

    sr = (BANKS[bank]["sr_base"]
          + MERCHANTS[merchant]["sr_mod"]
          + PLT_SR_MOD[plt_idx])
    # Weekend dip
    if ts.weekday() >= 5:
        sr -= 0.008
    # Peak-hour spike (9–11 PM)
    if 21 <= ts.hour <= 23:
        sr -= 0.012
    # Monthly salary credit day (1st–3rd) surge
    if ts.day <= 3:
        sr -= 0.006
    sr = max(0.75, min(0.98, sr))

    success = random.random() < sr
    status  = "Success" if success else "Failed"
    reason  = "NA" if success else random.choices(FAILURE_REASONS, weights=FAIL_WEIGHTS)[0]

    amount = round(np.random.lognormal(mean=6.5, sigma=1.2), 2)
    amount = min(amount, 100000)
    latency_ms = int(np.random.exponential(scale=800) + 200) if success else int(np.random.exponential(scale=2500) + 500)

    records.append({
        "transaction_id":   f"TXN{1000000 + i}",
        "timestamp":        ts,
        "date":             ts.date(),
        "hour":             ts.hour,
        "day_of_week":      ts.strftime("%A"),
        "month":            ts.strftime("%B"),
        "bank":             bank,
        "merchant":         merchant,
        "category":         MERCHANTS[merchant]["category"],
        "platform":         platform,
        "amount":           amount,
        "status":           status,
        "failure_reason":   reason,
        "latency_ms":       latency_ms,
    })

df = pd.DataFrame(records)
df.sort_values("timestamp", inplace=True)
df.reset_index(drop=True, inplace=True)
df.to_csv("/tmp/upi_project/upi_transactions.csv", index=False)
print(f"Dataset generated: {len(df)} rows")
print(df["status"].value_counts())
print(f"Overall SR: {(df['status']=='Success').mean():.3f}")
