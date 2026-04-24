---
title: Implementation Plan
status: active
updated: 2026-04-24
---

## Workflow

1. Read AGENTS.md and .github/instructions/python.instructions.md first
2. Make minimal, targeted changes
3. Never hand-edit src/autoscrapper/progress/data/ or items_rules.default.json
4. Regenerate data with scripts/update_snapshot_and_defaults.py when needed
5. Run validation before marking done:
   - uv run ruff check src/ tests/ scripts/
   - uv run basedpyright src/
   - uv run pytest

## Delivery Waves

<waves>
  <wave id="1" goal="OCR accuracy improvements">
    <task-ref id="T012"/>
    <task-ref id="T013"/>
    <task-ref id="T027"/>
    <task-ref id="T028"/>
    <task-ref id="T029"/>
    <task-ref id="T030"/>
    <task-ref id="T031"/>
    <task-ref id="T032"/>
  </wave>
  <wave id="2" goal="Data pipeline hardening">
    <task-ref id="T014"/>
    <task-ref id="T003"/>
    <task-ref id="T001"/>
    <task-ref id="T002"/>
  </wave>
  <wave id="3" goal="Feature completion">
    <task-ref id="T017"/>
    <task-ref id="T019"/>
    <task-ref id="T020"/>
    <task-ref id="T022"/>
  </wave>
  <wave id="4" goal="Research">
    <task-ref id="T021"/>
  </wave>
</waves>

## Active Tasks

<task id="T001" priority="medium" size="M" status="ready">
  <title>Calibrate OCR item-name threshold from failure corpus</title>
  <file>src/autoscrapper/ocr/failure_corpus.py</file>
  <file>scripts/replay_ocr_failure_corpus.py</file>
  <why>Replace hand-picked threshold with corpus-backed evidence</why>
  <done>
    <item>Corpus samples capture fields needed for accuracy scoring</item>
    <item>Replay script compares thresholds and reports accuracy</item>
    <item>Default changes only when replay shows no regression</item>
  </done>
</task>

<task id="T002" priority="low" size="S" status="blocked" depends-on="T001">
  <title>Benchmark tessdata.best-eng vs tessdata.fast-eng</title>
  <file>src/autoscrapper/ocr/tesseract.py</file>
  <file>scripts/benchmark_tessdata_models.py</file>
  <why>Only worth doing after threshold corpus is stable</why>
  <done>
    <item>Benchmark uses same corpus from T001</item>
    <item>Compare accuracy and latency for both models</item>
    <item>Change models only if latency trade-off is acceptable</item>
  </done>
</task>

<task id="T003" priority="medium" size="M" status="blocked" depends-on="T014">
  <title>Enrich snapshot updates with hybrid MetaForge plus wiki pipeline</title>
  <why>Extend updater after unsupported Supabase dependency is removed</why>
  <done>
    <item>MetaForge primary and RaidTheory fallback remain intact</item>
    <item>Wiki enrichment fills gaps for workshop, expedition, project-use data</item>
    <item>Dry-run output reports coverage without writing tracked files</item>
    <item>Metadata records origin of enriched fields</item>
  </done>
</task>

<task id="T012" priority="medium" size="S" status="ready">
  <title>Add Roman numeral OCR alias correction to rule lookup</title>
  <file>src/autoscrapper/core/item_actions.py</file>
  <why>Close OCR-to-rule mismatch for tiered weapon names</why>
  <done>
    <item>Normalization corrects common OCR suffix errors (1V, 111)</item>
    <item>Canonical matching uses existing fuzzy threshold</item>
    <item>Tests cover corrected and unchanged names</item>
  </done>
</task>

<task id="T013" priority="medium" size="S" status="ready">
  <title>Filter weapon swap UI text from item-name detection</title>
  <file>src/autoscrapper/ocr/inventory_vision.py</file>
  <why>Prevent overlay text from being mistaken for item title</why>
  <done>
    <item>Known swap-related UI strings ignored on first title pass</item>
    <item>Retry path expands to reach real item name below UI line</item>
    <item>Change does not weaken unrelated title extraction</item>
  </done>
</task>

<task id="T014" priority="high" size="M" status="ready">
  <title>Remove Supabase dependency from data snapshot updates</title>
  <file>src/autoscrapper/progress/data_update.py</file>
  <file>scripts/update_snapshot_and_defaults.py</file>
  <why>Remove committed credential, keep updater on supported sources</why>
  <done>
    <item>MetaForge item fetching uses includeComponents instead of Supabase</item>
    <item>All Supabase constants and helpers deleted</item>
    <item>Snapshot updater runs without any Supabase call path</item>
  </done>
</task>

<task id="T017" priority="low" size="S" status="ready">
  <title>Make ScanSettingsScreen a real abstract base class</title>
  <file>src/autoscrapper/tui/settings.py</file>
  <why>Turn silent design bug into enforced contract</why>
  <done>
    <item>Class inherits from ABC</item>
    <item>Abstract methods enforced at instantiation</item>
    <item>No new type-checking regressions</item>
  </done>
</task>

<task id="T019" priority="medium" size="S" status="ready">
  <title>Write per-session decision log for rule review</title>
  <file>src/autoscrapper/scanner/</file>
  <why>Create durable record without replacing OCR failure corpus</why>
  <done>
    <item>Session appends JSONL decision records when logging enabled</item>
    <item>Log includes timestamp, raw text, decision, location, score, source</item>
    <item>Feature is opt-in, does not slow normal scans</item>
  </done>
</task>

<task id="T020" priority="medium" size="M" status="ready">
  <title>Add safe recycle protection against active quest requirements</title>
  <file>src/autoscrapper/progress/</file>
  <why>Prevent recycling items that active quests still need</why>
  <done>
    <item>Recycle decisions cross-checked against active quest requirements</item>
    <item>Conflicts override decision to KEEP and record quest reason</item>
    <item>Feature degrades gracefully when progress data absent</item>
  </done>
</task>

<task id="T021" priority="low" size="M" status="research">
  <title>Assess Raider Lens overlay ideas before integration</title>
  <file>src/autoscrapper/tui/</file>
  <why>Optional exploratory work, do not start until higher-value tasks land</why>
  <done>
    <item>Written assessment identifies what can be reused safely</item>
    <item>Prototype stays isolated from OCR and scan performance risk</item>
  </done>
</task>

<task id="T022" priority="low" size="S" status="ready">
  <title>Make pytest available in documented install paths</title>
  <file>pyproject.toml</file>
  <file>scripts/setup-linux.sh</file>
  <file>scripts/setup-windows.ps1</file>
  <why>Remove setup drift for contributors and CI environments</why>
  <done>
    <item>Docs point contributors to install path including pytest</item>
    <item>Fresh setup aligns with dependency groups in pyproject.toml</item>
  </done>
</task>

<task id="T027" priority="high" size="M" status="ready">
  <title>Feed rules_store.get_item_names() to Tesseract as user_words</title>
  <file>src/autoscrapper/ocr/tesseract.py</file>
  <file>src/autoscrapper/items/rules_store.py</file>
  <why>Tesseract LSTM has no domain prior; user_words recommended for non-prose vocabulary</why>
  <done>
    <item>initialize_ocr writes item-name tokens to temp file, loads via user_words_suffix</item>
    <item>load_system_dawg set to 0 to remove English-dictionary noise</item>
    <item>Re-init after rules_store custom-overrides change, with integration test</item>
    <item>Corpus replay shows no regressions</item>
  </done>
</task>

<task id="T028" priority="medium" size="S" status="ready">
  <title>Pad all four sides of OCR title-strip ROIs</title>
  <file>src/autoscrapper/ocr/inventory_vision.py</file>
  <why>Tightly-cropped text reduces accuracy per tessdoc</why>
  <done>
    <item>Top, bottom, right edges receive symmetric _TITLE_PAD pixels of median background</item>
    <item>Retry path keeps existing extra expansion behaviour</item>
    <item>Corpus replay shows no regressions</item>
  </done>
</task>

<task id="T029" priority="medium" size="M" status="ready">
  <title>Add Sauvola binarisation as parallel candidate for uneven illumination</title>
  <file>src/autoscrapper/ocr/inventory_vision.py</file>
  <why>Otsu fails on title-band glow and rarity gradients; Sauvola is locally adaptive</why>
  <done>
    <item>preprocess_for_ocr_sauvola implemented via numpy or Tesseract thresholding_method=2</item>
    <item>When Otsu yields no fuzzy match, Sauvola runs and higher-WRatio result wins</item>
    <item>No new mandatory dependency added</item>
  </done>
</task>

<task id="T030" priority="medium" size="S" status="ready">
  <title>Confidence-gated retry instead of match-only retry</title>
  <file>src/autoscrapper/ocr/inventory_vision.py</file>
  <why>Current retry misses high-fuzzy/low-confidence cases producing wrong item names</why>
  <done>
    <item>Primary read uses image_to_data, computes mean per-character confidence</item>
    <item>Retries fire when mean_conf below 60 even if fuzzy match exists</item>
    <item>Highest-confidence result wins</item>
  </done>
</task>

<task id="T031" priority="medium" size="S" status="ready" depends-on="T001">
  <title>Glyph-aware fuzzy distance for OCR-prone confusions</title>
  <file>src/autoscrapper/ocr/inventory_vision.py</file>
  <why>WRatio penalises O/0, I/1, 5/S equally, forcing loose threshold</why>
  <done>
    <item>match_item_name_result canonicalises 0-O, 1-I, 5-S, 8-B on query and choices</item>
    <item>Default threshold tightens ~5 points without losing recall</item>
    <item>OCR and rule-lookup thresholds remain shared</item>
  </done>
</task>

<task id="T032" priority="low" size="XS" status="ready">
  <title>Set user_defined_dpi=300 on Tesseract API</title>
  <file>src/autoscrapper/ocr/tesseract.py</file>
  <why>Numpy arrays carry no DPI header; explicit 300 DPI hint correct with 2x upscale</why>
  <done>
    <item>initialize_ocr sets user_defined_dpi to 300</item>
    <item>No corpus regression</item>
  </done>
</task>

## Next Picks

<next-picks>
  <pick rank="1" task="T014">Security fix removing committed credentials</pick>
  <pick rank="2" task="T027">High-impact OCR accuracy improvement</pick>
  <pick rank="3" task="T012">Small OCR normalization fix</pick>
  <pick rank="4" task="T013">UI text filtering</pick>
  <pick rank="5" task="T028">ROI padding improvement</pick>
</next-picks>
