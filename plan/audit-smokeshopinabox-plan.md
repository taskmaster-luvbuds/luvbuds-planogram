# Audit: smokeshopinabox-plan.md — 9-Phase Epistemic Audit

**Auditor**: delphi (Infrastructure Architect)
**Artifact under audit**: `plan/smokeshopinabox-plan.md` (370 lines, written 2026-05-19)
**Methodology**: Lattice / Lens / Prism / Witness — claim extraction, evidence grounding, gap/blind-spot analysis, coherence scoring, dissonance mapping

---

## PHASE 1: CLAIM EXTRACTION

Every explicit and implicit claim in the artifact, numbered.

### Explicit Claims

| # | Claim | Location (line) |
|---|-------|-----------------|
| C1 | planogram.html is a 1,064-line single-file HTML/CSS/JS application | L8 |
| C2 | The existing tool has no build step and no dependencies | L8 |
| C3 | The existing tool was built for Fine Fettle with 29 products | L8 |
| C4 | The existing tool supports pixel scaling at PX=16 pixels per inch | L8,28 |
| C5 | The existing tool has multi-display support, order export, and a product index sidebar | L8 |
| C6 | index.html is an identical copy of planogram.html — a duplicate file | L9 |
| C7 | transcription march 19.md contains key requirements: print/export button, CSV import template | L10 |
| C8 | BigComOrderCreationPayload.txt shows the exact BigCommerce Orders V2 JSON field structure | L11 |
| C9 | .claude/settings.local.json contains a hardcoded GitHub PAT token | L12 |
| C10 | The exposed token must be rotated and the file sanitized | L12 |
| C11 | The plan/ directory was empty when the plan was written | L13 |
| C12 | The Glass green CSV contains 31 SKUs, 0 blank dimensions | L19 |
| C13 | The Glass yellow CSV contains 3 SKUs, 0 dimensions blank | L20 |
| C14 | The Herb green CSV contains 75 SKUs, ~30+ blank dimensions | L21 |
| C15 | The Herb yellow CSV contains 13 SKUs, several blank dimensions | L22 |
| C16 | The Vape green CSV contains 23 SKUs, several blank dimensions | L23 |
| C17 | The Vape yellow CSV contains 10 SKUs, few blank dimensions | L24 |
| C18 | Total catalog is ~155 SKUs across 25+ subcategories | L25 |
| C19 | 59+ SKUs have incomplete or missing dimensions (38%) | L25 |
| C20 | Shelf width is 27.5", shelf depth is 10.5" | L29-30 |
| C21 | Three shelves exist: top (12" clearance), mid (12" clearance), bot (10.5" clearance) | L31 |
| C22 | The existing product catalog P is a hardcoded JS object with 29 entries | L36 |
| C23 | The BigCommerce mapping BC is a hardcoded JS object | L37 |
| C24 | The image path function ip(id) returns local images/ PNG paths | L38 |
| C25 | Six CSS category classes exist: papers, pipes, bulk, batteries, accessories, insert | L39 |
| C26 | The existing tool has cross-shelf, cross-display drag-and-drop with ghost elements | L41 |
| C27 | Order export generates BigCommerce JSON, excludes insert items | L42 |
| C28 | A Python script (build_catalog.py) should read 6 CSVs and output catalog.json | L72,95,185 |
| C29 | Image paths should switch from local PNGs to BigCommerce CDN URLs | L97 |
| C30 | Unit pricing can be derived from CSV revenue/qtySold | L99,296 |
| C31 | Cost price can be derived from (revenue - profit)/qtySold | L297 |
| C32 | Categories should expand from 6 hardcoded CSS classes to a data-driven system from CSV columns | L101 |
| C33 | Category colors should be auto-assigned from a generated palette | L104 |
| C34 | Shape-based rendering should be the primary rendering mode; images are secondary | L105 |
| C35 | Data pipeline (CSV→JSON) is BLOCKING — must come first among implementation phases | L109 |
| C36 | Shape-based rendering is BLOCKING — the existing tool has no shape fallback | L112 |
| C37 | ZAZA grinders have 18 color/size variants, all with blank dimensions | L123 |
| C38 | Eyce silicone products have mostly blank dimensions | L124 |
| C39 | 155 products need 4-6 displays organized by product line | L128 |
| C40 | Products should be grouped into 6 displays matching the 6 product lines | L129-134 |
| C41 | BigCommerce order export needs 22 specific JSON fields per line item | L292 |
| C42 | Brand can be extracted from product description text | L298 |
| C43 | The existing tool has no screenshot or print-to-PDF capability | L140 |
| C44 | Phase 8 (Security) should be executed first in priority order | L351 |
| C45 | Category default sizes can substitute for missing dimensions | L246,366 |
| C46 | Shape fallback protects against CDN image URL expiration or breakage | L367 |
| C47 | Single-file HTML remains viable but may become unwieldy past 2K lines | L369 |
| C48 | The 3K-line threshold is where JS should split to a separate file | L369 |
| C49 | The GitHub PAT is already exposed in git history (not just working tree) | L370 |
| C50 | Puffco products are high-value items needing security consideration | L170 |
| C51 | Vape batteries need electrical separation — no stacking | L166 |
| C52 | Glass water pipes need shelf clearance verification per item | L167 |
| C53 | Cones/papers are lightweight and stackable with high volume per column | L168 |
| C54 | Grinders are heavy with medium footprint — shelf weight is a consideration | L169 |
| C55 | The existing drag-and-drop, multi-display, and order export code can be preserved | L83-88 |
| C56 | build_catalog.py should parse dimension strings in the format `1.5" x 3.2" x 0.7"` into numeric inches | L226 |
| C57 | Each SKU's product line is derivable from its source CSV filename | L228 |
| C58 | The planogram should default to shape-only mode and load images asynchronously | L283-284 |
| C59 | Catalog.json should be fetched at page load time | L258 |
| C60 | A print stylesheet with @media print can hide the sidebar for printing | L303 |
| C61 | Browser print trigger is a viable export mechanism | L304 |

### Implicit Claims

| # | Claim | Source |
|---|-------|--------|
| I1 | The existing rendering engine architecture can be extended rather than replaced | "Rendering Engine (preserved + extended)" L85 |
| I2 | The CSV data (qtySold, revenue, profit) is accurate and current | Used as pricing source throughout Phase 5 |
| I3 | Store operators are the primary end users of the planogram | "Store operator perspective" section L159 |
| I4 | The 27.5"×10.5" shelf dimensions are correct for all product lines | No per-line shelf adjustment suggested |
| I5 | Python is the right language for build_catalog.py | Chosen without alternatives discussed |
| I6 | catalog.json should be a build artifact, not committed to git | ".gitignore entries for generated files (catalog.json if build-artifact)" L343 |
| I7 | The single-file architecture should be preserved as long as possible | "Keep single-file; extract catalog to JSON; if it crosses 3K lines, split JS" L369 |
| I8 | 6 displays × 3 shelves is sufficient shelf space for 155 products | Not calculated — asserted without sq-in math |
| I9 | Auto-generated category colors can produce 25+ visually distinguishable colors | "Generate category color palette for all 25+ subcategories" L229 |
| I10 | The existing drag-and-drop UX scales from 29 to 155 products without redesign | Drag-and-drop preserved without modification L41 |
| I11 | Fetching catalog.json at load succeeds and the failure case is negligible | No error handling or retry logic specified for the fetch |
| I12 | The CSV column structure is consistent enough for a single parser | CSVs have different schemas (some lack "Primary Category") |
| I13 | The BigCommerce CDN base URL (cdn11.bigcommerce.com/s-ijm7dw7yvr) is stable long-term | Used as image source without URL stability caveat |
| I14 | The planogram is for LuvBuds internal use / B2B sales tool | Audience not stated but context implies this |
| I15 | The plan author has read every CSV file and every line of planogram.html | Detail level implies full codebase knowledge |
| I16 | Phase ordering in the Priority Order table is the execution sequence | "Priority Order" table L349 lists phases 8,1,2,3,4,7,5,6 |
| I17 | Shape rendering can convey all necessary product information for shelf layout decisions | Shape is "primary mode" L105 |

---

## PHASE 2: EVIDENCE AUDIT

### Classification Summary

| Category | Count | Percentage |
|----------|-------|------------|
| VERIFIED | 29 | 37% |
| UNVERIFIED | 36 | 46% |
| CONTRADICTED | 2 | 3% |
| UNTESTABLE | 11 | 14% |
| **TOTAL** | **78** | 100% |

### Detailed Classification

#### VERIFIED (evidence exists)

C1, C2, C3, C4, C5 — The file was read in full; these claims match the observed code.
C6 — Confirmed by prior session file comparison (planogram.html and index.html are byte-identical duplicates).
C8 — BigComOrderCreationPayload.txt was read; the JSON structure is confirmed.
C9 — settings.local.json was read; the token string is present.
C11 — Confirmed: `ls plan/` returned empty before the plan was written.
C12-C17 — All 6 CSVs were read in full; SKU counts match.
C18 — Sum of CSV SKU counts: 31+3+75+13+23+10 = 155. VERIFIED.
C19 — 59+ incomplete confirmed by scanning dimension columns across all 6 CSVs.
C20, C21 — These are the literal constants in planogram.html line ~10-15.
C22, C23, C24, C25, C26, C27 — All confirmed by reading planogram.html source.
C7 — transcription march 19.md was read; Joe Hurwitz quote and requirements are present.
C37 — ZAZA grinders confirmed with blank dimensions in Herb green CSV.
C43 — planogram.html has no @media print rules, no canvas export, no window.print() call. VERIFIED.
C49 — The token is in the committed file, not just in the working tree (confirmed by git log showing the file tracked).

#### UNVERIFIED (plausible, no evidence presented)

C28 — No build_catalog.py exists yet. The plan asserts it should be written but provides no evidence of feasibility (e.g., a sample CSV parse test).
C29 — BigCommerce CDN URLs are present in the CSVs, but no evidence that they'll work as img src in a browser (CORS headers, hotlink protection untested).
C30, C31 — Revenue/qtySold gives an average unit price, but the actual unit price may differ (bulk pricing, discounts, price changes over time). Evidence needed: sample calculation verified against known product prices.
C32, C33 — 25+ distinguishable colors from an auto-generated palette is a known-hard design problem. No palette generation algorithm or color-distance threshold specified.
C34 — Asserted as user requirement but the user quote says "use shapes for now" — "for now" implies temporary, not "primary mode permanently."
C35, C36 — BLOCKING status is the author's judgment; no evidence that work literally cannot proceed without these.
C39, C40 — 155 products across 6 displays × 3 shelves = 18 shelves × 12 columns = 216 column slots. The math might work but isn't shown. Column depth for back-row products isn't factored.
C41 — The 22 fields are listed without evidence that all are required (some may be optional in the BigCommerce API).
C42 — Brand extraction from description is pattern-matching on known brand names. Evidence needed: test extraction against all 155 descriptions to measure recall rate.
C44 — Security is listed first in priority but the plan itself says Phase 8. The phases are numbered 1-8, not by priority. This ordering creates ambiguity.
C45 — "Category defaults" for missing dimensions are mentioned but no defaults are specified. What is the default size for a grinder? A water pipe?
C46 — Shape fallback as protection against CDN breakage is logical but untested. The CDN may have CORS issues, or the shape may render at wrong dimensions.
C47, C48 — 2K and 3K line thresholds are arbitrary. No evidence that the file will reach these sizes.
C50-C54 — Product-line physical characteristics are domain knowledge assertions. None are sourced from manufacturer specs.
C55 — The existing code preservation claim is an intent, not a proven capability. The code has never been tested with 155 products.
C56 — Dimension parsing regex/algorithm is specified but not tested against the actual CSV dimension strings (some have only height, some have extra text).
C57 — Product line derivation from filename is fragile. "Vape only SSIB options - green - enriched.csv" → "vape-green" requires parsing logic that isn't defined.
C60, C61 — @media print for a canvas/layout-based tool often fails because canvas content isn't in the DOM print flow. Evidence needed: a test print of the existing tool.

Implicit claims I1-I17 are all UNVERIFIED by definition (they're implicit).

#### CONTRADICTED

**C20/C21 (Shelf dimensions) vs C52 (Glass water pipes need clearance verification)**: The shelves have 12"/12"/10.5" clearance. Several water pipes in the catalog are 7.5"–9.75" tall. A 9.75" product on a 10.5" clearance shelf has only 0.75" of headroom — technically fits but practically too tight for a fragile glass item. The plan asserts both "shelf dimensions are 27.5×10.5 with 12"/12"/10.5" clearance" AND "glass pipes need clearance verification" without recognizing that the existing clearance values may be insufficient for the product mix.

**C34 (Shape is primary mode) vs I17 (Shapes convey necessary info) vs C46 (Images are secondary enhancement)**: The user quote is "we have to use shapes for now" — the word "for now" directly contradicts the plan's framing of shapes as the permanent primary mode. The plan has reified a temporary constraint into a permanent architecture decision without acknowledging this distinction.

#### UNTESTABLE

C10 — "Must be rotated" is a security imperative, not a falsifiable claim about the artifact.
C30/C31 — Without knowing which products had price changes, bulk discounts, or promotional pricing, the derived prices can't be definitively verified or falsified without external data.
I4, I8, I9, I10, I14, I15, I16, I17 — These are all design judgments or assertions about future states. Some would become testable after implementation but are currently unfalsifiable.

---

## PHASE 3: GAP ANALYSIS

### CRITICAL Gaps (blocks success)

**G-C1: No success criteria defined for any phase**
What is missing: Measurable completion conditions. What does "Phase 1 done" mean? "All 155 SKUs parse without error" vs "catalog.json is generated" vs "catalog.json is validated against CSV source."
Why it matters: The implementer cannot know when a phase is complete. Phases blend into each other. The operator cannot verify delivery.
Severity: CRITICAL

**G-C2: No test strategy**
What is missing: How to verify the shape renderer draws correctly sized rectangles. How to verify the order JSON is valid. How to verify 155 SKUs all appear. How to verify drag-and-drop still works.
Why it matters: A planogram with wrong dimensions is worse than no planogram — it actively misleads about shelf fit. Without tests, the first validation is a store operator discovering a Puffco Peak doesn't fit where the planogram says it does.
Severity: CRITICAL

**G-C3: No CSV schema reconciliation strategy**
What is missing: The 6 CSVs have different column structures. Herb CSVs lack "Primary Category." Some files have "Description," others have "Description" under a different index. The "Subcategory 1" column exists in some but not all files. The plan assumes a single build_catalog.py can parse all 6 without addressing schema differences.
Why it matters: The parser will either fail on mismatched columns or silently produce incorrect category assignments. Either outcome breaks the category system and display organization.
Severity: CRITICAL

**G-C4: No rollback or fallback strategy**
What is missing: If planogram-v2.html doesn't work — if the shape renderer is broken, if catalog.json fails to load, if the BigCommerce CDN blocks hotlinking — what happens? The plan says "shape fallback protects against CDN breakage" but what protects against shape renderer breakage?
Why it matters: The existing planogram.html is functional and validated by a customer ("I f****** love it" — Joe Hurwitz). Destroying it without a revert path is an unacceptable risk.
Severity: CRITICAL

**G-C5: catalog.json fetch failure not handled**
What is missing: The plan says catalog.json is "fetched at load" (L80, L258). No error handling, retry logic, cached fallback, or offline mode is mentioned.
Why it matters: If catalog.json is 404, CORS-blocked, or the CDN is down, the entire application is a blank page. The current tool works because all data is inline — this is a degradation from current reliability.
Severity: CRITICAL

### HIGH Gaps (significantly weakens)

**G-H1: No time or effort estimates**
What is missing: How long will build_catalog.py take? How long to implement the shape renderer? Which phases can happen in parallel?
Why it matters: Without estimates, the operator cannot allocate resources, set expectations with stakeholders, or detect when a phase is taking too long.
Severity: HIGH

**G-H2: No stakeholder identified**
What is missing: Who is this planogram for? Fine Fettle (existing customer)? LuvBuds directly? Multiple stores? The plan says "store operator perspective" but doesn't name the actual customer.
Why it matters: Different customers have different product mixes, shelf configurations, and ordering workflows. Building for "generic store operator" produces a tool that serves no specific store well.
Severity: HIGH

**G-H3: No mention of existing preset configs (CONFIGS object)**
What is missing: The existing tool has 4 preset configurations (all, spread, papers, hardware) in a CONFIGS object. The plan doesn't mention whether these should be preserved, replaced, or expanded for the new catalog.
Why it matters: Presets are the primary usability feature for store operators who don't want to drag 155 items manually. Without preset strategy, the 155-SKU planogram may be unusable at scale.
Severity: HIGH

**G-H4: Dimension parsing edge cases not addressed**
What is missing: The CSVs contain dimension strings like `"1.53"" x 3.22"" x 0.7"""` (escaped double quotes), `"4.75"" x 9.75"" x 3.5"""`, blank fields, and potentially malformed strings. The plan says "Parse dimension strings into numeric inches" without addressing these edge cases.
Why it matters: A single parse failure could silently produce a 0×0×0 product that either crashes the renderer or renders invisibly.
Severity: HIGH

**G-H5: No shelf configuration validation for new product mix**
What is missing: The plan preserves the existing shelf config (27.5"×10.5", 12"/12"/10.5" clearance) without validating it against the 155-SKU catalog. Several water pipes are 9.75" tall (top shelf has 12" clearance — fits but tight). Puffco Peak Pro 2 dimensions aren't in the CSV — how do we know it fits?
Why it matters: A planogram that places products on shelves they physically cannot fit on undermines the tool's core purpose.
Severity: HIGH

### MEDIUM Gaps (notable omission)

**G-M1: No product index sidebar scaling strategy**
The sidebar currently shows 29 products. At 155 products, the scrollable list needs search, filters, and likely virtualization. The plan mentions filters in Phase 6 but not the basic performance concern.
Severity: MEDIUM

**G-M2: No display insert strategy**
The existing tool has an "insert" category for non-product fixtures (battery trays, water pipe stands). The plan doesn't mention whether inserts still exist or how they're generated for the new catalog.
Severity: MEDIUM

**G-M3: No print layout specification**
The plan says "@media print that hides sidebar, shows only displays" but doesn't address: pagination across 6 displays, display labels in print, scale-to-fit for different paper sizes, or what happens when displays don't fit on one page.
Severity: MEDIUM

**G-M4: catalog.json versioning not addressed**
If catalog.json is a build artifact (implied by .gitignore suggestion L343), how is it versioned? Is it regenerated from CSV on every change? What if the CSV changes but catalog.json isn't regenerated?
Severity: MEDIUM

**G-M5: No accessibility considerations**
155 draggable colored rectangles with SKU labels — is any of this keyboard-navigable? Screen-reader compatible? The original tool likely has the same gap, but scaling from 29 to 155 products amplifies it.
Severity: MEDIUM

**G-M6: The GitHub remote is inaccessible**
The plan was committed locally but `git push origin master` failed with "Repository not found." The plan doesn't mention this or propose a new remote.
Severity: MEDIUM

### LOW Gaps (nice to have)

**G-L1: No browser compatibility matrix**
**G-L2: No offline/PWA capability**
**G-L3: No analytics or usage tracking**
**G-L4: No mention of the BigCommerce CDN image dimensions (actual pixel size of product photos — relevant for image overlay rendering)**

---

## PHASE 4: BLIND SPOT ANALYSIS

### Blind Spot 1: Infrastructure Architect Framing

**What is not being seen**: The plan treats the planogram as a system migration problem (hardcoded → data-driven, local → CDN, 6 categories → 25). It does not see it as a product design problem.

**Why invisible**: The author (delphi) is the Infrastructure Architect daemon. The framing is structural — layers, pipelines, data flow. The plan sees JSON schemas and rendering engines but not user journeys.

**Damage if unaddressed**: The resulting tool may be architecturally sound but unusable. A store operator doesn't care about catalog.json — they care about "can I lay out my store in 10 minutes and print the result?" The plan doesn't answer that question.

### Blind Spot 2: The Missing Iteration Model

**What is not being seen**: The plan presents 8 linear phases. The user said "use shapes for now" — which implies they expect to iterate. A 2-display demo with 40 products shown to a stakeholder next week is more valuable than a perfect 6-display system delivered in 6 weeks.

**Why invisible**: The plan's structure (phases 1-8 with priority order) naturally implies waterfall delivery. The author is optimizing for completeness — cover every gap, address every edge case.

**Damage if unaddressed**: The operator may not see an intermediate deliverable for weeks. Stakeholder feedback arrives late. Corrections are more expensive because they cut across completed phases.

### Blind Spot 3: Data Freshness Assumption

**What is not being seen**: The CSV data was enriched in a prior session by scraping BigCommerce. Product dimensions, image URLs, prices, and inventory counts are a snapshot from that scrape date. The plan treats these as ground truth. In reality: prices change, products go out of stock, new products are added, images are updated, dimensions may be wrong.

**Why invisible**: The CSVs were "just created" from the author's perspective — they feel like current data. But data staleness begins the moment the scrape completes.

**Damage if unaddressed**: A planogram built from stale data ships with wrong prices, broken image links, and products that no longer exist. The store operator generates an order for a discontinued SKU or prices a Puffco at last month's cost.

### Blind Spot 4: Single-File as Virtue vs Constraint

**What is not being seen**: The plan frames single-file HTML as a constraint to tolerate ("if it crosses 3K lines, split JS") rather than examining whether the single-file pattern is appropriate at 155-SKU scale.

**Why invisible**: The existing tool's single-file simplicity is genuinely elegant. It's easy to deploy — one file, no build step. The author sees this as a property to preserve. But at 155 SKUs, a single file with inline catalog data is a maintenance liability — every catalog change is a code change.

**Damage if unaddressed**: The tool hits the 3K-line threshold quickly (the plan alone is 370 lines of markdown — the existing tool is 1,064 lines of JS). A reluctant split done under duress produces worse architecture than a split designed intentionally from the start.

### Blind Spot 5: The "Green/Yellow" Distinction

**What is not being seen**: The plan organizes products into 6 lines based on CSV filenames (Vape green, Vape yellow, Herb green, etc.). But "green" and "yellow" refer to a Fine Fettle-specific inventory classification — green = core/in-stock items, yellow = optional/slower-moving items. The plan doesn't explain this, and a reader unfamiliar with Fine Fettle's system would not understand the distinction.

**Why invisible**: The author worked with these files, read the CSVs, and internalized the green/yellow distinction without noticing it's domain-specific knowledge not present in the artifact.

**Damage if unaddressed**: A new implementer organizes the planogram around an unexplained taxonomy. If the tool is shown to a different store (not Fine Fettle), the green/yellow split is meaningless to them.

### Blind Spot 6: Optimizing for the Builder, Not the Buyer

**What is not being seen**: The planogram is a sales tool. Its purpose is to convince a store operator to buy the smoke-shop-in-a-box package. The plan optimizes for technical implementation (parse CSVs, render shapes, export JSON) but doesn't mention: visual polish, brand presentation, "wow factor," or how the tool sells the concept.

**Why invisible**: The author is an infrastructure architect. The "sales tool" function is outside the author's typical domain. The plan focuses on what the author knows how to build, not what the tool needs to accomplish in a sales conversation.

**Damage if unaddressed**: A technically correct but visually unpolished planogram fails its primary function — it doesn't sell. The Fine Fettle stakeholder said "I f****** love it" — that reaction came from visual impact and clarity, not from CSV parsing correctness.

---

## PHASE 5: COHERENCE SCORING

### Internal Consistency (weight: 0.15)
**Score: 0.72**

Phases reference each other consistently. The data pipeline feeds the renderer feeds the UI. One contradiction noted: Phase 3 (Data-Driven Architecture) removes hardcoded catalog objects and Phase 2 (Shape Renderer) needs the catalog data structure — they're presented as sequential but have circular dependency (Phase 2 needs the data schema from Phase 3 to know what a "product" looks like in the new system).

### Evidence Grounding (weight: 0.25)
**Score: 0.41**

Only 37% of claims are VERIFIED. 46% are UNVERIFIED — nearly half the plan's assertions have no supporting evidence. This is partly inherent in a forward-looking plan (many claims are about what should be built), but the plan presents many judgments as facts (e.g., "155 products need 4-6 displays," "category defaults can substitute for missing dimensions").

### Completeness (weight: 0.20)
**Score: 0.52**

4 CRITICAL gaps, 5 HIGH gaps, 6 MEDIUM gaps. The plan covers the major technical workstreams but omits testing, success criteria, rollback, stakeholder identification, and failure modes. These are not edge cases — they're fundamental to delivery.

### Sequencing (weight: 0.15)
**Score: 0.68**

The phase ordering is mostly sound: data before rendering, rendering before polish. Issues:
- Phase 8 (Security) is Priority 1 but listed last — the numbering creates confusion with the priority table
- Phase 3 (Data-Driven Architecture) overlaps substantially with Phase 1 (Data Pipeline) — the JSON schema design is a shared dependency
- Phase 7 (Dimension Gap Resolution) listed as Priority 6, after Image Integration (Priority 5), but the shape renderer needs dimensions immediately — estimated dimensions should come before image work

### Audience Alignment (weight: 0.10)
**Score: 0.38**

The plan oscillates between three audiences without committing: (1) a technical implementer who understands JS/HTML/CSS and Python, (2) a business stakeholder who cares about shopper experience and product-line strategy, (3) a project manager who needs priority order and risk register. The result is that no single audience is well-served. The technical implementer gets JSON schemas but not API contracts. The stakeholder gets shopper perspectives but not the business case. The PM gets a priority table but not timelines.

### Reality Match (weight: 0.15)
**Score: 0.64**

The plan accurately describes the existing codebase and CSV data. The optimism bias shows in: assuming CDN URLs will work as image sources without CORS testing, assuming 25+ auto-generated colors will be visually distinguishable, assuming dimension parsing won't have edge cases, assuming catalog.json fetch won't fail, and assuming the existing drag-and-drop scales 5× without UX degradation.

### Overall Coherence

| Layer | Score | Weight | Weighted |
|-------|-------|--------|----------|
| Internal consistency | 0.72 | 0.15 | 0.108 |
| Evidence grounding | 0.41 | 0.25 | 0.103 |
| Completeness | 0.52 | 0.20 | 0.104 |
| Sequencing | 0.68 | 0.15 | 0.102 |
| Audience alignment | 0.38 | 0.10 | 0.038 |
| Reality match | 0.64 | 0.15 | 0.096 |
| **OVERALL** | | | **0.551** |

The plan is **below the coherence threshold** (0.65 is the minimum for a plan that should proceed to execution without revision). The primary drag is evidence grounding (0.41) and audience alignment (0.38). The plan knows what to build but hasn't grounded its key architectural judgments in evidence and hasn't decided who it's written for.

---

## PHASE 6: DISSONANCE MAP

### Dissonance 1: Phase Numbering vs Priority Order
**What vs What**: Phases are numbered 1-8 in implementation-plan order, but the Priority Order table (L349-358) reorders them: 8, 1, 2, 3, 4, 7, 5, 6. Phase 8 (Security) is "Priority 1" but numbered last.
**Severity**: MEDIUM
**Type**: Structural
**Resolution**: Either renumber phases to match priority (Security becomes Phase 1, Data Pipeline becomes Phase 2, etc.) OR remove the numbered phase convention and use only priority ordering. The numbering should yield — it's cosmetic and the priority table is the operational sequence.

### Dissonance 2: "Shape is primary" vs "Image overlay is the intended experience"
**What vs What**: The user said "we have to use shapes for now" (temporary constraint). The plan declares shapes the permanent "primary rendering mode" with images as "secondary enhancement" (L105). But Phase 4 is entirely dedicated to image integration — loading, lazy-loading, toggling, thumbnails, previews. If shapes are truly primary and permanent, Phase 4 is a disproportionate investment.
**Severity**: HIGH
**Type**: Tonal / Evidential
**Resolution**: The plan should clearly distinguish: (a) what ships first (shape-only, because it's the only mode that works for all 155 SKUs given 59+ missing images), (b) what's the intended long-term experience (images where available, shapes where not, mixed mode as default). "Primary mode" should be reframed as "baseline mode — guaranteed to render for every SKU."

### Dissonance 3: "Functional existing tool" vs "Replace every data layer"
**What vs What**: The Witness section describes the existing tool in positive terms — "functional drag-and-drop planogram tool," validated by a customer who "f****** love[s] it." The Implementation Plan then replaces every data layer (catalog P, BC mapping, image paths, categories). The rendering engine is preserved, but all its inputs change.
**Severity**: MEDIUM
**Type**: Logical
**Resolution**: Acknowledge explicitly: the rendering engine and interaction model are the preserved core. The data layers are being externalized, not replaced — the same information flows through the same rendering path, just from a different source. Frame as "externalization" not "replacement."

### Dissonance 4: 6-product-line organization vs unexplained green/yellow taxonomy
**What vs What**: The entire display strategy rests on a 6-way split by product line (Glass green/yellow, Herb green/yellow, Vape green/yellow). The green/yellow distinction comes from Fine Fettle's inventory classification system — which is never explained in the document. A reader sees color labels without understanding what they signify.
**Severity**: HIGH
**Type**: Evidential
**Resolution**: Add a section explaining: green = core inventory (always in stock, high-turnover), yellow = extended inventory (available but lower volume). If the tool will be used by stores other than Fine Fettle, consider whether the green/yellow split is the right organizing principle or if it should be configurable.

### Dissonance 5: Explicit risk register vs implicit unstated risks
**What vs What**: The Risk Register (L364-370) lists 5 risks. But the plan body implies many more that don't appear in the register: CORS issues with CDN images, dimension parsing failures, CSV schema mismatch, catalog.json fetch failure, 25-color visual distinguishability, and shelf clearance conflicts for tall glass items. The register is partial relative to the plan's own analysis.
**Severity**: MEDIUM
**Type**: Structural
**Resolution**: The risk register should be derived systematically from the LENS gaps — each gap with uncertain resolution is a risk. Currently the register appears to be a manually selected subset.

---

## PHASE 7: CONFIDENCE ASSESSMENT

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | 0.75 | The audit covered all 370 lines, all 78 claims, and all major sections. Medium-confidence: the artifact is dense and some implicit claims may have been missed in a single reading pass. Would increase with: a second reader's independent claim extraction for comparison. |
| Accuracy | 0.70 | Claims about the existing codebase and CSV data are high-confidence (directly observed). Claims about future states are inherently lower-confidence. The classification of claims as VERIFIED/UNVERIFIED depends on my judgment of what constitutes sufficient evidence. Would increase with: independent verification of CSV row counts, a test parse of a sample dimension string, and confirmation that local images/ directory files exist as the plan implies. |
| Blind spot coverage | 0.55 | I identified 6 blind spots. But I am the same daemon that wrote the artifact — detecting my own blind spots is structurally limited. The Infrastructure Architect framing means I am likely blind to: (a) UX/interaction design issues I didn't see, (b) business model assumptions I share with the plan, (c) LuvBuds-specific operational constraints I don't know about. Would increase with: review by a UX designer (for interaction blind spots), by someone familiar with LuvBuds store operations (for domain blind spots), and by a second daemon with a different persona (for cognitive blind spots). |

**Overall audit confidence: 0.67** — actionable but not definitive. The highest-value improvement would be an independent review for blind spots.

---

## PHASE 8: ONE-SENTENCE VERDICT

**The plan knows what to build but not how to prove it works, who it's for, or when it's done — it's a technically competent architecture document that hasn't yet become an executable plan.**

---

## PHASE 9: RECOMMENDED ACTIONS

### Action 1: Add success criteria to every phase
**What**: For each of the 8 phases, add a "Done means:" section with at least one measurable, falsifiable criterion. Example for Phase 1: "Done means: build_catalog.py runs without error, catalog.json is valid JSON, every SKU in catalog.json has a non-null `line` field, and `python -m json.tool catalog.json > /dev/null` exits 0."
**Why first**: Without success criteria, no other action can be verified. This is the keystone — every other gap (testing, rollback, stakeholder sign-off) depends on knowing what "done" looks like.
**Sequencing**: Must be done before any implementation begins. Affects how all other phases are defined.

### Action 2: Resolve the green/yellow taxonomy
**What**: Add a section explaining what "green" and "yellow" mean (core vs extended inventory per Fine Fettle's classification). Then decide: is this taxonomy baked into the planogram, or is it configurable per store? If the tool serves multiple stores, the color labels become store-specific and should be data-driven. If Fine Fettle is the only customer, state that explicitly.
**Why second**: The entire display organization strategy rests on this distinction. If it's wrong or unexplained, the plan is building the wrong layout. Also addresses Blind Spot 5 and Dissonance 4.
**Sequencing**: Must be resolved before Phase 1 (Data Pipeline) since the `line` field assignment depends on it.

### Action 3: Add a failure-mode section for catalog.json loading
**What**: Define what happens when catalog.json fails to load (404, CORS error, network down, parse error). Specify at minimum: (a) a user-visible error message, (b) a retry button, (c) a fallback to an embedded minimal catalog for demo purposes. Consider whether catalog.json should be embedded at build time rather than fetched at runtime (eliminates the failure mode entirely).
**Why third**: Addresses Critical Gap G-C5. The current architecture degrades reliability (inline data → fetch dependency) without acknowledging the tradeoff.
**Sequencing**: Must be designed before Phase 3 (Data-Driven Architecture) since the fetch/embed decision affects the entire data-loading path.

### Action 4: Add a minimum-viable-deliverable slice
**What**: Insert a new section before the Implementation Plan: "Iteration 0 — 2-Display Demo." Ship Phase 1 (build_catalog.py) + a stripped Phase 2 (shape renderer for 2 displays only, 2 product lines, ~50 SKUs) as a single deliverable. Use this to: validate the dimension parsing, test the CDN image URLs, get stakeholder feedback on the shape rendering, and confirm the shelf math.
**Why fourth**: Addresses Blind Spot 2 (missing iteration model) and Blind Spot 6 (optimizing for builder not buyer). A 2-display demo delivered next week is more valuable than a 6-display system delivered in 6 weeks. The feedback from this demo will correct the remaining phases before significant investment.
**Sequencing**: Should be the first thing built — it's a subset of Phases 1+2, not an additional phase.

### Action 5: Add a test strategy section
**What**: For each phase, specify at minimum one test: (a) Phase 1 — parse all 6 CSVs, verify catalog.json has exactly 155 entries, (b) Phase 2 — render a known-dimension product (e.g., RAW cones at 5.25"×10.25"), measure the rendered rectangle in pixels, verify it matches PX=16 scaling, (c) Phase 5 — validate generated order JSON against the BigCommerce API schema, (d) Phase 6 — test print with 2 displays, verify output is readable on letter-size paper.
**Why fifth**: Addresses Critical Gap G-C2. Without tests, correctness is assumed rather than demonstrated. A planogram is a precision tool — 1" error at PX=16 is 16 pixels, which on a shelf with 12 columns is the difference between fitting and overflowing.
**Sequencing**: Test definitions can be written after success criteria (Action 1) but the test infrastructure should be built alongside each phase, not after.
