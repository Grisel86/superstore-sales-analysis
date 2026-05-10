# 📊 Superstore Sales Analysis

**End-to-end Exploratory Data Analysis and Business Intelligence project**  
simulating a real-world retail analytics scenario.

---

## 🗂️ Business Problem

A retail company with 3 years of transactional data needs to understand:
- **Where** is the business generating (and losing) profit?
- **What** is the impact of discounts on the bottom line?
- **Who** are the most valuable customer segments?
- **When** do sales peaks occur and how to leverage them?

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `Pandas` | Data wrangling, aggregations, time series |
| `NumPy` | Numerical operations, statistical computations |
| `Matplotlib` | Custom visualizations, dashboards |
| `Seaborn` | Statistical plots, heatmaps, distributions |
| `SciPy` | Linear regression, statistical tests |

---

## 📁 Project Structure

```
superstore-sales-analysis/
├── data/
│   ├── generate_data.py     ← Synthetic dataset generator
│   └── raw/                 ← Generated CSV lands here
├── notebooks/
│   ├── 01_EDA.py            ← Data quality + distributions
│   ├── 02_kpis_analysis.py  ← Business KPIs + category/region/segment
│   └── 03_discount_insights.py ← Discount impact + loss analysis + cohorts
├── src/
│   └── utils.py             ← Reusable helpers (load, validate, KPIs, plots)
├── reports/
│   └── figures/             ← All exported charts (auto-generated)
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart

```bash
# 1. Clone
git clone https://github.com/Grisel86/superstore-sales-analysis.git
cd superstore-sales-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset
python data/generate_data.py

# 4. Run notebooks (VS Code with Jupyter extension, or convert to .ipynb)
# Each .py file uses # %% cell markers — open in VS Code for interactive execution
```

---

## 📈 Key Findings

| Insight | Detail |
|---------|--------|
| 💰 Total Revenue | ~$2.1M across 3 years |
| 📉 Loss-making orders | ~18% of transactions at a loss |
| 🏷️ Discount threshold | Orders with >30% discount are consistently unprofitable |
| 🏆 Best segment | Corporate — highest avg order value |
| 🗺️ Top region | West — highest revenue but margin varies |
| 📦 Weakest category | Furniture — lowest profit margin |

---

## 📊 Sample Visualizations

> Charts auto-saved to `reports/figures/` when notebooks are executed.

- **KPI Dashboard** — 6 business KPIs in card layout
- **Monthly Sales Trend** — Multi-year comparison line chart
- **Category Performance** — Sales, Profit & Margin side-by-side
- **Sub-Category Bubble Chart** — Sales vs Profit, size = Quantity
- **Discount Impact** — Scatter + regression line, avg profit by discount bucket
- **Loss Analysis** — Where the business loses money (category + region)
- **Cohort Retention Heatmap** — Customer retention by acquisition quarter

---

## 🔍 Data Quality Approach

This project reflects a **QA-first mindset**:
- Automated data validation before any analysis (`validate_data()` in `utils.py`)
- Checks for: nulls, duplicates, negative sales, type consistency, date range integrity
- All findings reported programmatically — replicable and auditable

---

## 👩‍💻 Author

**Fabiana Grisel González**  
 Data Scientist / QA Automation Engineer 
[LinkedIn](https://www.linkedin.com/in/fabiana-grisel-gonzalez) · [GitHub](https://github.com/Grisel86)

---

## 📄 License

MIT — free to use and adapt.
