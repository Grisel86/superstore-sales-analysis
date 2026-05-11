# %% [markdown]
# # 03 · Discount Impact & Advanced Insights
# **Objetivo:** Analizar el impacto de los descuentos en la rentabilidad,
# identificar patrones de pérdida y generar recomendaciones de negocio accionables.

# %%
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402
from scipy import stats  # noqa: E402

from src.utils import load_data, set_style, save_fig

set_style()
df = load_data()
df["Year"]  = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month

# %% [markdown]
# ## 1. Impacto del Descuento en el Profit

# %%
set_style()
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Discount Impact on Profitability", fontsize=15, fontweight="bold")

# Scatter: discount vs profit
colors = ["#52C47A" if p > 0 else "#F26B6B" for p in df["Profit"]]
axes[0].scatter(df["Discount"], df["Profit"], alpha=0.25, c=colors, s=15)

# Línea de regresión
m, b, r, p, se = stats.linregress(df["Discount"], df["Profit"])
x_line = np.linspace(0, df["Discount"].max(), 100)
axes[0].plot(x_line, m * x_line + b, color="navy", linewidth=2,
             label=f"Trend (r={r:.2f})")
axes[0].axhline(0, color="gray", linestyle="--", linewidth=1)
axes[0].set_xlabel("Discount Rate")
axes[0].set_ylabel("Profit (USD)")
axes[0].set_title("Discount vs Profit per Transaction")
axes[0].legend()

# Profit medio por nivel de descuento
disc_bins = pd.cut(df["Discount"],
                   bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.6],
                   labels=["0%", "1-10%", "11-20%", "21-30%", "31-40%", ">40%"])
disc_agg = df.groupby(disc_bins, observed=False)["Profit"].mean().reset_index()
disc_agg.columns = ["Discount Range", "Avg Profit"]

color_bars = ["#52C47A" if p > 0 else "#F26B6B" for p in disc_agg["Avg Profit"]]
bars = axes[1].bar(disc_agg["Discount Range"], disc_agg["Avg Profit"], color=color_bars, edgecolor="white")
axes[1].axhline(0, color="gray", linestyle="--", linewidth=1)
axes[1].set_title("Avg Profit by Discount Range")
axes[1].set_xlabel("Discount Range")
axes[1].set_ylabel("Avg Profit (USD)")
for bar in bars:
    h = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width()/2,
                 h + (2 if h >= 0 else -8),
                 f"${h:.1f}", ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
save_fig(fig, "12_discount_impact")
plt.show()

print(f"\n📉 Correlación Discount vs Profit: {df['Discount'].corr(df['Profit']):.3f}")
print(f"   → A cada +10% de descuento, el profit promedio cambia en: ${m*0.1:+.2f}")

# %% [markdown]
# ## 2. Órdenes con Pérdida — ¿Dónde pierde dinero el negocio?

# %%
loss_df = df[df["Profit"] < 0].copy()

print(f"🔴 Órdenes con pérdida: {len(loss_df):,}  ({len(loss_df)/len(df)*100:.1f}% del total)")
print(f"   Total pérdida acumulada: ${loss_df['Profit'].sum():,.2f}")

set_style()
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle("Loss Analysis — Where Is the Business Losing Money?",
             fontsize=14, fontweight="bold")

# Por categoría
loss_cat = loss_df.groupby("Category")["Profit"].sum().sort_values()
colors_l = ["#F26B6B" if p < 0 else "#52C47A" for p in loss_cat]
loss_cat.plot(kind="barh", color=colors_l, ax=axes[0])
axes[0].set_title("Total Loss by Category")
axes[0].set_xlabel("Profit (USD)")
axes[0].axvline(0, color="gray", linewidth=1)
for bar in axes[0].patches:
    axes[0].text(bar.get_width() - 200, bar.get_y() + bar.get_height()/2,
                 f"${bar.get_width():,.0f}", va="center", fontsize=9, color="white", fontweight="bold")

# Por región
loss_reg = loss_df.groupby("Region")["Profit"].sum().sort_values()
loss_reg.plot(kind="barh", color="#F26B6B", ax=axes[1])
axes[1].set_title("Total Loss by Region")
axes[1].set_xlabel("Profit (USD)")

# Distribución del descuento en órdenes con pérdida vs ganancia
sns.kdeplot(df[df["Profit"] >= 0]["Discount"], ax=axes[2],
            label="Profitable", color="#52C47A", fill=True, alpha=0.4)
sns.kdeplot(df[df["Profit"] < 0]["Discount"], ax=axes[2],
            label="At Loss", color="#F26B6B", fill=True, alpha=0.4)
axes[2].set_title("Discount Distribution:\nProfit vs Loss Orders")
axes[2].set_xlabel("Discount Rate")
axes[2].legend()

plt.tight_layout()
save_fig(fig, "13_loss_analysis")
plt.show()

# %% [markdown]
# ## 3. Cohort Analysis — Retención de Clientes

# %%
# Primera compra de cada cliente
first_order = df.groupby("Customer ID")["Order Date"].min().reset_index()
first_order.columns = ["Customer ID", "Cohort Date"]
first_order["Cohort"] = first_order["Cohort Date"].dt.to_period("Q").astype(str)

df_cohort = df.merge(first_order[["Customer ID", "Cohort"]], on="Customer ID")
df_cohort["Order Quarter"] = df_cohort["Order Date"].dt.to_period("Q").astype(str)

cohort_data = (
    df_cohort.groupby(["Cohort", "Order Quarter"])["Customer ID"]
    .nunique()
    .reset_index()
)

# Pivot
cohort_pivot = cohort_data.pivot(index="Cohort", columns="Order Quarter", values="Customer ID").fillna(0)
# Normalizar por tamaño de cohort
cohort_size  = cohort_pivot.iloc[:, 0]
cohort_pct   = cohort_pivot.divide(cohort_size, axis=0) * 100

set_style()
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(cohort_pct, annot=True, fmt=".0f", cmap="YlGnBu",
            ax=ax, linewidths=0.4, cbar_kws={"label": "% of Cohort Active"})
ax.set_title("Customer Retention by Cohort (Quarterly)", fontsize=14, fontweight="bold")
ax.set_xlabel("Order Quarter")
ax.set_ylabel("Acquisition Cohort")
plt.tight_layout()
save_fig(fig, "14_cohort_retention")
plt.show()

# %% [markdown]
# ## 4. Business Recommendations

# %%
print("""
╔══════════════════════════════════════════════════════════════════╗
║           BUSINESS RECOMMENDATIONS — SUPERSTORE SALES           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  1. 🏷️  DISCOUNT POLICY                                          ║
║     Descuentos >30% generan pérdidas consistentes.               ║
║     Recomendación: limitar descuentos a máx 20% en Technology    ║
║     y Furniture, donde el margen base ya es ajustado.            ║
║                                                                  ║
║  2. 📦 FURNITURE PROFITABILITY                                   ║
║     Es la categoría con menor margen. Revisar costos de          ║
║     logística (peso/volumen) y política de precios.              ║
║                                                                  ║
║  3. 🗺️  REGIONAL OPPORTUNITY                                     ║
║     Identificar regiones con alto volumen de ventas pero         ║
║     bajo margen: oportunidad de optimización de costos.          ║
║                                                                  ║
║  4. 👥 CORPORATE SEGMENT                                         ║
║     Mayor valor de ticket promedio. Invertir en retención        ║
║     y programas de fidelidad B2B.                                ║
║                                                                  ║
║  5. 📅 SEASONALITY                                               ║
║     Aprovechar picos trimestrales con campañas proactivas.        ║
║     Preparar stock y logística para Q4.                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")