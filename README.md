# 📊 Superstore Sales Analysis

**End-to-end Exploratory Data Analysis and Business Intelligence project**  
simulating a real-world retail analytics scenario.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-0.12%2B-4C9BE8)
![SciPy](https://img.shields.io/badge/SciPy-1.11%2B-8CAAE6?logo=scipy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🗂️ Business Problem

A retail company with 3 years of transactional data needs to understand:

- 💰 **Where** is the business generating — and losing — profit?
- 🏷️ **What** is the true impact of discounts on the bottom line?
- 👥 **Who** are the most valuable customer segments, and how do they behave over time?
- 📅 **When** do sales peaks occur, and how can the business leverage them?
- 🗺️ **Which** states and regions offer the best growth opportunity?

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| `Pandas` | 2.0+ | Data wrangling, aggregations, time series, cohort pivots |
| `NumPy` | 1.24+ | Numerical operations, statistical computations |
| `Matplotlib` | 3.7+ | Custom visualizations, KPI dashboards, bubble charts |
| `Seaborn` | 0.12+ | Statistical plots, heatmaps, KDE distributions |
| `SciPy` | 1.11+ | Linear regression, correlation statistics |

---

## 📁 Project Structure

```
superstore-sales-analysis/
│
├── data/
│   ├── generate_data.py          ← Reproducible synthetic dataset generator (seed=42)
│   └── raw/
│       └── superstore_sales.csv  ← Generated on first run (5,000 transactions)
│
├── notebooks/
│   ├── 01_EDA.py                 ← Data quality + distributions + temporal analysis
│   ├── 02_kpis_analysis.py       ← Business KPIs + category / region / segment / product
│   ├── 03_discount_insights.py   ← Discount impact + loss analysis + cohort retention
│   └── 04_advanced_insights.py   ← Product portfolio matrix + Pareto + state deep-dive
│
├── src/
│   └── utils.py                  ← Reusable helpers: load, validate, compute_kpis, save_fig
│
├── reports/
│   └── figures/                  ← All exported charts (auto-generated, 18+ visuals)
│
├── requirements.txt
└── README.md
```

> 💡 Each `.py` notebook uses `# %%` cell markers — open in **VS Code** with the Jupyter extension for interactive execution, or convert to `.ipynb` with `jupytext`.

---

## 📦 Dataset

The dataset is **synthetically generated** (`data/generate_data.py`) with the same structure as the classic Kaggle Superstore dataset, ensuring full reproducibility with no external dependencies.

| Property | Value |
|----------|-------|
| Rows | 5,000 transactions |
| Columns | 19 fields |
| Date range | 2021–2023 (3 years) |
| Categories | Technology, Furniture, Office Supplies |
| Regions | West, East, Central, South |
| Segments | Consumer, Corporate, Home Office |

**Key fields:** `Order ID`, `Order Date`, `Ship Date`, `Ship Mode`, `Customer ID`, `Segment`, `Region`, `State`, `Category`, `Sub-Category`, `Product Name`, `Sales`, `Quantity`, `Discount`, `Profit`

---

## 🚀 Quickstart

```bash
# 1. Clone
git clone https://github.com/Grisel86/superstore-sales-analysis.git
cd superstore-sales-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset (only needed once)
python data/generate_data.py

# 4. Run notebooks in order
# Open each .py file in VS Code — each cell is marked with # %%
# Recommended: Run All Cells top to bottom
# Charts auto-save to reports/figures/
```

---

## 📈 Key Findings

### Executive Summary

| Metric | Value | Signal |
|--------|-------|--------|
| 💰 Total Revenue | ~$2.1M across 3 years | Healthy top-line growth |
| 📉 Profit Margin | ~11–13% | Margin pressure from discounts |
| 🔴 Loss-making orders | ~18% of transactions | Discount policy problem |
| 🏷️ Critical threshold | Discount > 30% | Consistently unprofitable |
| 🏆 Best segment | Corporate | Highest avg order value |
| 🗺️ Top region | West | Highest revenue, margin varies |
| 📦 Weakest category | Furniture | Lowest profit margin |
| 🛒 Best sub-category | Phones (Technology) | High sales AND high margin |

---

### 🏷️ Discount Impact

The single most actionable finding in this project: **discounts above 30% destroy profitability across all categories**.

- At **0% discount** → avg profit per order is positive across all categories
- At **11–20%** → margin compresses but remains viable for Technology and Office Supplies
- At **31–40% and above** → avg profit turns **negative** — every sale at this level costs the business money
- Correlation between Discount and Profit: **≈ −0.22**
- Each additional 10% discount shifts avg profit by approximately **−$12 to −$18**

> 📌 Furniture is the most vulnerable: its base margin (~12%) means any discount above ~10% can flip to a loss.

---

### 📦 Category Performance

| Category | Relative Sales | Profit Margin | Risk |
|----------|---------------|---------------|------|
| Technology | High | High (~25%) | Low |
| Office Supplies | Medium | Medium (~30% base) | Low |
| Furniture | High | Low (~12%) | **High** — discount-sensitive |

The **Sub-Category Bubble Chart** (Notebook 02) reveals the clearest picture:
Phones and Computers sit in the *high sales + high profit* quadrant, while Tables and Bookcases drag the Furniture category into loss territory when discounted.

The **Product Portfolio Matrix** (Notebook 04) maps each sub-category on a BCG-style quadrant (Revenue vs Profit Margin), making it easy to identify which products are Stars, Cash Cows, or candidates for strategic review.

---

### 👥 Customer Segments & Retention

| Segment | Share of Sales | Avg Order Value | Opportunity |
|---------|---------------|----------------|-------------|
| Consumer | ~50% | Moderate | Volume retention |
| Corporate | ~30% | **Highest** | B2B loyalty programs |
| Home Office | ~20% | Low-medium | Upsell campaigns |

The **Cohort Retention Heatmap** (Notebook 03) shows customer re-purchase rates by acquisition quarter.

The **Pareto / 80-20 Analysis** (Notebook 04) confirms a classic concentration pattern: a minority of customers generate the majority of revenue, making high-value customer retention the highest-ROI business action.

---

### 🗺️ Regional & State Analysis

- **West** leads in total revenue, driven by California
- **South** shows the weakest margin — likely elevated logistics costs relative to order size
- **State deep-dive** (Notebook 04): top 5 states account for ~60% of total revenue
- Several high-volume states show below-average margins — discount inconsistency is a likely driver
- The **Revenue vs Margin scatter by state** reveals growth opportunities: states with mid-range revenue but high margin are candidates for investment

---

### 🚚 Shipping Profitability

- **Same Day** and **First Class** orders show higher profit margins than Standard Class
- Counter-intuitive finding: customers who pay for faster shipping tend to discount less, suggesting a correlation between urgency and full-price purchasing
- **Standard Class** (50%+ of orders) is the volume workhorse but lowest-margin shipping tier

---

## 📊 Visualizations Generated

| # | File | What it shows |
|---|------|--------------|
| 01 | `01_numeric_distributions.png` | Histograms + KDE for Sales, Profit, Quantity, Discount |
| 02 | `02_categorical_distributions.png` | Bar charts for all categorical fields |
| 03 | `03_monthly_sales_trend.png` | Multi-year monthly trend with area fill |
| 04 | `04_correlation_matrix.png` | Masked lower-triangle heatmap |
| 05 | `05_shipping_analysis.png` | Boxplot + pie chart for ship modes |
| 06 | `06_kpi_dashboard.png` | 6-card executive KPI dashboard |
| 07 | `07_category_performance.png` | Sales, Profit, Margin by category |
| 08 | `08_subcategory_scatter.png` | Bubble chart: Sales vs Profit vs Quantity |
| 09 | `09_regional_performance.png` | Revenue and margin by region |
| 10 | `10_segment_analysis.png` | Donut chart + avg order value by segment |
| 11 | `11_top_products.png` | Top 10 products by sales and profit |
| 12 | `12_discount_impact.png` | Scatter + regression line + avg profit by bucket |
| 13 | `13_loss_analysis.png` | Loss by category, region, and discount KDE |
| 14 | `14_cohort_retention.png` | Quarterly cohort heatmap |
| 15 | `15_product_portfolio_matrix.png` | BCG-style quadrant: revenue vs profit margin |
| 16 | `16_pareto_revenue.png` | 80/20 cumulative revenue by customer |
| 17 | `17_state_performance.png` | Top 15 states: revenue vs margin scatter |
| 18 | `18_ship_mode_profitability.png` | Profit margin and avg order value by ship mode |

---

## 🔍 Data Quality Approach

This project reflects a **QA-first mindset** — a direct application of QA Engineering experience to data analytics:

- `validate_data()` in `utils.py` runs **before any analysis begins**
- Automated checks on every load:
  - Null values per column
  - Duplicate rows
  - Negative sales (data integrity flag)
  - Negative profit (expected — but quantified and tracked)
  - Type consistency
  - Date range integrity (`Ship Date` ≥ `Order Date`)
- All findings reported programmatically — **replicable and auditable**

> This approach mirrors production data pipeline validation and directly maps to **Data Quality Engineer** and **Analytics Engineer** role requirements.

---

## 🎯 Business Recommendations

1. **🏷️ Discount Policy** — Cap discounts at 20% across all categories. For Furniture, the ceiling should be 10–15% given its thin base margin. Implement tiered approval for anything above the threshold.

2. **📦 Furniture Profitability** — Audit logistics costs (weight/volume ratio is unfavorable vs. Office Supplies). Consider targeted price adjustments for Tables and Bookcases, or flag consistent negative-margin SKUs for review.

3. **👥 Corporate Segment** — Highest ticket value with strong retention. Invest in B2B loyalty: dedicated account support, volume pricing tiers, and premium shipping upgrades as a retention benefit.

4. **🗺️ Regional Optimization** — South region shows high order volume but weaker margins. Identify whether discount over-application or logistics costs are the primary driver before deciding on strategy.

5. **📅 Seasonality** — Q4 is the revenue peak. Pre-position inventory, negotiate logistics rates for peak periods, and prioritize Q1 customer acquisition campaigns — cohort data shows Q1 acquirees are the most retentive.

---

## 👩‍💻 Author

**Fabiana Grisel González**  
Data Scientist in training · QA Automation Engineer · Argentina

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?logo=linkedin)](https://www.linkedin.com/in/fabiana-grisel-gonzalez)
[![GitHub](https://img.shields.io/badge/GitHub-%40Grisel86-181717?logo=github)](https://github.com/Grisel86)

---

## 📄 License

MIT — free to use and adapt.