"""
src/utils.py
Funciones reutilizables para el análisis de ventas.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from pandas.io.parsers import TextFileReader

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).resolve().parents[1]
DATA_RAW     = ROOT / "data" / "raw" / "superstore_sales.csv"
FIGURES_DIR  = ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Estilo global ─────────────────────────────────────────────────────────────
PALETTE   = "Set2"
BG_COLOR  = "#F8F9FA"
GRID_COLOR = "#E0E0E0"

def set_style():
    """Aplica estilo consistente a todos los plots."""
    sns.set_theme(style="whitegrid", palette=PALETTE)
    plt.rcParams.update({
        "figure.facecolor": BG_COLOR,
        "axes.facecolor":   BG_COLOR,
        "axes.grid":        True,
        "grid.color":       GRID_COLOR,
        "axes.spines.top":  False,
        "axes.spines.right":False,
        "font.family":      "DejaVu Sans",
        "axes.titlesize":   14,
        "axes.labelsize":   12,
    })

# ── Carga y validación ────────────────────────────────────────────────────────

def load_data(path: Path = DATA_RAW) -> TextFileReader | DataFrame:
    """Carga el dataset y castea tipos."""
    df = pd.read_csv(path, parse_dates=["Order Date", "Ship Date"])
    return df


def validate_data(df: pd.DataFrame) -> dict:
    """
    Retorna un dict con un resumen de calidad del dataset.
    Útil para demostrar mindset QA en entrevistas.
    """
    report = {
        "shape":           df.shape,
        "nulls":           df.isnull().sum().to_dict(),
        "duplicates":      df.duplicated().sum(),
        "dtypes":          df.dtypes.astype(str).to_dict(),
        "negative_sales":  (df["Sales"] < 0).sum(),
        "negative_profit": (df["Profit"] < 0).sum(),
        "date_range":      (df["Order Date"].min(), df["Order Date"].max()),
    }
    return report


def print_validation_report(report: dict):
    print("=" * 55)
    print("  DATA QUALITY REPORT")
    print("=" * 55)
    print(f"  Shape:            {report['shape'][0]:,} rows × {report['shape'][1]} cols")
    print(f"  Duplicates:       {report['duplicates']}")
    print(f"  Negative Sales:   {report['negative_sales']}")
    print(f"  Negative Profit:  {report['negative_profit']}")
    print(f"  Date range:       {report['date_range'][0].date()} → {report['date_range'][1].date()}")
    total_nulls = sum(report["nulls"].values())
    print(f"  Total nulls:      {total_nulls}")
    if total_nulls > 0:
        nulls = {k: v for k, v in report["nulls"].items() if v > 0}
        for col, n in nulls.items():
            print(f"    └─ {col}: {n}")
    print("=" * 55)

# ── KPIs ──────────────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """Calcula los KPIs principales del negocio."""
    return {
        "total_sales":      df["Sales"].sum(),
        "total_profit":     df["Profit"].sum(),
        "profit_margin":    df["Profit"].sum() / df["Sales"].sum() * 100,
        "total_orders":     df["Order ID"].nunique(),
        "avg_order_value":  df.groupby("Order ID")["Sales"].sum().mean(),
        "total_customers":  df["Customer ID"].nunique(),
        "avg_discount":     df["Discount"].mean() * 100,
        "orders_at_loss":   (df.groupby("Order ID")["Profit"].sum() < 0).sum(),
    }


def print_kpis(kpis: dict):
    print("\n" + "=" * 55)
    print("  BUSINESS KPIs")
    print("=" * 55)
    print(f"  💰 Total Sales:         ${kpis['total_sales']:>12,.2f}")
    print(f"  📈 Total Profit:        ${kpis['total_profit']:>12,.2f}")
    print(f"  📊 Profit Margin:        {kpis['profit_margin']:>11.2f}%")
    print(f"  🛒 Total Orders:         {kpis['total_orders']:>12,}")
    print(f"  💵 Avg Order Value:     ${kpis['avg_order_value']:>12,.2f}")
    print(f"  👥 Unique Customers:     {kpis['total_customers']:>12,}")
    print(f"  🏷️  Avg Discount:         {kpis['avg_discount']:>11.2f}%")
    print(f"  🔴 Orders at Loss:       {kpis['orders_at_loss']:>12,}")
    print("=" * 55)

# ── Helpers de plots ──────────────────────────────────────────────────────────

def fmt_millions(x, pos=None):
    """Formatter para ejes en millones."""
    return f"${x/1e6:.1f}M" if abs(x) >= 1e6 else f"${x:,.0f}"


def save_fig(fig: plt.Figure, name: str):
    """Guarda la figura en reports/figures/."""
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    print(f"  💾 Saved → {path.relative_to(ROOT)}")
