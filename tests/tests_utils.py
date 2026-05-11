"""
tests/test_utils.py
Unit tests para src/utils.py

Cobertura:
- validate_data()  → calidad del dato
- compute_kpis()   → lógica de negocio
- load_data()      → integridad del dataset generado
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import validate_data, compute_kpis, load_data


# ── Fixture compartida ────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """DataFrame mínimo y válido para tests de validate_data y compute_kpis.
    No depende del archivo CSV — cada test es autónomo."""
    return pd.DataFrame({
        "Order ID":    ["ORD-001", "ORD-002", "ORD-003"],
        "Order Date":  pd.to_datetime(["2022-01-01", "2022-02-15", "2022-03-10"]),
        "Ship Date":   pd.to_datetime(["2022-01-05", "2022-02-18", "2022-03-15"]),
        "Customer ID": ["C001", "C002", "C001"],
        "Sales":       [500.0, 200.0, 350.0],
        "Profit":      [100.0, -20.0, 75.0],   # ORD-002 tiene pérdida intencional
        "Quantity":    [2, 1, 3],
        "Discount":    [0.0, 0.2, 0.1],
    })


# ── Tests: validate_data() ────────────────────────────────────────────────────

class TestValidateData:

    def test_returns_dict_with_required_keys(self, sample_df):
        """El reporte debe tener exactamente las claves esperadas."""
        report = validate_data(sample_df)
        expected_keys = {"shape", "nulls", "duplicates", "dtypes",
                         "negative_sales", "negative_profit", "date_range"}
        assert expected_keys.issubset(report.keys())

    def test_clean_dataset_has_no_nulls(self, sample_df):
        """Un dataset limpio no debe reportar nulls."""
        report = validate_data(sample_df)
        assert sum(report["nulls"].values()) == 0

    def test_detects_null_in_sales(self, sample_df):
        """Debe detectar exactamente 1 null en Sales cuando se inyecta uno."""
        df = sample_df.copy()
        df.loc[0, "Sales"] = None
        report = validate_data(df)
        assert report["nulls"]["Sales"] == 1

    def test_detects_duplicate_rows(self, sample_df):
        """Debe contar el número correcto de filas duplicadas."""
        df_dup = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
        report = validate_data(df_dup)
        assert report["duplicates"] == 1

    def test_detects_negative_sales(self, sample_df):
        """Ventas negativas son una anomalía de datos — deben ser detectadas."""
        df = sample_df.copy()
        df.loc[0, "Sales"] = -50.0
        report = validate_data(df)
        assert report["negative_sales"] == 1

    def test_negative_profit_is_counted(self, sample_df):
        """Profit negativo es válido de negocio (pérdida), pero debe cuantificarse.
        sample_df tiene 1 orden con pérdida: ORD-002 (Profit=-20)."""
        report = validate_data(sample_df)
        assert report["negative_profit"] == 1

    def test_date_range_matches_data(self, sample_df):
        """El rango de fechas debe coincidir con el min/max real del dataset."""
        report = validate_data(sample_df)
        start, end = report["date_range"]
        assert start == pd.Timestamp("2022-01-01")
        assert end   == pd.Timestamp("2022-03-10")

    def test_shape_is_correct(self, sample_df):
        """El shape reportado debe ser (3, 8) para sample_df."""
        report = validate_data(sample_df)
        assert report["shape"] == (3, 8)


# ── Tests: compute_kpis() ─────────────────────────────────────────────────────

class TestComputeKpis:

    def test_returns_all_expected_kpis(self, sample_df):
        """Todas las métricas de negocio deben estar presentes en el resultado."""
        kpis = compute_kpis(sample_df)
        expected = {"total_sales", "total_profit", "profit_margin",
                    "total_orders", "avg_order_value", "total_customers",
                    "avg_discount", "orders_at_loss"}
        assert expected.issubset(kpis.keys())

    def test_total_sales_is_correct(self, sample_df):
        """500 + 200 + 350 = 1050."""
        kpis = compute_kpis(sample_df)
        assert kpis["total_sales"] == pytest.approx(1050.0)

    def test_total_profit_is_correct(self, sample_df):
        """100 - 20 + 75 = 155."""
        kpis = compute_kpis(sample_df)
        assert kpis["total_profit"] == pytest.approx(155.0)

    def test_profit_margin_formula(self, sample_df):
        """Margin = (155 / 1050) * 100 ≈ 14.76%."""
        kpis = compute_kpis(sample_df)
        expected_margin = (155.0 / 1050.0) * 100
        assert kpis["profit_margin"] == pytest.approx(expected_margin, rel=1e-3)

    def test_total_customers_deduplicates(self, sample_df):
        """C001 aparece 2 veces → debe contar como 1 cliente único."""
        kpis = compute_kpis(sample_df)
        assert kpis["total_customers"] == 2

    def test_orders_at_loss_correct(self, sample_df):
        """Solo ORD-002 tiene profit < 0 → 1 orden en pérdida."""
        kpis = compute_kpis(sample_df)
        assert kpis["orders_at_loss"] == 1

    def test_avg_discount_is_percentage(self, sample_df):
        """avg_discount debe estar entre 0 y 100 (es %, no ratio)."""
        kpis = compute_kpis(sample_df)
        assert 0 <= kpis["avg_discount"] <= 100

    def test_avg_order_value_is_positive(self, sample_df):
        """El ticket promedio debe ser positivo."""
        kpis = compute_kpis(sample_df)
        assert kpis["avg_order_value"] > 0


# ── Tests: load_data() (requiere dataset generado) ────────────────────────────

class TestLoadData:

    def test_returns_dataframe(self):
        """load_data() debe retornar un DataFrame, no None ni dict."""
        df = load_data()
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        """Todas las columnas críticas para el análisis deben existir."""
        df = load_data()
        required = [
            "Order ID", "Order Date", "Ship Date", "Ship Mode",
            "Customer ID", "Segment", "Region", "State",
            "Category", "Sub-Category", "Product Name",
            "Sales", "Quantity", "Discount", "Profit",
        ]
        missing = [col for col in required if col not in df.columns]
        assert missing == [], f"Columnas faltantes: {missing}"

    def test_date_columns_are_datetime(self):
        """Order Date y Ship Date deben ser dtype datetime, no string."""
        df = load_data()
        assert pd.api.types.is_datetime64_any_dtype(df["Order Date"])
        assert pd.api.types.is_datetime64_any_dtype(df["Ship Date"])

    def test_ship_date_never_before_order_date(self):
        """Integridad temporal: ningún envío puede ocurrir antes del pedido."""
        df = load_data()
        invalid = (df["Ship Date"] < df["Order Date"]).sum()
        assert invalid == 0, f"{invalid} órdenes tienen Ship Date < Order Date"

    def test_no_negative_sales(self):
        """Ventas negativas son un error de datos en este dataset."""
        df = load_data()
        negatives = (df["Sales"] < 0).sum()
        assert negatives == 0, f"Se encontraron {negatives} ventas negativas"

    def test_discount_range_is_valid(self):
        """Discount debe estar en [0.0, 1.0] — es un ratio, no porcentaje."""
        df = load_data()
        assert df["Discount"].between(0.0, 1.0).all(), \
            "Hay valores de Discount fuera del rango [0, 1]"

    def test_dataset_has_minimum_rows(self):
        """El dataset generado debe tener al menos 4000 filas para análisis válido."""
        df = load_data()
        assert len(df) >= 4000, f"Dataset muy pequeño: {len(df)} filas"

    def test_categories_are_valid(self):
        """Solo deben existir las 3 categorías definidas en el generador."""
        df = load_data()
        valid_cats = {"Technology", "Furniture", "Office Supplies"}
        actual_cats = set(df["Category"].unique())
        assert actual_cats == valid_cats, \
            f"Categorías inesperadas: {actual_cats - valid_cats}"