# %% [markdown]
# # 02 · KPIs & Business Analysis
# **Objetivo:** Calcular los KPIs clave del negocio y analizar performance por categoría,
# segmento, región y producto.

# %%
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from src.utils import (load_data, compute_kpis, print_kpis,
                        set_style, save_fig)

set_style()
df = load_data()
df["Year"]    = df["Order Date"].dt.year
df["Month"]   = df["Order Date"].dt.month
df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)

# %% [markdown]
# ## 1. KPIs Generales

# %%
kpis = compute_kpis(df)
print_kpis(kpis)

# %% [markdown]
# ### KPI Dashboard visual

# %%
set_style()
fig = plt.figure(figsize=(16, 4))
fig.suptitle("📊  Executive KPI Dashboard", fontsize=18, fontweight="bold", y=1.05)

kpi_data = [
    ("Total Sales",     f"${kpis['total_sales']:,.0f}",        "#4C9BE8"),
    ("Total Profit",    f"${kpis['total_profit']:,.0f}",        "#52C47A"),
    ("Profit Margin",   f"{kpis['profit_margin']:.1f}%",        "#F7A440"),
    ("Total Orders",    f"{kpis['total_orders']:,}",            "#A084DC"),
    ("Avg Order Value", f"${kpis['avg_order_value']:,.0f}",     "#F26B6B"),
    ("Customers",       f"{kpis['total_customers']:,}",         "#4BC8C8"),
]

for i, (label, value, color) in enumerate(kpi_data):
    ax = fig.add_subplot(1, 6, i + 1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # Card background
    rect = mpatches.FancyBboxPatch(
        (0.05, 0.1), 0.9, 0.85,
        boxstyle="round,pad=0.05",
        linewidth=2, edgecolor=color,
        facecolor=color + "22"  # color con transparencia hex
    )
    ax.add_patch(rect)
    ax.text(0.5, 0.68, value,  ha="center", va="center", fontsize=15,
            fontweight="bold", color=color)
    ax.text(0.5, 0.28, label,  ha="center", va="center", fontsize=9,
            color="#555555", wrap=True)

plt.tight_layout()
save_fig(fig, "06_kpi_dashboard")
plt.show()

# %% [markdown]
# ## 2. Sales & Profit por Categoría

# %%
cat_agg = (
    df.groupby("Category")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
    .assign(Margin=lambda x: x["Profit"] / x["Sales"] * 100)
    .sort_values("Sales", ascending=False)
    .reset_index()
)
print(cat_agg.to_string(index=False))

# %%
set_style()
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle("Performance by Category", fontsize=15, fontweight="bold")

colors = sns.color_palette("Set2", 3)

# Sales
sns.barplot(data=cat_agg, x="Category", y="Sales", palette="Set2", ax=axes[0])
axes[0].set_title("Total Sales")
axes[0].set_ylabel("USD")
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar in axes[0].patches:
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                 f"${bar.get_height():,.0f}", ha="center", fontsize=9, fontweight="bold")

# Profit
colors_profit = ["#52C47A" if p > 0 else "#F26B6B" for p in cat_agg["Profit"]]
sns.barplot(data=cat_agg, x="Category", y="Profit", palette=colors_profit, ax=axes[1])
axes[1].set_title("Total Profit")
axes[1].set_ylabel("USD")
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
axes[1].axhline(0, color="gray", linewidth=0.8, linestyle="--")

# Profit Margin
bars = sns.barplot(data=cat_agg, x="Category", y="Margin", palette="Set2", ax=axes[2])
axes[2].set_title("Profit Margin %")
axes[2].set_ylabel("%")
axes[2].axhline(0, color="gray", linewidth=0.8, linestyle="--")
for bar in axes[2].patches:
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"{bar.get_height():.1f}%", ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
save_fig(fig, "07_category_performance")
plt.show()

# %% [markdown]
# ## 3. Sub-Category — Sales vs Profit Scatter

# %%
subcat_agg = (
    df.groupby(["Category", "Sub-Category"])
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
         Quantity=("Quantity", "sum"))
    .reset_index()
)

set_style()
fig, ax = plt.subplots(figsize=(13, 7))

palette = {"Technology": "#4C9BE8", "Furniture": "#F7A440", "Office Supplies": "#52C47A"}

for cat, grp in subcat_agg.groupby("Category"):
    sc = ax.scatter(grp["Sales"], grp["Profit"],
                    s=grp["Quantity"] * 1.5,
                    color=palette[cat], alpha=0.8, label=cat,
                    edgecolors="white", linewidth=0.8)
    for _, row in grp.iterrows():
        ax.annotate(row["Sub-Category"], (row["Sales"], row["Profit"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

ax.axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.5)
ax.axvline(subcat_agg["Sales"].mean(), color="gray", linestyle=":", linewidth=1, alpha=0.5)
ax.set_title("Sub-Category: Sales vs Profit\n(bubble size = total quantity)", fontsize=14, fontweight="bold")
ax.set_xlabel("Total Sales (USD)")
ax.set_ylabel("Total Profit (USD)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(title="Category", fontsize=10)
plt.tight_layout()
save_fig(fig, "08_subcategory_scatter")
plt.show()

# %% [markdown]
# ## 4. Regional Performance

# %%
region_agg = (
    df.groupby("Region")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
         Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"))
    .assign(Margin=lambda x: x["Profit"] / x["Sales"] * 100)
    .sort_values("Sales", ascending=False)
    .reset_index()
)

set_style()
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Regional Performance", fontsize=15, fontweight="bold")

# Sales por región
sns.barplot(data=region_agg, x="Region", y="Sales", palette="Blues_d",
            order=region_agg["Region"], ax=axes[0])
axes[0].set_title("Sales by Region")
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar in axes[0].patches:
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                 f"${bar.get_height():,.0f}", ha="center", fontsize=9, fontweight="bold")

# Margin por región
color_margin = ["#52C47A" if m > 0 else "#F26B6B" for m in region_agg["Margin"]]
sns.barplot(data=region_agg, x="Region", y="Margin", palette=color_margin,
            order=region_agg["Region"], ax=axes[1])
axes[1].set_title("Profit Margin % by Region")
axes[1].set_ylabel("Margin %")
axes[1].axhline(0, color="gray", linestyle="--")
for bar in axes[1].patches:
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 f"{bar.get_height():.1f}%", ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
save_fig(fig, "09_regional_performance")
plt.show()

print("\n🗺️  Regional summary:")
print(region_agg.to_string(index=False))

# %% [markdown]
# ## 5. Segment Analysis

# %%
seg_agg = (
    df.groupby("Segment")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
         Orders=("Order ID", "nunique"))
    .assign(Margin=lambda x: x["Profit"] / x["Sales"] * 100,
            Avg_Order=lambda x: x["Sales"] / x["Orders"])
    .reset_index()
)

set_style()
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Customer Segment Analysis", fontsize=15, fontweight="bold")

# Donut chart de sales
wedges, texts, autotexts = axes[0].pie(
    seg_agg["Sales"], labels=seg_agg["Segment"],
    autopct="%1.1f%%", startangle=90,
    colors=sns.color_palette("Set2"),
    wedgeprops={"edgecolor": "white", "linewidth": 3, "width": 0.6}
)
axes[0].set_title("Sales Share by Segment")
for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_fontweight("bold")

# Avg order value por segmento
sns.barplot(data=seg_agg, x="Segment", y="Avg_Order", palette="Set2", ax=axes[1])
axes[1].set_title("Avg Order Value by Segment")
axes[1].set_ylabel("USD")
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar in axes[1].patches:
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f"${bar.get_height():,.0f}", ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
save_fig(fig, "10_segment_analysis")
plt.show()

# %% [markdown]
# ## 6. Top 10 Products

# %%
top_products = (
    df.groupby("Product Name")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "count"))
    .nlargest(10, "Sales")
    .reset_index()
)

set_style()
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Top 10 Products", fontsize=15, fontweight="bold")

# Por ventas
sns.barplot(data=top_products, y="Product Name", x="Sales", palette="Blues_r",
            orient="h", ax=axes[0])
axes[0].set_title("by Sales")
axes[0].set_xlabel("USD")
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Por profit
colors_p = ["#52C47A" if p > 0 else "#F26B6B" for p in top_products["Profit"]]
sns.barplot(data=top_products, y="Product Name", x="Profit", palette=colors_p,
            orient="h", ax=axes[1])
axes[1].set_title("by Profit")
axes[1].set_xlabel("USD")
axes[1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
axes[1].axvline(0, color="gray", linewidth=1, linestyle="--")

plt.tight_layout()
save_fig(fig, "11_top_products")
plt.show()

# %% [markdown]
# ## 7. Quarterly YoY Growth

# %%
quarterly = (
    df.groupby(["Year", "Quarter"])["Sales"]
    .sum()
    .reset_index()
    .pivot(index="Quarter", columns="Year", values="Sales")
    .fillna(0)
)

# YoY growth %
if len(quarterly.columns) >= 2:
    years = sorted(quarterly.columns)
    for i in range(1, len(years)):
        quarterly[f"YoY_{years[i]}"] = (
            (quarterly[years[i]] - quarterly[years[i-1]]) / quarterly[years[i-1]] * 100
        ).replace([np.inf, -np.inf], np.nan)

print("\n📅 Quarterly Sales & YoY Growth:")
print(quarterly.round(1).to_string())
