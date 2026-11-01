"""
UPI Transaction Success Rate Analysis
Author: Anagh P.
Tools: Python (Pandas, Matplotlib, Seaborn)
Dataset: 50,000 synthetic UPI transactions (Jan–Dec 2024)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings, os
warnings.filterwarnings("ignore")

OUTPUT = "/tmp/upi_project/charts"
os.makedirs(OUTPUT, exist_ok=True)

# ─── Palette ────────────────────────────────────────────────────────────────
PHONEPE_PURPLE = "#5F259F"
SUCCESS_GREEN  = "#2ECC71"
FAIL_RED       = "#E74C3C"
WARN_ORANGE    = "#F39C12"
LIGHT_BG       = "#F9F7FD"
GRID_COLOR     = "#E0D7F0"

BANK_PALETTE  = sns.color_palette("Purples_d", 10)
CAT_PALETTE   = [PHONEPE_PURPLE, "#8E44AD", "#2980B9", SUCCESS_GREEN,
                 WARN_ORANGE, FAIL_RED, "#1ABC9C"]

def style_axis(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(LIGHT_BG)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, linestyle="--")
    ax.spines[["top","right","left"]].set_visible(False)
    ax.spines["bottom"].set_color("#CCCCCC")
    if title:  ax.set_title(title, fontsize=13, fontweight="bold", pad=10, color="#1A1A2E")
    if xlabel: ax.set_xlabel(xlabel, fontsize=10, color="#555")
    if ylabel: ax.set_ylabel(ylabel, fontsize=10, color="#555")
    ax.tick_params(colors="#555", labelsize=9)

# ─── Load data ───────────────────────────────────────────────────────────────
df = pd.read_csv("/tmp/upi_project/upi_transactions.csv", parse_dates=["timestamp","date"])
df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
df["success_flag"] = (df["status"] == "Success").astype(int)

# ─── KPI Summary ─────────────────────────────────────────────────────────────
total_txns   = len(df)
total_success = df["success_flag"].sum()
total_failed  = total_txns - total_success
overall_sr    = total_success / total_txns * 100
total_vol     = df[df["status"]=="Success"]["amount"].sum()
avg_latency   = df["latency_ms"].mean()

print("=" * 55)
print("  UPI TRANSACTION SUCCESS RATE — KEY METRICS  ")
print("=" * 55)
print(f"  Total Transactions : {total_txns:,}")
print(f"  Successful         : {total_success:,}  ({overall_sr:.2f}%)")
print(f"  Failed             : {total_failed:,}")
print(f"  Total Volume (₹)   : ₹{total_vol:,.0f}")
print(f"  Avg Latency        : {avg_latency:.0f} ms")
print("=" * 55)

# ─── Chart 1 : Bank-wise SR ──────────────────────────────────────────────────
bank_sr = (df.groupby("bank")["success_flag"]
             .agg(["sum","count"])
             .assign(sr=lambda x: x["sum"]/x["count"]*100)
             .sort_values("sr"))

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(LIGHT_BG)
bars = ax.barh(bank_sr.index, bank_sr["sr"],
               color=[SUCCESS_GREEN if v >= 93 else WARN_ORANGE if v >= 90 else FAIL_RED
                      for v in bank_sr["sr"]],
               edgecolor="white", linewidth=0.5, height=0.6)
ax.axvline(overall_sr, color=PHONEPE_PURPLE, linewidth=1.8, linestyle="--",
           label=f"Overall SR: {overall_sr:.1f}%")
for bar, val in zip(bars, bank_sr["sr"]):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=9, color="#333")
style_axis(ax, "Bank-wise Transaction Success Rate (2024)", "Success Rate (%)", "Bank")
ax.set_xlim(82, 100)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/01_bank_sr.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 1 saved: bank-wise SR")

# ─── Chart 2 : Category-wise SR ──────────────────────────────────────────────
cat_sr = (df.groupby("category")["success_flag"]
            .agg(["sum","count"])
            .assign(sr=lambda x: x["sum"]/x["count"]*100,
                    vol=lambda x: x["count"])
            .sort_values("sr", ascending=False))

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(LIGHT_BG)
colors = [SUCCESS_GREEN if v >= 93 else WARN_ORANGE if v >= 90 else FAIL_RED
          for v in cat_sr["sr"]]
bars = ax.bar(cat_sr.index, cat_sr["sr"], color=colors,
              edgecolor="white", linewidth=0.6, width=0.55)
ax.axhline(overall_sr, color=PHONEPE_PURPLE, linewidth=1.8, linestyle="--",
           label=f"Overall SR: {overall_sr:.1f}%")
for bar, val in zip(bars, cat_sr["sr"]):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.05,
            f"{val:.1f}%", ha="center", fontsize=9, color="#333")
style_axis(ax, "Category-wise Transaction Success Rate (2024)", "Category", "Success Rate (%)")
ax.set_ylim(85, 98)
ax.legend(fontsize=9)
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/02_category_sr.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 2 saved: category-wise SR")

# ─── Chart 3 : Platform-wise SR ──────────────────────────────────────────────
plt_sr = (df.groupby("platform")["success_flag"]
            .agg(["sum","count"])
            .assign(sr=lambda x: x["sum"]/x["count"]*100)
            .sort_values("sr", ascending=False))

fig, ax = plt.subplots(figsize=(9, 4))
fig.patch.set_facecolor(LIGHT_BG)
bars = ax.bar(plt_sr.index, plt_sr["sr"],
              color=[PHONEPE_PURPLE, "#8E44AD", WARN_ORANGE, FAIL_RED],
              edgecolor="white", linewidth=0.6, width=0.45)
ax.axhline(overall_sr, color=FAIL_RED, linewidth=1.5, linestyle="--",
           label=f"Overall SR: {overall_sr:.1f}%")
for bar, val in zip(bars, plt_sr["sr"]):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.05,
            f"{val:.1f}%", ha="center", fontsize=10, color="#333", fontweight="bold")
style_axis(ax, "Platform-wise Transaction Success Rate (2024)", "Platform", "Success Rate (%)")
ax.set_ylim(86, 98)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/03_platform_sr.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 3 saved: platform-wise SR")

# ─── Chart 4 : Failure Reason Distribution ───────────────────────────────────
fail_df = df[df["status"] == "Failed"]
reason_counts = fail_df["failure_reason"].value_counts()

fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor(LIGHT_BG)
palette = sns.color_palette("RdPu", len(reason_counts))
bars = ax.barh(reason_counts.index, reason_counts.values,
               color=palette, edgecolor="white", height=0.6)
for bar, val in zip(bars, reason_counts.values):
    ax.text(val + 5, bar.get_y() + bar.get_height()/2,
            str(val), va="center", fontsize=9)
style_axis(ax, "Root Cause Analysis — Failed Transaction Breakdown",
           "Number of Failures", "Failure Reason")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/04_failure_rca.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 4 saved: failure RCA")

# ─── Chart 5 : Hourly SR Heatmap ─────────────────────────────────────────────
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
hourly = (df.groupby(["day_of_week","hour"])["success_flag"]
            .mean()
            .mul(100)
            .unstack("hour"))
hourly = hourly.reindex(day_order)

fig, ax = plt.subplots(figsize=(14, 4))
fig.patch.set_facecolor(LIGHT_BG)
sns.heatmap(hourly, cmap="RdYlGn", vmin=88, vmax=97, linewidths=0.3,
            linecolor="white", annot=False, ax=ax,
            cbar_kws={"label": "Success Rate (%)", "shrink": 0.8})
style_axis(ax, "Hourly Success Rate Heatmap (Day × Hour)", "Hour of Day", "Day of Week")
ax.set_xticklabels([f"{h:02d}:00" if h % 3 == 0 else "" for h in range(24)],
                   rotation=45, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/05_hourly_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 5 saved: hourly heatmap")

# ─── Chart 6 : Weekly SR Trend ───────────────────────────────────────────────
weekly = (df.groupby("week")["success_flag"]
            .agg(["mean","count"])
            .assign(sr=lambda x: x["mean"]*100))

fig, ax = plt.subplots(figsize=(13, 4))
fig.patch.set_facecolor(LIGHT_BG)
ax.plot(weekly.index, weekly["sr"], color=PHONEPE_PURPLE,
        linewidth=2, marker="o", markersize=3, label="Weekly SR")
ax.fill_between(weekly.index, weekly["sr"], alpha=0.12, color=PHONEPE_PURPLE)
ax.axhline(overall_sr, color=FAIL_RED, linestyle="--", linewidth=1.2,
           label=f"Annual avg: {overall_sr:.1f}%")
# Annotate notable dips
dip_weeks = weekly[weekly["sr"] < weekly["sr"].quantile(0.10)]
for w, row in dip_weeks.iterrows():
    ax.annotate(f"W{w}\n{row['sr']:.1f}%",
                xy=(w, row["sr"]), xytext=(w+0.5, row["sr"]-0.4),
                fontsize=7, color=FAIL_RED, arrowprops=dict(arrowstyle="-", color=FAIL_RED))
style_axis(ax, "Weekly Transaction Success Rate Trend (Jan–Dec 2024)",
           "Week Number", "Success Rate (%)")
ax.set_ylim(88, 97)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/06_weekly_trend.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 6 saved: weekly trend")

# ─── Chart 7 : Top Merchant SR (bottom 10 = problem areas) ──────────────────
merch_sr = (df.groupby("merchant")["success_flag"]
              .agg(["sum","count"])
              .assign(sr=lambda x: x["sum"]/x["count"]*100)
              .sort_values("sr"))

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(LIGHT_BG)
colors = [FAIL_RED if v < 91 else WARN_ORANGE if v < 93 else SUCCESS_GREEN
          for v in merch_sr["sr"]]
bars = ax.barh(merch_sr.index, merch_sr["sr"], color=colors,
               edgecolor="white", height=0.55)
ax.axvline(overall_sr, color=PHONEPE_PURPLE, linewidth=1.8, linestyle="--",
           label=f"Overall SR: {overall_sr:.1f}%")
for bar, val in zip(bars, merch_sr["sr"]):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=9)
style_axis(ax, "Merchant-wise Transaction Success Rate",
           "Success Rate (%)", "Merchant")
ax.set_xlim(84, 100)
ax.legend(fontsize=9)
p1 = mpatches.Patch(color=FAIL_RED, label="Critical (<91%)")
p2 = mpatches.Patch(color=WARN_ORANGE, label="Watch (91-93%)")
p3 = mpatches.Patch(color=SUCCESS_GREEN, label="Healthy (≥93%)")
ax.legend(handles=[p1, p2, p3], fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/07_merchant_sr.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart 7 saved: merchant SR")

# ─── Summary Table ───────────────────────────────────────────────────────────
print("\n─── Bank SR Summary ───")
print(bank_sr[["sum","count","sr"]].rename(columns={"sum":"Success","count":"Total","sr":"SR%"}).to_string())
print("\n─── Category SR Summary ───")
print(cat_sr[["sum","count","sr"]].rename(columns={"sum":"Success","count":"Total","sr":"SR%"}).to_string())
print("\n─── Platform SR Summary ───")
print(plt_sr[["sum","count","sr"]].rename(columns={"sum":"Success","count":"Total","sr":"SR%"}).to_string())
print("\n✅ All charts saved to /tmp/upi_project/charts/")
