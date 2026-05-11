# %% [markdown]
# # 01 · Exploratory Data Analysis (EDA)
# **Proyecto:** Superstore Sales Analysis  
# **Dataset:** Superstore Sales (sintético, estructura idéntica a Kaggle)  
# **Objetivo:** Entender la estructura, calidad y distribución del dataset antes de cualquier análisis.
import math
# %%
import sys, os

import ax

if "__file__" in globals():
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
else:
    sys.path.append("..")
from matplotlib.ticker import FuncFormatter
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from src.utils import load_data, validate_data, print_validation_report, set_style, save_fig

set_style()

# %% [markdown]
# ## 1. Carga y vista general

# %%
df = load_data()

print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes}")
df.head()

# %%
df.describe(include="all").T

# %% [markdown]
# ## 2. Data Quality Check
# > **Nota:** Como QA Engineer, el primer paso es siempre validar la calidad del dato.

# %%
report = validate_data(df)
print_validation_report(report)

# %% [markdown]
# ## 3. Distribución de variables numéricas

# %%
set_style()
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Distribución de Variables Numéricas", fontsize=16, fontweight="bold", y=1.01)

num_cols = [("Sales", "steelblue"), ("Profit", "seagreen"),
            ("Quantity", "darkorange"), ("Discount", "orchid")]

for ax, (col, color) in zip(axes.flatten(), num_cols):
    data = df[col]
    sns.histplot(data, ax=ax, color=color, bins=40, kde=True, alpha=0.75)
    ax.axvline(data.mean(),   color="red",    linestyle="--", linewidth=1.5, label=f"Mean: {data.mean():.2f}")
    ax.axvline(data.median(), color="navy",   linestyle=":",  linewidth=1.5, label=f"Median: {data.median():.2f}")
    ax.set_title(f"Distribution of {col}")
    ax.set_xlabel(col)
    ax.legend(fontsize=9)

plt.tight_layout()
save_fig(fig, "01_numeric_distributions")
plt.show()

# %% [markdown]
# **Observaciones:**
# - **Sales** tiene una distribución fuertemente sesgada a la derecha (outliers en tickets altos).
# - **Profit** muestra valores negativos → órdenes con pérdida, muy probablemente por descuentos altos.
# - **Discount** concentrado en 0 y múltiplos de 10% (política de descuentos estandarizada).

# %% [markdown]
# ## 4. Variables categóricas

# %%
set_style()
cat_cols = ["Category", "Sub-Category", "Segment", "Region", "Ship Mode"]
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Distribución de Variables Categóricas", fontsize=16, fontweight="bold")

for ax, col in zip(axes.flatten(), cat_cols):
    counts = df[col].value_counts()
    bars = sns.barplot(x=counts.values, y=counts.index, ax=ax,
                       palette="Set2", orient="h")
    # Etiquetas de valor
    for bar in bars.patches:
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                f"{int(bar.get_width()):,}", va="center", fontsize=9)
    ax.set_title(f"{col} — Count")
    ax.set_xlabel("Count")
    ax.set_ylabel("")

fig, axes = plt.subplots(
    nrows=math.ceil(len(cat_cols)/3), ncols=3, figsize=(18, 10)
)

plt.tight_layout()
save_fig(fig, "02_categorical_distributions")
plt.show()

# %% [markdown]
# ## 5. Análisis temporal — ¿cuándo se vende más?

# %%
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df["Ship Date"]  = pd.to_datetime(df["Ship Date"], errors="coerce")

monthly = (
    df.groupby(["Year", "Month"])["Sales"]
    .sum()
    .reset_index()
)
monthly["Period"] = pd.to_datetime(
    monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
)

# %%
set_style()
fig, ax = plt.subplots(figsize=(16, 5))

for year, grp in monthly.groupby("Year"):
    ax.plot(grp["Period"], grp["Sales"], marker="o", linewidth=2,
            label=str(year), alpha=0.85)
    # Sombreado bajo la curva
    ax.fill_between(grp["Period"], grp["Sales"], alpha=0.07)

ax.set_title("Monthly Sales Trend by Year", fontsize=15, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (USD)")
ax.yaxis.set_major_formatter((lambda x, _: f"${x:,.0f}"))
ax.legend(title="Year")
plt.tight_layout()
save_fig(fig, "03_monthly_sales_trend")
plt.show()

# %% [markdown]
# ## 6. Matriz de correlación

# %%
set_style()
corr = df[["Sales", "Profit", "Quantity", "Discount"]].corr()

fig, ax = plt.subplots(figsize=(7, 5))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, annot=True, fmt=".3f", cmap="RdYlGn",
    mask=mask, ax=ax, linewidths=0.5,
    vmin=-1, vmax=1, center=0,
    annot_kws={"size": 12}
)
ax.set_title("Correlation Matrix", fontsize=14, fontweight="bold")
plt.tight_layout()
save_fig(fig, "04_correlation_matrix")
plt.show()

# %% [markdown]
# **Key insight:** Correlación negativa entre `Discount` y `Profit` (≈ -0.22).  
# A mayor descuento aplicado, menor ganancia — confirmando la hipótesis del negocio.

# %% [markdown]
# ## 7. Shipping time analysis

# %%
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

set_style()
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribución por modo de envío
sns.boxplot(data=df, x="Ship Mode", y="Ship Days",
            palette="Set2", ax=axes[0], order=df.groupby("Ship Mode")["Ship Days"].median().sort_values().index)
axes[0].set_title("Shipping Days by Ship Mode")
axes[0].set_xlabel("")

# Conteo por ship mode
ship_counts = df["Ship Mode"].value_counts()
axes[1].pie(ship_counts, labels=ship_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette("Set2"), startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2})
axes[1].set_title("Ship Mode Distribution")

plt.suptitle("Shipping Analysis", fontsize=15, fontweight="bold")
plt.tight_layout()
save_fig(fig, "05_shipping_analysis")
plt.show()

print("\n📦 Average shipping days by mode:")
print(df.groupby("Ship Mode")["Ship Days"].mean().round(1).sort_values())
