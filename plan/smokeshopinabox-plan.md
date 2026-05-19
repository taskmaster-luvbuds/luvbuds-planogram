# Smoke Shop In A Box — Full-Catalog Planogram Plan

## Audit: Lattice / Lens / Prism / Witness

### WITNESS — What Is Directly Seen

**Existing codebase** (`smokeshopinboxplanogram/`):
- `planogram.html` — 1,064-line single-file HTML/CSS/JS application. Functional drag-and-drop planogram tool built for Fine Fettle (29 products). Shelf-based layout with pixel scaling (PX=16), multi-display support, order export, product index sidebar. No build step, no dependencies.
- `index.html` — identical copy of planogram.html. **Duplicate file.**
- `transcription march 19.md` — Fine Fettle stakeholder meeting transcript. Key requirements: print/export button, CSV import template, Joe Hurwitz validation.
- `BigComOrderCreationPayload.txt` — real BigCommerce Orders V2 API JSON. Shows exact field structure needed for order export.
- `.claude/settings.local.json` — **CRITICAL: contains hardcoded GitHub PAT.** Must be rotated and removed.
- `plan/` — empty directory (target for this document).

**Product catalog** (`csv/` — 6 enriched files):

| File | SKUs | Categories | Dimension Gaps |
|------|------|------------|----------------|
| Glass only SSIB options - green | 31 | Dab Accessories, Lighters, Smoking Accessories, Glass Hand Pipe, Water Pipe | 7 blank |
| Glass only SSIB options - yellow | 3 | Water Pipe (Scientific) | 0 blank |
| Herb only SSIB options - green | 75 | Grinders, Ashtrays, Lighters, Cones, Papers, Hand Pipe, Water Pipe, Storage, Vape | ~30+ blank |
| Herb only SSIB options - yellow | 13 | Cones, Dugout, Flower Vape, Silicone Hand Pipe, WP Silicone | several blank |
| Vape only SSIB options - green | 23 | Atomizers, Cart Batteries, Concentrate Vape, E-Nectar, Flower Vape | several blank |
| Vape only SSIB options - yellow | 10 | Cart Batteries, Concentrate Vape, Flower Vape | few blank |
| **TOTAL** | **~155** | **25+ subcategories** | **59+ incomplete** |

**Existing tool constants:**
```
PX = 16 pixels per inch
SW = 27.5" shelf width
SD = 10.5" shelf depth
SHELVES: top (12" clearance), mid (12" clearance), bot (10.5" clearance)
```

**Existing tool structures:**
- Product catalog `P` — hardcoded JS object with 29 entries: `{n, w, h, d, c}`
- BigCommerce mapping `BC` — hardcoded JS object with `{pid, vid, name, price, cost, brand}`
- Image path function `ip(id)` — returns local `images/` PNG paths with special-case mappings
- Category CSS: `cat-papers`, `cat-pipes`, `cat-bulk`, `cat-batteries`, `cat-accessories`, `cat-insert`
- Multi-display state: `displays[]` array with create/clone/remove functions
- Drag-and-drop: cross-shelf, cross-display with ghost element
- Order export: `generateOrderCSV()` builds BigCommerce JSON, excludes inserts
- Stats panel: shelf utilization percentages

---

### LATTICE — Structural Framework

The existing architecture is a **single-file monolithic JavaScript application** with three hardcoded data layers that must become data-driven:

```
┌─────────────────────────────────────────────────┐
│                 planogram.html                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Catalog P │  │  BC Map  │  │ Image paths   │  │
│  │ (29 SKUs) │  │ (prices) │  │ (local PNGs)  │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
│  ┌──────────────────────────────────────────┐    │
│  │         Rendering Engine                  │    │
│  │  ┌────────┐  ┌────────┐  ┌────────────┐  │    │
│  │  │Shelf   │  │Drag/   │  │Order       │  │    │
│  │  │Layout  │  │Drop    │  │Export      │  │    │
│  │  └────────┘  └────────┘  └────────────┘  │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

**Target architecture — data-driven with CSV pipeline:**

```
┌────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  6 CSV files   │────▶│  build_catalog.  │────▶│  catalog.json   │
│  (~155 SKUs)   │     │  py              │     │  (single source)│
└────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    planogram-v2.html                          │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │ catalog.json     │  │ CDN image URLs   │                  │
│  │ (fetched at load)│  │ (from CSV cols)  │                  │
│  └──────────────────┘  └──────────────────┘                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │         Rendering Engine (preserved + extended)       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │    │
│  │  │Shape     │  │Category  │  │Multi-Display     │   │    │
│  │  │Renderer  │  │Expansion │  │Layout            │   │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Key structural changes:**

1. **Product catalog**: Hardcoded `P` object → `catalog.json` fetched at load. Generated by a Python script that reads all 6 CSVs and outputs a single JSON file with normalized fields.

2. **Image paths**: `ip(id)` returning local PNGs → direct BigCommerce CDN URLs from CSV `Image URLs` column. Shape-based fallback where no image exists.

3. **Pricing map**: Hardcoded `BC` object → CSV revenue/profit columns used to derive unit price, with BigCommerce product_id/variant_id populated where available.

4. **Categories**: 6 hardcoded CSS classes → data-driven category system generated from `Primary Category` + `Subcategory 1` CSV columns, with auto-assigned color palette.

5. **Shape renderer**: New rendering mode that draws colored rectangles sized to product dimensions (W×H at PX scale). This is the **primary** rendering mode per user directive — images are secondary.

---

### LENS — Focused Gap Analysis

**Gap 1 — Data Pipeline (BLOCKING)**
The existing tool has 29 hand-maintained product entries. Scaling to ~155 SKUs requires a CSV→JSON pipeline. Without this, every catalog change requires manual JS editing.

**Gap 2 — Shape-Based Rendering (BLOCKING)**
User directive: "we have to use shapes for now and the dementions to make sure we have the size set up." The existing tool renders products as thumbnails with a background image from `images/`. No shape-based fallback exists. The new tool must render products as dimensionally-accurate colored rectangles first, with image overlay as enhancement.

**Gap 3 — Image Source Migration**
Existing images load from local `images/` directory (e.g., `images/ZZ114-48 copy.png`). The enriched CSVs contain BigCommerce CDN URLs (`cdn11.bigcommerce.com/s-ijm7dw7yvr/...`). The new tool must use these remote URLs. For SKUs without images, the shape renderer is the primary display.

**Gap 4 — Category System**
Existing: 6 category CSS classes (`papers`, `pipes`, `bulk`, `batteries`, `accessories`, `insert`). New catalog has 25+ subcategories across 6 product lines. Need a color assignment system that distinguishes categories while staying visually coherent. Each product line (Glass green, Glass yellow, Herb green, Herb yellow, Vape green, Vape yellow) is a separate "department" with its own subcategory palette.

**Gap 5 — Dimension Handling**
59+ SKUs (38%) have blank or incomplete dimensions. The planogram's core value is spatial layout — missing dimensions break the shape renderer. Categories with the most gaps:
- ZAZA grinders (18 color/size variants): all blank — need manual measurement or manufacturer specs
- Eyce silicone products: mostly blank
- Various accessories (screens, tips, small items): low spatial impact but still needed

**Gap 6 — Multi-Display Layout Strategy**
29 products fit on 3 shelves in a single display. 155 products need organization across 4-6 displays, likely grouped by product line:
- Display 1: Vape — Green (cart batteries, concentrate vapes)
- Display 2: Vape — Yellow (premium batteries, Puffco)
- Display 3: Herb — Green (cones, papers, grinders, accessories)
- Display 4: Herb — Yellow (RAW cones, dugouts, silicone pipes)
- Display 5: Glass — Green (bangers, hand pipes, water pipes)
- Display 6: Glass — Yellow (scientific water pipes, downstems)

**Gap 7 — BigCommerce Order Export**
Existing `BC` mapping has hardcoded product_id/variant_id/price/cost/brand for 29 SKUs. New catalog needs this populated for ~155 SKUs. The `BigComOrderCreationPayload.txt` shows the exact JSON structure required. Revenue and profit columns in CSVs can derive unit pricing.

**Gap 8 — Print/Export Image**
Transcription requirement: "a print export button." The existing tool has no screenshot or print-to-PDF capability. Need a print stylesheet + browser print trigger, or a canvas-based export.

**Gap 9 — Security**
Exposed GitHub PAT in `.claude/settings.local.json`. Must be rotated at github.com/settings/tokens and the file sanitized.

**Gap 10 — File Duplication**
`planogram.html` and `index.html` are identical. One should be canonical; the other removed or replaced with a redirect.

---

### PRISM — Multi-Perspective Requirements

**Shopper perspective:**
- Quick visual scan: products grouped by category, not by SKU number
- Category headers visible at shelf level
- High-demand items at eye level (mid shelf)
- Impulse items at bottom shelf (accessible)
- Premium/high-value items at top shelf (aspirational)

**Store operator perspective:**
- Order generation from layout → BigCommerce JSON → paste into order form
- Restock awareness: "available physical" column shows current inventory
- Shelf utilization stats: how full is each display
- Print layout for store setup reference

**Product-line physical realities:**
- **Vape batteries**: small footprint (1-2" W), high value density. Fit many per shelf column. Need electrical separation (no stacking). Display inserts like battery trays.
- **Glass water pipes**: large (3-7" W, 7-12" H), fragile. Need shelf clearance verification per item. Low units-per-column (often 1).
- **Cones/papers**: lightweight, stackable. High volume per column. Boxed displays create their own footprint.
- **Grinders**: heavy, medium footprint (2-3" W). Shelf weight consideration. Display at mid-to-low height.
- **Concentrate vapes (Puffco)**: premium, medium footprint, high value. Security consideration — display at top or behind counter.
- **Silicone pipes**: irregular shapes, lightweight. Flexible placement.

**Rendering perspective:**
- Shape mode: colored rectangles with SKU label overlay → dimensionally accurate layout
- Image mode: product photo overlaid on shape at correct scale → visual confirmation
- Mixed mode: shapes with images where available, pure shapes where not
- Category color must be visible even in image mode (border or badge)

---

## Implementation Plan

### Phase 1 — Data Pipeline (CSV → JSON)

**Script**: `build_catalog.py`

Read all 6 enriched CSVs, normalize columns, output `catalog.json`:

```json
{
  "products": {
    "SKU": {
      "name": "Description",
      "category": "Primary Category",
      "subcategory": "Subcategory 1",
      "qtySold": 1234,
      "revenue": 12345.67,
      "available": 100,
      "profit": 1234.56,
      "url": "https://shopluvbuds.com/...",
      "images": ["https://cdn11.bigcommerce.com/..."],
      "width": 1.5,
      "height": 3.2,
      "depth": 0.7,
      "line": "vape-green"
    }
  },
  "lines": {
    "vape-green": { "label": "Vape — Green", "color": "#1B5E20" },
    "vape-yellow": { "label": "Vape — Yellow", "color": "#F9A825" },
    "herb-green": { "label": "Herb — Green", "color": "#004D40" },
    "herb-yellow": { "label": "Herb — Yellow", "color": "#F57F17" },
    "glass-green": { "label": "Glass — Green", "color": "#01579B" },
    "glass-yellow": { "label": "Glass — Yellow", "color": "#FF8F00" }
  },
  "categories": {
    "Cart Batteries": "#1B5E20",
    "Concentrate Vape": "#4A148C",
    ...
  }
}
```

**Tasks:**
1. Write `build_catalog.py` to parse all 6 CSVs and output unified JSON
2. Parse dimension strings (`1.5" x 3.2" x 0.7"`) into numeric inches
3. Derive unit price from `revenue / qtySold` where available
4. Assign each SKU to a product line based on source CSV filename
5. Generate category color palette for all 25+ subcategories
6. Flag SKUs with missing dimensions for manual measurement

### Phase 2 — Shape-Based Renderer

**Modify planogram.html → planogram-v2.html**

**2a. Product rendering engine:**
- New render mode: `drawProductShape(ctx, product, x, y, width_px, height_px)`
- Colored rectangle filled with category color
- SKU code + short name label centered in rectangle
- Product image overlaid if available (loaded from CDN URL)
- Depth indicator: subtle 3D edge on shapes to show stacking
- Toggle between shape-only / image-overlay / mixed modes

**2b. Dimension-based sizing:**
- All product rectangles sized by actual W×H at PX scale
- Products without dimensions: use category default sizes (estimated averages per subcategory)
- Visual indicator (dashed border) on products using estimated dimensions
- Shelf clearance check: product height must fit within shelf `cl` value

**2c. Depth stacking:**
- Existing back-row logic preserved: `const D = SD / product.depth` units per column
- Visual: back product rendered behind front, peeking above
- Depth utilization shown in stats panel

### Phase 3 — Data-Driven Architecture

**3a. Replace hardcoded catalog:**
- Remove `P` object, replace with `fetch('catalog.json')` at init
- Remove `BC` object, embed pricing in catalog.json product entries
- Remove `ip(id)` function, use `product.images` array from catalog

**3b. Category system expansion:**
- Remove 6 hardcoded CSS classes
- Generate category stylesheet dynamically from catalog.json categories map
- Each subcategory gets a distinct color derived from a generated palette
- Product line (green/yellow) shown as a badge/tag on each item

**3c. Multi-display strategy:**
- Default config: 6 displays, one per product line
- Each display pre-loaded with its line's products
- Display label shows product line name
- Stats aggregated per-display and fleet-wide

### Phase 4 — Image Integration

**4a. CDN image loading:**
- Load product images from BigCommerce CDN URLs in CSV
- Lazy-load images as they become visible
- Fallback to shape rendering on load failure
- Image caching via browser cache (CDN handles this)

**4b. Image-to-shape ratio:**
- Shape mode is default — renders instantly
- Image mode is toggle — loads asynchronously, replaces shape fill
- Products with images: show image thumbnail in sidebar
- Products without: show shape preview in sidebar

### Phase 5 — BigCommerce Order Export

**5a. Export format:**
- Match exact JSON structure from `BigComOrderCreationPayload.txt`
- Required fields per line item: `product_id`, `variant_id`, `order_address_id`, `name`, `sku`, `base_price`, `price_ex_tax`, `base_total`, `quantity`, `width`, `height`, `depth`, `base_cost_price`, `cost_price_inc_tax`, `cost_price_ex_tax`, `brand`, `weight`, `fulfillment_source`, `applied_discounts`, `product_options`, `configurable_fields`
- Generate as downloadable JSON file (matching existing `generateOrderCSV()` pattern)

**5b. Pricing:**
- Unit price derived from CSV `revenue / qtySold`
- Cost price from `(revenue - profit) / qtySold`
- Brand extracted from product description where identifiable (Pulsar, Lookah, SirEEL, Yocan, etc.)

### Phase 6 — UI/UX Improvements

**6a. Print/Export button:**
- Add print stylesheet (`@media print`) that hides sidebar, shows only displays
- Browser print trigger button
- Alternative: canvas-based PNG export of full layout

**6b. Product index improvements:**
- Filter by product line (Glass/Herb/Vape), category, dimension status
- Search by SKU or description
- Show "missing dimensions" filter
- Quantity stepper per product

**6c. Search and filter:**
- Category filter chips
- Dimension status: "has dimensions" / "estimated"
- Revenue/sales sorting (identify top sellers for prime placement)

### Phase 7 — Dimension Gap Resolution

**Priority 1 (high spatial impact):**
- ZAZA grinders (18 variants): request manufacturer specs or measure physically
- Eyce silicone pipes and water pipes: request specs
- Large water pipes without dimensions

**Priority 2 (medium spatial impact):**
- Accessories with standard sizes (screens, tips, downstems)
- Use industry-standard defaults where dimensions are standard

**Priority 3 (low spatial impact):**
- Small items (carb caps, lighter cases): use estimated small-rectangle placeholder

### Phase 8 — Security + Hygiene

**CRITICAL — Before any commit:**
1. Rotate GitHub PAT at github.com/settings/tokens
2. Remove `.claude/settings.local.json` from the repo or sanitize the token
3. Add `.claude/settings.local.json` to `.gitignore`
4. Verify no other secrets in committed files

**File cleanup:**
1. Decide canonical filename: `planogram.html` or `index.html`
2. Remove duplicate or replace with meta-refresh redirect
3. Add `.gitignore` entries for generated files (catalog.json if build-artifact)

---

## Priority Order

| Order | Phase | Why First |
|-------|-------|-----------|
| 1 | Phase 8 (Security) | Exposed token is active vulnerability |
| 2 | Phase 1 (Data Pipeline) | Everything depends on having normalized product data |
| 3 | Phase 2 (Shape Renderer) | Core user requirement — "use shapes for now" |
| 4 | Phase 3 (Data-Driven) | Enables scaling past 29 SKUs |
| 5 | Phase 4 (Images) | Enhancement on top of shape foundation |
| 6 | Phase 7 (Dimensions) | Parallel track — unblocks accurate rendering |
| 7 | Phase 5 (Order Export) | Business value — enables store ordering |
| 8 | Phase 6 (UI/UX) | Polish — print, search, filters |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| 59+ SKUs lack dimensions | Can't render accurate layout | Category defaults + visual "estimated" indicator + manual measurement backlog |
| BigCommerce CDN URLs may expire/change | Broken images | Shape fallback is primary; images are enhancement |
| CSV data may not include BigCommerce product_id/variant_id | Can't generate valid order JSON | Derive from product URL or leave as `0` with SKU as identifier |
| Single-file HTML may become unwieldy at 2K+ lines | Maintenance burden | Keep single-file; extract catalog to JSON; if it crosses 3K lines, split JS to separate file |
| GitHub PAT already exposed in git history | Credential leak | Rotate immediately; git history still contains old token — accept risk or rewrite history |
