#!/usr/bin/env python3
"""Download BigCommerce images for zero-image products by searching SKU."""
import json, os, time, urllib.request, sys

BC_STORE = "ijm7dw7yvr"
BC_TOKEN = "hposyo0lemeuc5b8tnxfd5y8aa1k8ph"
BC_API = f"https://api.bigcommerce.com/stores/{BC_STORE}/v3"

CATALOG_PATH = "catalog.json"
IMAGES_DIR = "images"

def load_catalog():
    with open(CATALOG_PATH) as f:
        return json.load(f)

def save_catalog(data):
    with open(CATALOG_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def find_product_by_sku(sku):
    """Search BigCommerce for a product by SKU."""
    url = f"{BC_API}/catalog/products?sku={sku}&include=images"
    req = urllib.request.Request(url, headers={
        "X-Auth-Token": BC_TOKEN,
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            prods = data.get('data', [])
            return prods[0] if prods else None
    except Exception as e:
        print(f"  API error for {sku}: {e}", file=sys.stderr)
        return None

def get_product_images(bc_product_id):
    """Get images from BigCommerce API for a product."""
    url = f"{BC_API}/catalog/products/{bc_product_id}/images"
    req = urllib.request.Request(url, headers={
        "X-Auth-Token": BC_TOKEN,
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get('data', [])
    except Exception as e:
        print(f"  Images API error for {bc_product_id}: {e}", file=sys.stderr)
        return []

def pick_best_image(images):
    """Pick primary: is_thumbnail=True, or first by sort_order."""
    if not images:
        return None
    for img in images:
        if img.get('is_thumbnail'):
            return img
    images_sorted = sorted(images, key=lambda x: x.get('sort_order', 99))
    return images_sorted[0]

def download_image(url, filepath):
    """Download an image to a local path."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  Download error: {e}", file=sys.stderr)
        return False

def main():
    catalog = load_catalog()
    products = catalog.get('products', {})

    # Find zero-image products
    items = [(sku, p) for sku, p in products.items() if not p.get('images')]
    print(f"Found {len(items)} zero-image products")

    success = 0
    failed = 0

    for i, (sku, p) in enumerate(items):
        local_path = f"{IMAGES_DIR}/{sku}.png"
        if os.path.exists(local_path):
            print(f"[{i+1}/{len(items)}] {sku}: local image already exists, wiring only")
            products[sku]['images'] = [local_path]
            success += 1
            continue

        if i > 0:
            time.sleep(0.2)

        # Find in BigCommerce by SKU
        bc_product = find_product_by_sku(sku)
        if not bc_product:
            print(f"[{i+1}/{len(items)}] {sku}: NOT FOUND in BigCommerce")
            failed += 1
            continue

        bc_id = bc_product['id']
        bc_name = bc_product.get('name', '')[:50]

        # Get images
        imgs = get_product_images(bc_id)
        if not imgs:
            print(f"[{i+1}/{len(items)}] {sku}: found in BC (id={bc_id}) but no images")
            failed += 1
            continue

        best = pick_best_image(imgs)
        if not best:
            print(f"[{i+1}/{len(items)}] {sku}: no usable image")
            failed += 1
            continue

        img_url = best.get('url_zoom') or best.get('url_standard') or best.get('url_thumbnail')
        if not img_url:
            print(f"[{i+1}/{len(items)}] {sku}: no image URL")
            failed += 1
            continue

        print(f"[{i+1}/{len(items)}] {sku}: downloading from BC id={bc_id} ({bc_name})...")
        if download_image(img_url, local_path):
            products[sku]['images'] = [local_path]
            # Update URL if it was a search URL
            if 'search.php' in p.get('url', ''):
                # Derive the product URL from BC data
                custom_url = bc_product.get('custom_url', {})
                url_path = custom_url.get('url', '') if isinstance(custom_url, dict) else ''
                if url_path:
                    products[sku]['url'] = f"https://shopluvbuds.com{url_path}"
            success += 1
        else:
            failed += 1

    save_catalog(catalog)
    print(f"\nDone: {success} succeeded, {failed} failed")
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
