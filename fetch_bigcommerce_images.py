#!/usr/bin/env python3
"""
Fetch missing product images from BigCommerce API.

Reads catalog.json, finds SKUs with empty images[], queries the BigCommerce
API by SKU, extracts product images, and updates catalog.json.
"""

import json
import sys
from pathlib import Path

import httpx

BIGCOMMERCE_STORE_HASH = "ijm7dw7yvr"
BIGCOMMERCE_ACCESS_TOKEN = "hposyo0lemeuc5b8tnxfd5y8aa1k8ph"
BASE_URL = f"https://api.bigcommerce.com/stores/{BIGCOMMERCE_STORE_HASH}/v3"
HEADERS = {
    "X-Auth-Token": BIGCOMMERCE_ACCESS_TOKEN,
    "Accept": "application/json",
}

PROJECT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = PROJECT_DIR / "catalog.json"


def search_product(client: httpx.Client, sku: str) -> dict | None:
    """Search for a product by SKU, returning the product data with images."""
    try:
        r = client.get(
            f"{BASE_URL}/catalog/products",
            params={"sku": sku, "include": "images"},
        )
        r.raise_for_status()
        data = r.json()
        products = data.get("data", [])
        if products:
            return products[0]
        return None
    except Exception as e:
        print(f"    API error: {e}")
        return None


def main():
    # Load catalog
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    # Find SKUs with no images
    missing = [
        sku for sku, data in catalog["products"].items()
        if not data.get("images")
    ]
    print(f"Querying BigCommerce for {len(missing)} SKUs with missing images...")

    updated = 0
    not_found = []

    with httpx.Client(headers=HEADERS, timeout=30.0) as client:
        for i, sku in enumerate(missing):
            print(f"[{i+1}/{len(missing)}] {sku}...", end=" ", flush=True)
            product = search_product(client, sku)

            if not product:
                print("NOT FOUND")
                not_found.append(sku)
                continue

            images = product.get("images", [])
            if not images:
                print("no images on product")
                not_found.append(sku)
                continue

            # Extract standard-size image URLs
            image_urls = [img["url_standard"] for img in images if img.get("url_standard")]
            if image_urls:
                catalog["products"][sku]["images"] = image_urls
                # Update product URL if we have one
                custom_url = product.get("custom_url", {}).get("url", "")
                if custom_url:
                    catalog["products"][sku]["url"] = f"https://shopluvbuds.com{custom_url}"
                updated += 1
                print(f"FOUND {len(image_urls)} image(s)")
            else:
                print("images missing url_standard")
                not_found.append(sku)

    if updated > 0:
        # Backup
        backup_path = CATALOG_PATH.with_suffix(".json.bak")
        with open(backup_path, "w") as f:
            json.dump(catalog, f, indent="\t")

        # Update stats
        missing_after = sum(1 for _, d in catalog["products"].items() if not d.get("images"))
        catalog["stats"]["products_with_images"] = len(catalog["products"]) - missing_after
        catalog["stats"]["products_without_images"] = missing_after

        # Save
        with open(CATALOG_PATH, "w") as f:
            json.dump(catalog, f, indent="\t")

        print(f"\nUpdated {updated} SKUs with BigCommerce images")
        print(f"Missing before: {len(missing)}, missing after: {missing_after}")
        print(f"Backup: {backup_path}")

        if not_found:
            print(f"\nStill missing ({len(not_found)}):")
            for sku in not_found:
                print(f"  {sku}")
    else:
        print(f"\nNo images found for any of the {len(missing)} SKUs.")


if __name__ == "__main__":
    main()
