# %% [markdown]
# # 04 · Advanced Insights
# **Proyecto:** Superstore Sales Analysis
# **Objetivo:** Análisis avanzado con cuatro ángulos complementarios a los notebooks anteriores:
# 1. Product Portfolio Matrix (BCG-style) — clasificar sub-categorías por revenue vs margen
# 2. Pareto / 80-20 — qué % de clientes genera el 80% del revenue
# 3. State Performance Deep-Dive — revenue vs margen por estado (top 15)
# 4. Shipping Mode Profitability — rentabilidad real por modo de envío

# %%
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from src.utils import load_data, set_style, save_fig

set_style()
df = load_data()
df["Year"]  = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month

# %% [markdown]
# ---
# ## 1. Product Portfolio Matrix (BCG-style)
#
# Clasifica cada sub-categoría en cuadrantes según:
# - Eje X: Revenue total (tamaño de negocio)
# - Eje Y: Profit Margin % (rentabilidad)
# - Tamaño del punto: cantidad de órdenes
#
# Cuadrantes:
# - ⭐ Stars       — Alto revenue, alto margen → prioridad máxima
# - 🐄 Cash Cows  — Bajo revenue, alto margen → excelentes pero pequeños
# - ❓ Question Marks — Alto revenue, bajo margen → revisar costos
# - 🐕 Dogs        — Bajo revenue, bajo margen → candidatos a revisar estrategia

# %%
subcat = (
    df.groupby(["Category", "Sub-Category"])
    .agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count"),
    )
    .assign(Margin=lambda x: x["Profit"] / x["Revenue"] * 100)
    .reset_index()
)

median_revenue = subcat["Revenue"].median()
median_margin  = subcat["Margin"].median()

def label_quadrant(row):
    high_rev = row["Revenue"] > median_revenue
    high_mar = row["Margin"]  > median_margin
    if   high_rev and high_mar:     return "Star"
    elif high_rev and not high_mar: return "Question Mark"
    elif not high_rev and high_mar: return "Cash Cow"
    else:                           return "Dog"

subcat["Quadrant"] = subcat.apply(label_quadrant, axis=1)

palette_q = {
    "Star":          "#52C47A",
    "Question Mark": "#F7A440",
    "Cash Cow":      "#4C9BE8",
    "Dog":           "#F26B6B",
}

set_style()
fig, ax = plt.subplots(figsize=(13, 8))

for q, grp in subcat.groupby("Quadrant"):
    ax.scatter(
        grp["Revenue"], grp["Margin"],
        s=grp["Orders"] * 3,
        color=palette_q[q], alpha=0.85,
        label=q, edgecolors="white", linewidth=0.8,
        zorder=3,
    )
    for _, row in grp.iterrows():
        ax.annotate(
            row["Sub-Category"],
            (row["Revenue"], row["Margin"]),
            textcoords="offset points", xytext=(7, 3),
            fontsize=8.5, fontweight="bold",
        )

# Líneas de cuadrante
ax.axvline(median_revenue, color="gray", linestyle="--", linewidth=1, alpha=0.6)
ax.axhline(median_margin,  color="gray", linestyle="--", linewidth=1, alpha=0.6)
ax.axhline(0, color="red", linestyle="-", linewidth=1.2, alpha=0.4)

# Labels de cuadrantes
ax.text(subcat["Revenue"].max() * 0.97, subcat["Margin"].max() * 0.95,
        "STARS", ha="right", fontsize=9, color="#52C47A", alpha=0.7, fontweight="bold")
ax.text(subcat["Revenue"].max() * 0.97, subcat["Margin"].min() * 0.8,
        "QUESTION MARKS", ha="right", fontsize=9, color="#F7A440", alpha=0.7, fontweight="bold")
ax.text(median_revenue * 0.05, subcat["Margin"].max() * 0.95,
        "CASH COWS", ha="left", fontsize=9, color="#4C9BE8", alpha=0.7, fontweight="bold")
ax.text(median_revenue * 0.05, subcat["Margin"].min() * 0.8,
        "DOGS", ha="left", fontsize=9, color="#F26B6B", alpha=0.7, fontweight="bold")

ax.set_title("Product Portfolio Matrix\n(Revenue vs Profit Margin — bubble size = orders)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Total Revenue (USD)")
ax.set_ylabel("Profit Margin (%)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}%"))
ax.legend(title="Quadrant", fontsize=9, loc="lower right")
plt.tight_layout()
save_fig(fig, "15_product_portfolio_matrix")
plt.show()

print("\n📊 Product Portfolio Summary:")
print(subcat[["Sub-Category", "Category", "Revenue", "Margin", "Quadrant"]]
      .sort_values("Revenue", ascending=False)
      .to_string(index=False))

# %% [markdown]
# **Insights:**
# - Los productos en **❓ Question Mark** (alto revenue, bajo margen) son el mayor riesgo:
#   generan ventas pero consumen rentabilidad. Revisar política de descuentos aplicada.
# - Los **🐄 Cash Cows** son sub-categorías pequeñas pero altamente rentables —
#   excelentes para escalar con mínima inversión.
# - Los **🐕 Dogs** requieren análisis de si el problema es pricing, costo logístico o descuentos excesivos.

# %% [markdown]
# ---
# ## 2. Pareto Analysis — 80/20 de Revenue por Cliente
#
# ¿Cuántos clientes generan el 80% del revenue?
# Este análisis responde una pregunta crítica de retención: ¿dónde concentrar esfuerzo?

# %%
customer_rev = (
    df.groupby("Customer ID")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
customer_rev.columns = ["Customer ID", "Revenue"]
customer_rev["Cumulative Revenue"] = customer_rev["Revenue"].cumsum()
customer_rev["Cumulative %"]       = customer_rev["Cumulative Revenue"] / customer_rev["Revenue"].sum() * 100
customer_rev["Customer Rank %"]    = (np.arange(1, len(customer_rev) + 1) / len(customer_rev)) * 100

# ¿Qué % de clientes = 80% del revenue?
threshold_80 = customer_rev[customer_rev["Cumulative %"] >= 80].iloc[0]["Customer Rank %"]
n_top = int(np.ceil(threshold_80 / 100 * len(customer_rev)))

set_style()
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Pareto Analysis — Customer Revenue Concentration", fontsize=15, fontweight="bold")

# Curva de Lorenz / Pareto
ax = axes[0]
ax.plot(customer_rev["Customer Rank %"], customer_rev["Cumulative %"],
        color="#4C9BE8", linewidth=2.5, label="Cumulative Revenue %")
ax.fill_between(customer_rev["Customer Rank %"], customer_rev["Cumulative %"],
                alpha=0.12, color="#4C9BE8")
ax.axhline(80, color="#F26B6B", linestyle="--", linewidth=1.5, alpha=0.8, label="80% threshold")
ax.axvline(threshold_80, color="#F26B6B", linestyle="--", linewidth=1.5, alpha=0.8)
ax.plot([threshold_80], [80], "o", color="#F26B6B", markersize=9, zorder=5)
ax.annotate(
    f"  Top {threshold_80:.0f}% of customers\n  → 80% of revenue",
    (threshold_80, 80), xytext=(threshold_80 + 5, 65),
    fontsize=9, color="#F26B6B", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#F26B6B", lw=1.2),
)
ax.plot([0, 100], [0, 100], color="gray", linestyle=":", linewidth=1, alpha=0.5,
        label="Perfect equality line")
ax.set_xlabel("Cumulative % of Customers (ranked by revenue)")
ax.set_ylabel("Cumulative % of Revenue")
ax.set_title("Revenue Concentration Curve")
ax.legend(fontsize=9)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Top 20 clientes por revenue
ax2 = axes[1]
top20 = customer_rev.head(20).copy()
top20["Label"] = [f"C-{i+1}" for i in range(len(top20))]
bars = ax2.barh(top20["Label"][::-1], top20["Revenue"][::-1],
                color="#4C9BE8", edgecolor="white", alpha=0.85)
ax2.set_title(f"Top 20 Customers by Revenue")
ax2.set_xlabel("Total Revenue (USD)")
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar in bars:
    ax2.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
             f"${bar.get_width():,.0f}", va="center", fontsize=8)

plt.tight_layout()
save_fig(fig, "16_pareto_revenue")
plt.show()

print(f"\n📌 Pareto Finding:")
print(f"   → Top {threshold_80:.0f}% of customers ({n_top:,} customers) generate 80% of total revenue")
print(f"   → Total customers: {len(customer_rev):,}")
print(f"   → Top customer revenue: ${customer_rev['Revenue'].iloc[0]:,.2f}")
print(f"   → Avg customer revenue: ${customer_rev['Revenue'].mean():,.2f}")

# %% [markdown]
# **Insights:**
# - La curva de concentración confirma el **principio 80/20**: un porcentaje reducido de
#   clientes genera la gran mayoría del revenue.
# - Implicación directa: **retener a los top clientes tiene un ROI mucho mayor que adquirir nuevos**.
# - Segmentar los top N clientes para programas de fidelidad B2B (especialmente si son Corporate)
#   debería ser la prioridad #1 de marketing.

# %% [markdown]
# ---
# ## 3. State Performance Deep-Dive
#
# Revenue y profit margin por estado (top 15 por revenue).
# Identifica estados con alto revenue pero bajo margen (riesgo) y los que tienen
# potencial de crecimiento (revenue medio, margen alto).

# %%
state_agg = (
    df.groupby("State")
    .agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count"),
        Customers=("Customer ID", "nunique"),
    )
    .assign(Margin=lambda x: x["Profit"] / x["Revenue"] * 100)
    .sort_values("Revenue", ascending=False)
    .reset_index()
)

top15 = state_agg.head(15)
median_rev_state = top15["Revenue"].median()
median_mar_state = top15["Margin"].median()

set_style()
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("State Performance Deep-Dive (Top 15 by Revenue)", fontsize=15, fontweight="bold")

# --- Chart 1: Revenue vs Margin scatter ---
ax = axes[0]
colors_s = ["#52C47A" if m > median_mar_state else "#F26B6B" for m in top15["Margin"]]
sc = ax.scatter(top15["Revenue"], top15["Margin"],
                s=top15["Orders"] * 2.5, c=colors_s, alpha=0.8,
                edgecolors="white", linewidth=0.8, zorder=3)

# Líneas medianas
ax.axvline(median_rev_state, color="gray", linestyle="--", linewidth=1, alpha=0.5)
ax.axhline(median_mar_state, color="gray", linestyle="--", linewidth=1, alpha=0.5)
ax.axhline(0, color="red", linestyle="-", linewidth=1, alpha=0.35)

for _, row in top15.iterrows():
    ax.annotate(row["State"], (row["Revenue"], row["Margin"]),
                textcoords="offset points", xytext=(6, 3), fontsize=7.5)

ax.set_xlabel("Total Revenue (USD)")
ax.set_ylabel("Profit Margin (%)")
ax.set_title("Revenue vs Profit Margin by State\n(bubble size = orders)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}%"))

# Patch legend
high_patch = mpatches.Patch(color="#52C47A", label=f"Above median margin ({median_mar_state:.1f}%)")
low_patch  = mpatches.Patch(color="#F26B6B", label=f"Below median margin")
ax.legend(handles=[high_patch, low_patch], fontsize=8, loc="lower right")

# --- Chart 2: Stacked horizontal bar — Revenue with margin label ---
ax2 = axes[1]
top15_sorted = top15.sort_values("Revenue")
bar_colors = ["#52C47A" if m > 0 else "#F26B6B" for m in top15_sorted["Margin"]]
bars = ax2.barh(top15_sorted["State"], top15_sorted["Revenue"],
                color=bar_colors, edgecolor="white", alpha=0.85)

ax2.set_title("Revenue by State (color = margin sign)")
ax2.set_xlabel("Total Revenue (USD)")
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

for bar, (_, row) in zip(bars, top15_sorted.iterrows()):
    ax2.text(bar.get_width() + 500,
             bar.get_y() + bar.get_height() / 2,
             f"  {row['Margin']:.1f}%",
             va="center", fontsize=8, fontweight="bold",
             color="#52C47A" if row["Margin"] > 0 else "#F26B6B")

plt.tight_layout()
save_fig(fig, "17_state_performance")
plt.show()

print("\n🗺️  State Performance Summary (Top 15):")
print(state_agg.head(15)[["State", "Revenue", "Profit", "Margin", "Orders", "Customers"]]
      .round({"Revenue": 0, "Profit": 0, "Margin": 2})
      .to_string(index=False))

# %% [markdown]
# **Insights:**
# - Los estados en el cuadrante **alto revenue + bajo margen** merecen atención inmediata:
#   están generando volumen pero erosionando rentabilidad.
#   Primeras preguntas a responder: ¿hay más descuentos en esos estados? ¿costos logísticos más altos?
# - Los estados con **revenue medio + alto margen** son los candidatos ideales para invertir en
#   crecimiento — el modelo de negocio ya funciona bien ahí.

# %% [markdown]
# ---
# ## 4. Shipping Mode Profitability
#
# ¿Cuál es la rentabilidad real por modo de envío?
# Contrastar el assumption de que "mismo día = más caro = menos margen".

# %%
ship_agg = (
    df.groupby("Ship Mode")
    .agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count"),
        Avg_Discount=("Discount", "mean"),
        Avg_Sales=("Sales", "mean"),
    )
    .assign(Margin=lambda x: x["Profit"] / x["Revenue"] * 100)
    .reset_index()
)

order_map = {"Same Day": 0, "First Class": 1, "Second Class": 2, "Standard Class": 3}
ship_agg["_order"] = ship_agg["Ship Mode"].map(order_map)
ship_agg = ship_agg.sort_values("_order").drop("_order", axis=1)

set_style()
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Shipping Mode Profitability Analysis", fontsize=15, fontweight="bold")

palette_ship = ["#A084DC", "#4C9BE8", "#52C47A", "#F7A440"]

# Chart 1: Profit margin
bars = axes[0, 0].bar(ship_agg["Ship Mode"], ship_agg["Margin"],
                       color=palette_ship, edgecolor="white")
axes[0, 0].set_title("Profit Margin % by Ship Mode")
axes[0, 0].set_ylabel("Margin %")
axes[0, 0].axhline(ship_agg["Margin"].mean(), color="red", linestyle="--",
                   linewidth=1.2, alpha=0.6, label=f"Avg: {ship_agg['Margin'].mean():.1f}%")
axes[0, 0].legend(fontsize=8)
for bar, val in zip(bars, ship_agg["Margin"]):
    axes[0, 0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")

# Chart 2: Avg order value
bars2 = axes[0, 1].bar(ship_agg["Ship Mode"], ship_agg["Avg_Sales"],
                        color=palette_ship, edgecolor="white")
axes[0, 1].set_title("Avg Order Value by Ship Mode")
axes[0, 1].set_ylabel("USD")
axes[0, 1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar, val in zip(bars2, ship_agg["Avg_Sales"]):
    axes[0, 1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    f"${val:,.0f}", ha="center", fontsize=10, fontweight="bold")

# Chart 3: Avg discount
bars3 = axes[1, 0].bar(ship_agg["Ship Mode"], ship_agg["Avg_Discount"] * 100,
                        color=palette_ship, edgecolor="white")
axes[1, 0].set_title("Avg Discount % by Ship Mode")
axes[1, 0].set_ylabel("Discount %")
for bar, val in zip(bars3, ship_agg["Avg_Discount"] * 100):
    axes[1, 0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")

# Chart 4: Volume (orders)
bars4 = axes[1, 1].bar(ship_agg["Ship Mode"], ship_agg["Orders"],
                        color=palette_ship, edgecolor="white")
axes[1, 1].set_title("Order Volume by Ship Mode")
axes[1, 1].set_ylabel("# Orders")
for bar, val in zip(bars4, ship_agg["Orders"]):
    axes[1, 1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    f"{val:,}", ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
save_fig(fig, "18_ship_mode_profitability")
plt.show()

print("\n🚚 Shipping Mode Summary:")
print(ship_agg[["Ship Mode", "Revenue", "Margin", "Avg_Sales", "Avg_Discount", "Orders"]]
      .rename(columns={"Avg_Discount": "Avg Discount", "Avg_Sales": "Avg Order $"})
      .round({"Revenue": 0, "Margin": 2, "Avg Order $": 2, "Avg Discount": 3})
      .to_string(index=False))

# %% [markdown]
# **Insights:**
# - Si **Same Day** y **First Class** muestran márgenes iguales o superiores a Standard Class,
#   el costo del envío rápido está siendo compensado por clientes que aplican menos descuentos.
#   Esto sugiere que los clientes urgentes son más rentables por orden.
# - **Standard Class** tiene el mayor volumen pero no necesariamente el mejor margen —
#   es el caballo de batalla del negocio, no su motor de rentabilidad.
# - Acción recomendada: incentivar upgrades a First Class para clientes Corporate
#   (mejor experiencia + mayor margen para el negocio = win-win).

# %% [markdown]
# ---
# ## Resumen del Notebook
#
# | Análisis | Hallazgo clave |
# |----------|----------------|
# | Portfolio Matrix | Identifica Stars, Cash Cows, Question Marks y Dogs por sub-categoría |
# | Pareto 80/20 | Un % reducido de clientes genera la mayoría del revenue |
# | State Deep-Dive | Varios estados top tienen revenue alto pero margen bajo |
# | Ship Mode Profitability | Los modos premium pueden tener mejor margen que Standard |