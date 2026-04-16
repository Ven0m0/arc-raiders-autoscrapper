# OCR Debug Vision Report
Date: 2026-04-16

## Summary

- Context menu raw captures are clean, color game screenshots; the processed (binarized/upscaled) versions produce high-contrast black-on-white text that is generally legible, but the background inventory icons bleed through as heavy black noise.
- The `lines_fail.json` files confirm that OCR is finding the correct menu option strings (e.g. "Move to Backpack", "Sell (+11,000)", "Recycle") but validation fails because the same SPARSE_TEXT pass also extracts large amounts of garbage tokens from the icon/background bleed region to the left of the menu.
- Infobox action sell crops are narrow strips tightly cropped to the sell button row. All 13 samples rendered legibly; the currency symbol (Phi glyph) occasionally clips or is absent from the leftmost edge but the `Sell (+N,NNN)` text is always intact and unambiguous.
- Inventory count raw and processed are both clear and numerically correct (`263/280  8`); the processed version uses larger, bolder glyphs with a grid icon and currency symbol — clean enough that no OCR errors are expected.
- The principal risk to pipeline accuracy is the background noise in processed context menu images, not the menu text itself; suppressing or masking the left-side icon bleed before OCR would likely eliminate most validation failures.

---

## Context Menu — Raw vs Processed

### Pair 1 — Early (06:03:47)

| Property | Raw | Processed |
|---|---|---|
| Filename | `20260416_060347_362678200_ctx_menu_raw.webp` | `20260416_060347_389481200_ctx_menu_processed.webp` |
| Item name visible | MATRIARCH REACTOR | MATRIARCH REACTOR |
| Menu options | Move to Backpack, Move to Safe Pocket, Inspect, Sell (+11,000), Recycle | Same — all present |
| Raw legibility | High. Color game screenshot; menu is a cream/off-white card with dark text. All five options clearly readable at native resolution. | — |
| Processed legibility | High for menu text. Binarization inverted colors to black-on-white; text glyphs are clean and sharp. |
| Rendering issues | Background inventory grid icons (left 30% of crop) are converted to heavy black blotches. The Phi currency glyph before "Sell" renders as a small blob but is recognizable. `×3` stack badges partially visible at right edge. |

**Lines-fail JSON (060347_659364500):** OCR extracted the correct menu strings but surrounded them with garbage tokens from the background: e.g. `"ON . MATRIARCH REACTOR"`, `"UV . Y Move to Backpack anny"`, `"x) n Sell (+11,000)"`. The target strings are present but mixed with noise characters — validation rejects the whole line rather than the clean substring.

---

### Pair 2 — Early+1 (same lines_fail batch: 060348)

**Lines-fail JSON (060348_010004300):** Very similar pattern to above. MATRIARCH REACTOR context still. Clean strings like `"Move to Backpack"`, `"Move to Safe Pocket"`, `"Inspect"`, `"Sell (+11,000)"`, `"Recycle"` all appear, each prefixed or suffixed with short noise tokens (`"&"`, `"Y"`, `"UY)"`, `"N"`, `"aj"`, `"mh Mm"`).

---

### Pair 3 — Early session, different item (060355)

**Lines-fail JSON (060355_097875700):** Item appears to be a weapon/gear slot item. Menu contains additional options: `"Swap with Primary Slot"`, `"Swap with Secondary Slot"`, `"Move to Backpack"`, `"Inspect"`, `"Repair"`, `"Upgrade"`, `"Sell(+10,540)"`, `"Recycle"`. All option strings appear in the JSON but again wrapped in noise (`"Im 7 EOECAT"`, `"il y Swap with Primary Slot"`, `"iy, Upgrade"`, `"ry val 'S Sell(+10,540)"`). The item name is garbled as `"EOECAT"` — likely OCR misread of a short item name from the title band.

---

### Pair 4 — Mid (06:05:26)

| Property | Raw | Processed |
|---|---|---|
| Filename | `20260416_060526_648963800_ctx_menu_raw.webp` | `20260416_060526_679869800_ctx_menu_processed.webp` |
| Item name visible | EXPIRED RESPIRATOR | EXPIRED RESPIRATOR (not in processed crop — title band absent) |
| Menu options | Split Stack, Move to Backpack, Move to Safe Pocket, Inspect, Sell (+1,280), Recycle | Same — all present and clean |
| Raw legibility | High. Different item class (consumable). "Split Stack" option visible — indicates stackable item. |
| Processed legibility | High. All menu option text is sharp white-on-black. Background icon noise is heavier in this crop; left side shows multiple binarized item thumbnails as blotches. |
| Rendering issues | Title band (item name) does not appear in processed crop — the `_ctx_menu_processed` crop starts below the header. This is consistent with `find_context_menu_crop` logic cropping to the action list only. The left-side blotch density is higher here than in Pair 1 due to more visible inventory cells in the frame. |

**Lines-fail JSON (060503_391087600):** From a nearby timestamp (different item — stackable). OCR found `"Split Stack"`, `"Move to Backpack"`, `"Move to Safe Pocket"`, `"Inspect"`, `"Sell(+2,000)"`. Garbage tokens around them: `"o () ) ( Split Stack"`, `"bh A ey x Move to Backpack"`, `"A a a Sag inspect"`, `"4 x2) (X 3X 2ilk sl"`. Last line is pure noise — binarized stack-count badges from inventory cells leaking into the right edge of the crop.

---

### Pair 5 — Late (06:08:38)

| Property | Raw | Processed |
|---|---|---|
| Filename | `20260416_060838_705499700_ctx_menu_raw.webp` | `20260416_060838_732438700_ctx_menu_processed.webp` |
| Item name visible | DEFLATED FOOTBALL | (title band absent from processed crop, consistent with mid-session behavior) |
| Menu options | Split Stack, Move to Backpack, Move to Safe Pocket, Inspect, Sell (+2,000), Recycle | Same — all present |
| Raw legibility | High. Late-session item; inventory shows rubber rings (duct tape?) and other misc items. ESC/TAB/CTRL footer visible — near inventory bottom. |
| Processed legibility | High for menu text. Upscaled crop is larger (~1270×900 px) than earlier pairs. Same background icon bleed pattern. |
| Rendering issues | The item thumbnail for "DEFLATED FOOTBALL" binarizes into a high-contrast blob (round shape, recognizable). The rounded inventory panel bottom-left corner creates a large curved black artifact. Footer buttons (ESC BACK, TAB CLOSE, CTRL) are binarized into filled rounded rectangles — these may generate spurious text tokens. |

**Lines-fail JSON (060838_645899200):** `"OO OO Split Stack"`, `"Move to Backpack"`, `"Move to Safe Pocket"` (clean), `"7 Inspect"`, `"Sell(+2,000)"`, `"BACK Recycle"`. Notably `"BACK"` from the footer ESC/TAB/CTRL bar bleeds into the Recycle line. Inventory stack counts (`"x x15"`, `"W x7"`, `"SN x10"`) appear as standalone garbage lines.

---

## Infobox Action Sell

All crops are narrow horizontal strips showing only the sell button region of the infobox. The Phi (currency) glyph and "Sell (+N,NNN)" text are the primary OCR targets.

| Timestamp | Text Visible | Phi Glyph Present | Legibility | Notes |
|---|---|---|---|---|
| 060458_327991200 | `Sell (+3,000)` | Yes (left edge, partial clip) | High | Two item thumbnails visible at far left — left edge of strip includes prior infobox panel |
| 060518_974972800 | `Sell (+3,000)` | Yes | High | Black left-side wedge artifact (infobox border); otherwise clean |
| 060526 (mid) | — | — | — | No dedicated sell strip for this timestamp (paired with ctx_menu) |
| 060549_799452000 | `Sell (+3,000)` | Yes (partial) | High | Two more item thumbnails at left; sell text clean and fully rendered |
| 060611_441375000 | `Sell (+2,000)` | Yes | High | Extra context: cube icon (backpack slot indicator?) and stacked item card with wrench/x5 badge visible at left |
| 060624_296766400 | `Sell (+2,500)` | No (clipped off-left) | High | Extremely tight crop — only the text, no glyph. Text itself sharp and unambiguous |
| 060625_715204200 | `Sell (+2,500)` | Yes | High | Clean minimal crop |
| 060650_627735600 | `Sell (+4,000)` | No (clipped off-left) | High | Same tight-crop pattern as 060624 |
| 060717_001605600 | `Sell (+2,000)` | Yes | High | Wide crop; includes wrench icon, cube icon, two item thumbnails with stack badges, and "Inspect" text above the sell row |
| 060734_949682500 | `Sell (+1,920)` | Yes | High | Narrow strip; item icons at left partially visible |
| 060741_362479800 | `Sell (+7,000)` | Yes | High | Wide strip showing inventory row (wrench ×3, checkmark ×3, ×1, ×3) and sell text at right |
| 060742_970778700 | `Sell (+7,000)` | Yes | High | Nearly identical to 060741 — likely same item, consecutive scan tick |
| 060753_998806300 | `Sell (+1,920)` | Yes | High | Clean minimal strip |
| 060839_221156300 | `Sell (+2,000)` | Yes | High | Clean minimal strip |
| 060849_010312500 | `Sell (+1,920)` | No (clipped off-left) | High | Tight crop; text clear |
| 060855_174493100 | `Sell (+4,500)` | Yes | High | Clean minimal strip |
| 060906_157102400 | `Sell (+1,200)` | No (clipped off-left) | High | Tight crop; text clear |

**Summary:** All 13 (15 total with duplicates) infobox sell strips contain legible, unambiguous sell values. The Phi glyph clips on approximately 4 of 13 unique strips depending on crop alignment, but is never needed for parsing — the text pattern `Sell (+N,NNN)` is always intact. No binarization artifacts affect the sell text itself. The variable width of crops (some include surrounding inventory context, some are text-only strips) suggests inconsistent crop anchoring, but this does not impact OCR of the sell value.

---

## Inventory Count

| Image | Text Visible | Legibility | Notes |
|---|---|---|---|
| `20260416_060345_773908900_inventory_count_raw.webp` | `263/280  8` (with grid icon and Phi/currency icon) | Very High | Compact dark strip on game HUD. Grid icon at left (3×3 dots), then `263/280`, then a circular currency icon, then `8`. Font is clean UI sans-serif. No artifacts. |
| `20260416_060345_802310600_inventory_count_processed.webp` | `263/280  8` (same content, binarized) | Very High | Processed version is binarized to black-on-white. Glyphs are thicker/bolder due to upscaling. Grid icon and currency icon both clearly visible as clean black shapes. Text spacing preserved accurately. Zero noise artifacts — this is a simple strip with no background content to bleed through. |

Inventory count OCR is the most reliable target in the pipeline. The strip has no background imagery and produces a clean binarized output with zero noise risk.

---

## Failure JSON Samples

Four `ctx_menu_lines_fail.json` files were analyzed. All share the same failure pattern.

### Common Structure
Each JSON is an array of `{"text": "...", "top": N}` objects where `top` is the pixel y-offset of that OCR line within the processed crop.

### Text Patterns Found

**Valid menu option strings (always present, but wrapped in noise):**
- `"MATRIARCH REACTOR"` — item name (title band, top of crop)
- `"Move to Backpack"` — clean in 3/4 JSONs; noisy in 1/4
- `"Move to Safe Pocket"` — clean in 3/4 JSONs
- `"Inspect"` — usually clean, occasionally prefixed with `"i :"` or `"7"`
- `"Sell (+11,000)"`, `"Sell(+10,540)"`, `"Sell(+2,000)"` — sell values always extractable; parenthesis style varies (space vs no-space after `+`)
- `"Recycle"` — usually clean; once appears as `"BACK Recycle"` due to footer bleed
- `"Split Stack"` — present for stackable items; occasionally prefixed with `"o () ) ("`
- `"Repair"`, `"Upgrade"`, `"Swap with Primary Slot"`, `"Swap with Secondary Slot"` — present for weapon-class items

**Noise token patterns (garbage from background):**
- Short symbol clusters: `"&"`, `"S"`, `"N"`, `"Y"`, `"UY)"`, `"x"`, `"aj"`, `"mh Mm"`, `"a I"`
- Stack badge fragments: `"x3"`, `"x) n"`, `"fs) 4 x3"`, `"4 x2) (X 3X 2ilk sl"`, `"x x15) (W x7) (SN x10"`
- Mixed lines: `"ON . MATRIARCH REACTOR"`, `"UV . Y Move to Backpack anny"`, `"bh A ey x Move to Backpack"`
- Footer bar bleed: `"BACK Recycle"` (ESC BACK / TAB CLOSE footer merges with last menu line)
- Garbled item name: `"Im 7 EOECAT"` (likely misread of a short item name from the title strip)

### Why Validation Fails
The validator appears to check that extracted lines match known menu option strings with high fidelity. Lines that contain a valid option string but are prefixed/suffixed with garbage tokens fail the match. Lines that are pure noise (stack badge fragments, symbol clusters) also fail and inflate the noise count per scan.

---

## Patterns & Recommendations

1. **Left-side icon bleed is the root cause of nearly all validation failures.** The processed context menu crop includes 30–50% of its width as binarized inventory background. A pre-OCR mask that whites-out everything left of the menu panel's left edge would eliminate the majority of garbage tokens. The menu panel left edge is consistently around x=480–500 in the raw 635px-wide crop (approximately 75% from left in the full-width processed image). A static left-margin crop or a dark-region detector on the processed image could identify this boundary.

2. **The footer bar (ESC BACK / TAB CLOSE / CTRL) bleeds into late-session crops.** When the inventory panel is scrolled near the bottom, the footer row appears in the capture. The binarized footer produces filled rounded-rectangle tokens and text like "BACK" that merges with valid menu lines. A crop height limit or bottom-margin exclusion would suppress this.

3. **Sell value extraction is fully reliable.** The `Sell (+N,NNN)` pattern is intact across all 13+ infobox strips tested. Phi glyph clipping is irrelevant since the sell text is parseable without it. The crop width variability (some strips include surrounding inventory context) is benign.

4. **Item name extraction from context menu title band is unreliable.** The title band is either absent from the processed crop (it is cropped out before the action list) or garbled when present (`"EOECAT"` vs actual name). Item name should not be sourced from context menu OCR; use the infobox title band path (`ocr_infobox_with_context`) instead.

5. **The `dark_fraction < 0.20` rejection threshold in `find_context_menu_crop` appears to be working.** All three raw crops analyzed show a clear dark menu panel occupying the right 40–50% of the crop, well above threshold. The rejection guard is not triggering on valid captures.

6. **Stack count badge text (`×2`, `×3`, `×5`, etc.) consistently appears in fail lines.** These originate from the inventory cell badges visible in the background. If a line consists entirely of `×N` tokens it should be discardable; adding a filter for lines matching `^[×xX\d\s\(\)]+$` would silently drop these without affecting valid option detection.

7. **Binarization quality is good for the target text.** Menu option characters are sharp with no broken strokes or merged glyphs. The upscaling factor applied to the processed crops (roughly 2× based on pixel dimensions) is appropriate. No recommendation to change binarization parameters — the issue is crop region selection, not threshold values.
