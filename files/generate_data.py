"""
generate_data.py
Genera un dataset sintético similar al Superstore Sales de Kaggle.
Ejecutar una sola vez: python data/generate_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ── Catálogos ────────────────────────────────────────────────────────────────

CATEGORIES = {
    "Technology": {
        "Phones":      ["iPhone 14", "Samsung Galaxy S23", "Google Pixel 7", "OnePlus 11"],
        "Computers":   ["MacBook Pro", "Dell XPS 15", "HP Spectre", "Lenovo ThinkPad"],
        "Accessories": ["Logitech Mouse", "Mechanical Keyboard", "USB Hub", "Webcam HD"],
        "Monitors":    ["LG 27\" 4K", "Samsung 32\" Curved", "Dell UltraSharp 24\""],
    },
    "Furniture": {
        "Chairs":      ["Ergonomic Chair", "Gaming Chair", "Executive Chair", "Task Chair"],
        "Tables":      ["Standing Desk", "Conference Table", "Side Table", "Coffee Table"],
        "Bookcases":   ["5-Shelf Bookcase", "Wall Bookcase", "Corner Bookcase"],
        "Storage":     ["Filing Cabinet", "Storage Ottoman", "Drawer Unit"],
    },
    "Office Supplies": {
        "Paper":       ["A4 Ream 500", "Photo Paper", "Cardstock", "Sticky Notes Pack"],
        "Binders":     ["3-Ring Binder", "Presentation Folder", "Spiral Notebook"],
        "Art":         ["Markers Set", "Colored Pencils", "Sketch Pad", "Watercolors"],
        "Fasteners":   ["Stapler", "Tape Dispenser", "Paper Clips Box", "Rubber Bands"],
    },
}

SEGMENTS   = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
REGIONS    = ["West", "East", "Central", "South"]

REGION_STATES = {
    "West":    ["California", "Washington", "Oregon", "Nevada", "Colorado"],
    "East":    ["New York", "Pennsylvania", "Virginia", "Massachusetts", "Florida"],
    "Central": ["Texas", "Illinois", "Ohio", "Michigan", "Minnesota"],
    "South":   ["Georgia", "North Carolina", "Tennessee", "Alabama", "Louisiana"],
}

CITIES = {
    "California": ["Los Angeles", "San Francisco", "San Diego"],
    "Washington": ["Seattle", "Spokane"],
    "Oregon":     ["Portland", "Eugene"],
    "Nevada":     ["Las Vegas", "Reno"],
    "Colorado":   ["Denver", "Boulder"],
    "New York":   ["New York City", "Buffalo"],
    "Pennsylvania":["Philadelphia", "Pittsburgh"],
    "Virginia":   ["Richmond", "Arlington"],
    "Massachusetts":["Boston", "Cambridge"],
    "Florida":    ["Miami", "Orlando", "Tampa"],
    "Texas":      ["Houston", "Dallas", "Austin"],
    "Illinois":   ["Chicago", "Springfield"],
    "Ohio":       ["Columbus", "Cleveland"],
    "Michigan":   ["Detroit", "Grand Rapids"],
    "Minnesota":  ["Minneapolis", "Saint Paul"],
    "Georgia":    ["Atlanta", "Savannah"],
    "North Carolina":["Charlotte", "Raleigh"],
    "Tennessee":  ["Nashville", "Memphis"],
    "Alabama":    ["Birmingham", "Montgomery"],
    "Louisiana":  ["New Orleans", "Baton Rouge"],
}

# ── Generador ─────────────────────────────────────────────────────────────────

def random_date(start="2021-01-01", end="2023-12-31"):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt   = datetime.strptime(end,   "%Y-%m-%d")
    return start_dt + timedelta(days=random.randint(0, (end_dt - start_dt).days))

def generate_dataset(n_rows: int = 5000) -> pd.DataFrame:
    rows = []
    customer_pool = [f"CUST-{i:04d}" for i in range(1, 401)]
    names_pool    = [
        "James Wilson", "Maria Garcia", "Robert Smith", "Jennifer Davis",
        "Michael Brown", "Patricia Johnson", "David Martinez", "Linda Anderson",
        "John Taylor", "Barbara Thomas", "William Jackson", "Elizabeth White",
        "Richard Harris", "Susan Martin", "Joseph Thompson", "Jessica Garcia",
        "Thomas Moore", "Sarah Rodriguez", "Charles Lewis", "Karen Clark",
    ] * 20  # 400 nombres únicos aprox

    for i in range(n_rows):
        # Geografía
        region = random.choice(REGIONS)
        state  = random.choice(REGION_STATES[region])
        city   = random.choice(CITIES[state])

        # Producto
        cat     = random.choice(list(CATEGORIES.keys()))
        subcat  = random.choice(list(CATEGORIES[cat].keys()))
        product = random.choice(CATEGORIES[cat][subcat])

        # Precios base por categoría
        base_price = {"Technology": 350, "Furniture": 280, "Office Supplies": 45}[cat]
        price_noise = np.random.uniform(0.5, 2.5)
        unit_price  = round(base_price * price_noise, 2)

        # Orden
        quantity = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        discount = random.choices([0, 0.1, 0.2, 0.3, 0.4, 0.5],
                                  weights=[40, 20, 20, 10, 7, 3])[0]
        sales    = round(unit_price * quantity * (1 - discount), 2)

        # Profit: mayor descuento → menor margen (puede ser negativo)
        margin_base = {"Technology": 0.25, "Furniture": 0.12, "Office Supplies": 0.30}[cat]
        margin      = margin_base - discount * 0.9 + np.random.normal(0, 0.04)
        profit      = round(sales * margin, 2)

        # Fechas
        order_date = random_date()
        ship_days  = {"Standard Class": 5, "Second Class": 3,
                      "First Class": 2, "Same Day": 0}
        ship_mode  = random.choices(
            list(ship_days.keys()), weights=[50, 25, 20, 5]
        )[0]
        ship_date  = order_date + timedelta(days=ship_days[ship_mode]
                                            + random.randint(0, 2))

        cust_idx = random.randint(0, len(customer_pool) - 1)

        rows.append({
            "Order ID":       f"ORD-{2021 + (order_date.year - 2021)}-{i:05d}",
            "Order Date":     order_date.strftime("%Y-%m-%d"),
            "Ship Date":      ship_date.strftime("%Y-%m-%d"),
            "Ship Mode":      ship_mode,
            "Customer ID":    customer_pool[cust_idx],
            "Customer Name":  names_pool[cust_idx],
            "Segment":        random.choice(SEGMENTS),
            "Country":        "United States",
            "City":           city,
            "State":          state,
            "Region":         region,
            "Product ID":     f"PROD-{cat[:3].upper()}-{abs(hash(product)) % 9999:04d}",
            "Category":       cat,
            "Sub-Category":   subcat,
            "Product Name":   product,
            "Sales":          sales,
            "Quantity":       quantity,
            "Discount":       discount,
            "Profit":         profit,
        })

    df = pd.DataFrame(rows)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"])
    return df


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "raw", "superstore_sales.csv")
    df = generate_dataset(5000)
    df.to_csv(output_path, index=False)
    print(f"✅ Dataset generado: {output_path}")
    print(f"   Filas: {len(df):,}  |  Columnas: {df.shape[1]}")
    print(f"   Rango: {df['Order Date'].min().date()} → {df['Order Date'].max().date()}")
    print(f"   Ventas totales: ${df['Sales'].sum():,.2f}")
