#!/usr/bin/env python3
"""
Fetch missing product images from shopluvbuds.com via Tandem Browser.

Reads catalog.json, finds SKUs with empty images[], searches
shopluvbuds.com for each via Tandem Browser, extracts product images,
and updates catalog.json.

Requires Tandem Browser running locally on port 8765.
"""

import asyncio
import json
import os
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

# --- Config ---
TANDEM_URL = "http://127.0.0.1:8765"
SEARCH_TEMPLATE = "https://shopluvbuds.com/search.php?search_query={sku}"
PROJECT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = PROJECT_DIR / "catalog.json"
CHECKPOINT_PATH = PROJECT_DIR / ".fetch_images_checkpoint.json"


def load_token() -> str:
    """Read Tandem API token from ~/.tandem/api-token."""
    token_path = Path.home() / ".tandem" / "api-token"
    if token_path.exists():
        return token_path.read_text().strip()
    return ""


class ImageExtractor(HTMLParser):
    """Parse BigCommerce search results HTML, extracting product image URLs."""

    def __init__(self):
        super().__init__()
        self.images = []
        self._in_product_card = False
        self._in_article = False
        self._current_src = None
        self._current_alt = None
        self._product_urls = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Track product card / article context
        classes = attrs_dict.get("class", "")
        if tag == "article" or tag == "li":
            if any(c in classes for c in ("product", "card", "productCard")):
                self._in_article = True

        # Capture product links
        if tag == "a" and self._in_article:
            href = attrs_dict.get("href", "")
            if href and "/products/" not in href and href not in self._product_urls:
                full = urljoin("https://shopluvbuds.com", href)
                if "shopluvbuds.com" in full:
                    self._product_urls.append(full)

        # Capture img src within product cards
        if tag == "img":
            src = attrs_dict.get("src", "") or attrs_dict.get("data-src", "")
            alt = attrs_dict.get("alt", "")
            if src:
                src = urljoin("https://shopluvbuds.com", src)
                # Filter out icons, logos, sprites
                if not any(skip in src.lower() for skip in (
                    "icon", "logo", "banner", "sprite", "pixel",
                    "tracking", "1x1", "spacer", "badge", "rating"
                )):
                    self.images.append({
                        "src": src,
                        "alt": alt,
                        "in_card": self._in_article,
                    })

    def handle_endtag(self, tag):
        if tag == "article" or tag == "li":
            self._in_article = False


def extract_images_from_html(html: str) -> list[dict]:
    """Extract product images from raw HTML."""
    parser = ImageExtractor()
    parser.feed(html)
    # Assign original positions before sorting
    for i, img in enumerate(parser.images):
        img["_pos"] = i
    # Sort: product-card images first, then by original position
    parser.images.sort(key=lambda x: (not x["in_card"], x.get("_pos", 0)))
    return parser.images


def extract_images_regex_fallback(html: str) -> list[str]:
    """Fallback: extract all plausible product image URLs via regex."""
    urls = set()
    # BigCommerce CDN patterns
    for pattern in [
        r'https://cdn\d+\.bigcommerce\.com/[^"\'\s]+\.(?:jpg|jpeg|png|webp)',
        r'https://shopluvbuds\.com/[^"\'\s]*product[^"\'\s]*\.(?:jpg|jpeg|png|webp)',
        r'data-src="([^"]+)"',
        r'<img[^>]+src="([^"]+)"',
    ]:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            url = match.group(1) if match.lastindex else match.group(0)
            # Filter small/icon images
            for skip in ("icon", "logo", "badge", "rating", "sprite", "pixel"):
                if skip in url.lower():
                    break
            else:
                urls.add(url)
    return list(urls)


async def search_sku(client: httpx.AsyncClient, sku: str) -> tuple[str | None, list[str]]:
    """Search shopluvbuds.com for a SKU and extract images.

    Returns (product_url, [image_urls]).
    """
    search_url = SEARCH_TEMPLATE.format(sku=sku)
    print(f"  Navigating to {search_url}...")

    # Open tab
    r = await client.post("/tabs/open", json={"url": search_url})
    r.raise_for_status()
    tab_info = r.json()
    tab_id = tab_info.get("tab", {}).get("id")

    # Wait for page load (Cloudflare challenges need more time)
    await asyncio.sleep(8)

    # Get raw HTML. /page-html returns raw HTML, not JSON.
    try:
        r = await client.get("/page-html")
        r.raise_for_status()
        html = r.text
    except Exception as e:
        print(f"    /page-html failed: {e}, trying /snapshot fallback...")
        try:
            r = await client.get("/snapshot")
            r.raise_for_status()
            snap = r.json()
            # Snapshot is accessibility tree, not HTML — extract URLs from it
            html = snap.get("snapshot", "")
        except Exception as e2:
            print(f"    /snapshot also failed: {e2}")
            html = ""

    # Close tab
    if tab_id:
        try:
            await client.post("/tabs/close", json={"id": tab_id})
        except Exception:
            pass

    if not html:
        return None, []

    # Extract images
    extracted = extract_images_from_html(html)
    image_urls = [img["src"] for img in extracted]

    # Fallback to regex if parser found nothing
    if not image_urls:
        image_urls = extract_images_regex_fallback(html)

    # Find product page URL
    product_url = None
    for img in extracted:
        if img.get("in_card"):
            # Get the product page from the article link
            pass

    return product_url, image_urls


def pick_best_images(image_urls: list[str], sku: str) -> list[str]:
    """Select the best image URLs for this SKU, preferring largest/most relevant."""
    if not image_urls:
        return []

    # Deduplicate
    seen = set()
    unique = []
    for url in image_urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)

    # Prefer BigCommerce CDN images with larger sizes
    def score(url):
        s = 0
        if "bigcommerce.com" in url:
            s += 2
        # Penalize tiny/thumbnail versions
        if "thumb" in url.lower() or "-tiny" in url.lower():
            s -= 1
        # Bonus for "product" in path
        if "/product/" in url.lower():
            s += 1
        return s

    unique.sort(key=score, reverse=True)
    return unique[:3]  # Max 3 images


async def main():
    token = load_token()
    if not token:
        print("ERROR: Tandem API token not found at ~/.tandem/api-token")
        sys.exit(1)

    # Load catalog
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    # Find SKUs with no images
    missing = [
        sku for sku, data in catalog["products"].items()
        if not data.get("images")
    ]
    print(f"Found {len(missing)} SKUs with missing images")

    # Load checkpoint if exists
    completed = set()
    results = {}
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            cp = json.load(f)
            completed = set(cp.get("completed", []))
            results = cp.get("results", {})
            print(f"Checkpoint: {len(completed)} already processed, resuming...")

    remaining = [s for s in missing if s not in completed]

    if not remaining:
        print("All SKUs already processed. Applying results...")
    else:
        # Connect to Tandem
        print(f"Connecting to Tandem at {TANDEM_URL}...")
        async with httpx.AsyncClient(
            base_url=TANDEM_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=45.0,
        ) as client:
            # Check status
            try:
                r = await client.get("/status")
                r.raise_for_status()
                status = r.json()
                print(f"  Tandem status: {status.get('status', 'unknown')}")
            except Exception as e:
                print(f"ERROR: Cannot reach Tandem at {TANDEM_URL}: {e}")
                print("Make sure Tandem Browser is running.")
                sys.exit(1)

            for sku in remaining:
                print(f"\n[{len(completed) + 1}/{len(missing)}] {sku}")
                try:
                    product_url, image_urls = await search_sku(client, sku)
                    best = pick_best_images(image_urls, sku)
                    if best:
                        results[sku] = {
                            "images": best,
                            "product_url": product_url or SEARCH_TEMPLATE.format(sku=sku),
                        }
                        print(f"    Found {len(best)} image(s): {best[0][:80]}...")
                    else:
                        results[sku] = {"images": [], "product_url": product_url}
                        print(f"    No images found")
                except Exception as e:
                    print(f"    ERROR: {e}")
                    results[sku] = {"images": [], "error": str(e)}

                completed.add(sku)

                # Save checkpoint after each SKU
                with open(CHECKPOINT_PATH, "w") as f:
                    json.dump({"completed": list(completed), "results": results}, f, indent=2)

                # Small delay between requests
                await asyncio.sleep(1)

    # Apply results to catalog
    updated = 0
    for sku, result in results.items():
        if sku in catalog["products"]:
            images = result.get("images", [])
            if images:
                catalog["products"][sku]["images"] = images
                # Update product URL if we found a better one
                if result.get("product_url"):
                    catalog["products"][sku]["url"] = result["product_url"]
                updated += 1
                print(f"  UPDATED {sku}: {len(images)} image(s)")

    if updated > 0:
        # Backup original
        backup_path = CATALOG_PATH.with_suffix(".json.bak")
        with open(backup_path, "w") as f:
            json.dump(catalog, f, indent="\t")
        print(f"Backup saved to {backup_path}")

        # Update stats
        missing_after = sum(1 for _, d in catalog["products"].items() if not d.get("images"))
        catalog["stats"]["products_with_images"] = len(catalog["products"]) - missing_after
        catalog["stats"]["products_without_images"] = missing_after

        # Save updated catalog
        with open(CATALOG_PATH, "w") as f:
            json.dump(catalog, f, indent="\t")
        print(f"\n{CATALOG_PATH} updated — {updated} SKUs now have images")
        print(f"Missing before: {len(missing)}, missing after: {missing_after}")

        # Clean up checkpoint on full success
        if missing_after == 0:
            CHECKPOINT_PATH.unlink(missing_ok=True)
            print("All images resolved — checkpoint removed.")
    else:
        print("\nNo changes to apply.")


if __name__ == "__main__":
    asyncio.run(main())
