#!/usr/bin/env python3
"""Build catalog.json from 6 enriched CSV files.

Reads all CSVs from ../csv/, normalizes columns, outputs unified catalog.json.
Handles: dimension parsing, price derivation, product line assignment,
missing column detection, blank dimension flagging.
"""

import csv
import json
import math
import os
import re
import sys
from pathlib import Path

CSV_DIR = Path(__file__).resolve().parent.parent / "csv"
OUTPUT = Path(__file__).resolve().parent / "catalog.json"

# Product line derived from filename keywords
LINE_MAP = {
    ("vape", "green"): "vape-green",
    ("vape", "yellow"): "vape-yellow",
    ("herb", "green"): "herb-green",
    ("herb", "yellow"): "herb-yellow",
    ("glass", "green"): "glass-green",
    ("glass", "yellow"): "glass-yellow",
}

LINE_LABELS = {
    "vape-green": "Vape — Green",
    "vape-yellow": "Vape — Yellow",
    "herb-green": "Herb — Green",
    "herb-yellow": "Herb — Yellow",
    "glass-green": "Glass — Green",
    "glass-yellow": "Glass — Yellow",
}

# Color palettes per line (dark greens, warm yellows, cool blues, warm oranges)
LINE_COLORS = {
    "vape-green": "#1B5E20",
    "vape-yellow": "#F9A825",
    "herb-green": "#004D40",
    "herb-yellow": "#F57F17",
    "glass-green": "#01579B",
    "glass-yellow": "#FF8F00",
}

# Category color palette — auto-assigned, stable order
CATEGORY_PALETTE = [
    "#1B5E20", "#4A148C", "#B71C1C", "#0D47A1", "#E65100",
    "#004D40", "#311B92", "#BF360C", "#1A237E", "#3E2723",
    "#33691E", "#880E4F", "#263238", "#827717", "#006064",
    "#F57F17", "#6A1B9A", "#C62828", "#1565C0", "#EF6C00",
    "#2E7D32", "#AD1457", "#4E342E", "#9E9D24", "#00838F",
    "#FF8F00", "#283593", "#4527A0", "#558B2F", "#37474F",
]


def detect_line(filename):
    """Derive product line from CSV filename."""
    name = filename.lower()
    for (cat, tier), line_id in LINE_MAP.items():
        if cat in name and tier in name:
            return line_id
    return None


def parse_dimensions(dim_str):
    """Parse dimension string like '1.53" x 3.22" x 0.7"' into (w, h, d) in inches.
    Returns (None, None, None) if unparseable."""
    if not dim_str or not dim_str.strip():
        return None, None, None
    # Extract all numbers from the string
    nums = re.findall(r"(\d+\.?\d*)\s*\"", dim_str)
    if len(nums) == 3:
        return float(nums[0]), float(nums[1]), float(nums[2])
    if len(nums) == 2:
        # Sometimes depth is missing; assume width + height
        return float(nums[0]), float(nums[1]), None
    return None, None, None


def parse_money(val):
    """Parse '$1,234.56' or '1234.56' → float. Returns None if empty/invalid."""
    if not val or not val.strip():
        return None
    clean = val.replace("$", "").replace(",", "").strip()
    try:
        return float(clean)
    except ValueError:
        return None


def parse_int(val):
    """Parse '1,234' → int. Returns None if empty/invalid."""
    if not val or not val.strip():
        return None
    try:
        return int(val.replace(",", "").strip())
    except ValueError:
        return None


def derive_price(revenue, qty_sold):
    """Derive unit price from revenue / quantity sold."""
    if revenue is None or qty_sold is None or qty_sold == 0:
        return None
    return round(revenue / qty_sold, 2)


def derive_cost(revenue, profit, qty_sold):
    """Derive unit cost from (revenue - profit) / quantity sold."""
    if revenue is None or profit is None or qty_sold is None or qty_sold == 0:
        return None
    return round((revenue - profit) / qty_sold, 2)


def extract_brand(description, sku):
    """Extract brand name from description or SKU prefix."""
    brand_patterns = [
        (r"^Pulsar\b", "Pulsar"),
        (r"^Lookah\b", "Lookah"),
        (r"^SirEEL\b", "SirEEL"),
        (r"^SMYLE\s+Labs?\b", "SMYLE Labs"),
        (r"^GROOVE\b", "GROOVE"),
        (r"^Ooze\b", "Ooze"),
        (r"^Yocan\b", "Yocan"),
        (r"^Wulf\b", "Wulf"),
        (r"^Puffco\b", "Puffco"),
        (r"^Zenco\b", "Zenco"),
        (r"^Boundless\b", "Boundless"),
        (r"^RAW\b", "RAW"),
        (r"^Pop\s+Cones?\b", "Pop Cones"),
        (r"^FUTUROLA\b", "FUTUROLA"),
        (r"^Tyson\b", "Tyson 2.0"),
        (r"^Eyce\b", "Eyce"),
        (r"^ZAZA\b", "ZAZA"),
    ]
    for pattern, brand in brand_patterns:
        if re.search(pattern, description, re.IGNORECASE):
            return brand
    # Fallback: first word of SKU prefix
    if "-" in sku:
        return sku.split("-")[0]
    return None


def load_csv(path):
    """Load a CSV, returning (rows, fieldnames)."""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows, reader.fieldnames


def normalize_row(row, fieldnames, line_id):
    """Normalize a single CSV row to the standard product schema."""
    # Handle missing Primary Category column (Vape green CSV)
    primary = row.get("Primary Category", "").strip()
    subcategory = row.get("Subcategory 1", "").strip()

    # If no Primary Category, derive from Subcategory 1 or line
    if not primary:
        if subcategory:
            primary = subcategory
        else:
            primary = LINE_LABELS.get(line_id, line_id)

    description = row.get("Description", "").strip()
    sku = row.get("SKU", "").strip()

    qty_sold = parse_int(row.get("QTY Sold", ""))
    revenue = parse_money(row.get("Revenue", ""))
    available = parse_int(row.get("Available Physical", ""))
    profit = parse_money(row.get("Profit", ""))

    product_url = row.get("Product URL", "").strip()
    image_urls_raw = row.get("Image URLs", "").strip()

    # Parse image URLs — pipe-separated
    images = []
    if image_urls_raw:
        images = [u.strip() for u in image_urls_raw.split("|") if u.strip()]

    dims_raw = row.get("Dimensions (W x H x D)", "").strip()
    width, height, depth = parse_dimensions(dims_raw)

    unit_price = derive_price(revenue, qty_sold)
    unit_cost = derive_cost(revenue, profit, qty_sold)
    brand = extract_brand(description, sku)

    has_dimensions = width is not None and height is not None

    return {
        "sku": sku,
        "name": description,
        "category": primary,
        "subcategory": subcategory if subcategory != primary else "",
        "line": line_id,
        "qtySold": qty_sold,
        "revenue": revenue,
        "available": available,
        "profit": profit,
        "unitPrice": unit_price,
        "unitCost": unit_cost,
        "brand": brand,
        "url": product_url,
        "images": images,
        "width": width,
        "height": height,
        "depth": depth,
        "hasDimensions": has_dimensions,
    }


def build_category_colors(products):
    """Assign distinct colors to each subcategory across all products."""
    subcats = {}
    for p in products:
        sc = p["subcategory"] or p["category"]
        if sc not in subcats:
            subcats[sc] = CATEGORY_PALETTE[len(subcats) % len(CATEGORY_PALETTE)]
    return subcats


def main():
    csv_files = sorted(CSV_DIR.glob("*.csv"))
    if not csv_files:
        print(f"ERROR: No CSV files found in {CSV_DIR}", file=sys.stderr)
        sys.exit(1)

    all_products = {}
    missing_dimensions = []
    line_counts = {}

    for csv_path in csv_files:
        line_id = detect_line(csv_path.name)
        if line_id is None:
            print(f"WARNING: Could not detect product line for {csv_path.name}", file=sys.stderr)
            continue

        rows, fieldnames = load_csv(csv_path)
        count = 0
        for row in rows:
            sku = row.get("SKU", "").strip()
            if not sku:
                continue  # skip blank rows

            if sku in all_products:
                print(f"  DUPLICATE: {sku} already in {all_products[sku]['line']}, skipping in {line_id}", file=sys.stderr)
                continue

            product = normalize_row(row, fieldnames, line_id)
            all_products[sku] = product
            count += 1

            if not product["hasDimensions"]:
                missing_dimensions.append(sku)

        line_counts[line_id] = count
        print(f"  {csv_path.name}: {count} SKUs → {line_id}")

    # Build output
    categories = build_category_colors(all_products.values())

    catalog = {
        "products": all_products,
        "lines": {
            lid: {"label": LINE_LABELS.get(lid, lid), "color": LINE_COLORS.get(lid, "#888888")}
            for lid in sorted(line_counts.keys())
        },
        "categories": categories,
        "stats": {
            "totalSKUs": len(all_products),
            "missingDimensions": len(missing_dimensions),
            "missingDimensionSKUs": sorted(missing_dimensions),
            "lines": line_counts,
        },
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(all_products)} products to {OUTPUT}")
    print(f"  Lines: {', '.join(f'{lid}({n})' for lid, n in sorted(line_counts.items()))}")
    print(f"  Categories: {len(categories)}")
    print(f"  Missing dimensions: {len(missing_dimensions)} SKUs")
    if missing_dimensions:
        print(f"  Flagged: {', '.join(sorted(missing_dimensions)[:15])}...")


if __name__ == "__main__":
    main()
