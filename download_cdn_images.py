#!/usr/bin/env python3
"""Download primary BigCommerce images for CDN-only products and update catalog.json."""
import json, os, re, time, urllib.request, sys

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

def get_cdn_only_products(products):
    """Find products with CDN images but no local images."""
    result = []
    for sku, p in products.items():
        images = p.get('images', [])
        has_local = False
        cdn_urls = []
        bc_ids = set()
        for img in images:
            src = img if isinstance(img, str) else img.get('src', '')
            if src.startswith('images/'):
                has_local = True
            elif src.startswith('http'):
                cdn_urls.append(src)
                m = re.search(r'products/(\d+)/', src)
                if m:
                    bc_ids.add(m.group(1))
        if not has_local and cdn_urls:
            result.append((sku, list(bc_ids)[0] if bc_ids else None, cdn_urls))
    return result

def fetch_product_images(bc_product_id):
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
        print(f"  API error for product {bc_product_id}: {e}", file=sys.stderr)
        return None

def pick_best_image(images):
    """Pick the primary image: is_thumbnail=True, or first by sort_order."""
    if not images:
        return None
    # Prefer thumbnail
    for img in images:
        if img.get('is_thumbnail'):
            return img
    # Fall back to lowest sort_order
    images.sort(key=lambda x: x.get('sort_order', 99))
    return images[0]

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
    items = get_cdn_only_products(products)

    print(f"Found {len(items)} CDN-only products to process")

    success = 0
    skipped = 0
    failed = 0

    for i, (sku, bc_id, cdn_urls) in enumerate(items):
        local_path = f"{IMAGES_DIR}/{sku}.png"

        # Skip if already downloaded
        if os.path.exists(local_path):
            print(f"[{i+1}/{len(items)}] {sku}: already exists, wiring only")
            skipped += 1
        else:
            if not bc_id:
                print(f"[{i+1}/{len(items)}] {sku}: no BC product ID extractable")
                failed += 1
                continue

            # Rate limit: 200ms between API calls
            if i > 0:
                time.sleep(0.2)

            imgs = fetch_product_images(bc_id)
            if imgs is None:
                failed += 1
                continue

            best = pick_best_image(imgs)
            if not best:
                print(f"[{i+1}/{len(items)}] {sku}: no images returned from API")
                failed += 1
                continue

            # Prefer url_zoom, fall back to url_standard
            img_url = best.get('url_zoom') or best.get('url_standard') or best.get('url_thumbnail')
            if not img_url:
                print(f"[{i+1}/{len(items)}] {sku}: no usable URL in image data")
                failed += 1
                continue

            print(f"[{i+1}/{len(items)}] {sku}: downloading from product {bc_id}...")
            if download_image(img_url, local_path):
                success += 1
            else:
                failed += 1
                continue

        # Update catalog: prepend local image, keep CDN images
        current_images = products[sku].get('images', [])
        # Filter out the local path if somehow already present
        current_images = [img for img in current_images
                         if not (isinstance(img, str) and img == local_path)]
        products[sku]['images'] = [local_path] + current_images

        print(f"  -> {local_path} + {len(current_images)} CDN images")

    # Save updated catalog
    save_catalog(catalog)

    print(f"\nDone: {success} downloaded, {skipped} already existed, {failed} failed")
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
