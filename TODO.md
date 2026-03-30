# OCR performance TODOs

TODO: crop infobox_bgr to title strip (top 22%) before preprocess_for_ocr in ocr_infobox()
TODO: pass top_fraction=1.0 to _extract_title_from_data after crop (strip is already the ROI)
TODO: remove sell_bbox/recycle_bbox extraction from ocr_infobox() — verify downstream never uses these fields, then drop both _extract_action_line_bbox calls
TODO: add _api_line (PSM.SINGLE_LINE) singleton alongside _api; use it in image_to_string and the stripped ocr_infobox
TODO: add rapidfuzz to pyproject.toml deps
TODO: populate _ITEM_NAMES at startup from rules_store (item names already in items_rules.default.json)
TODO: add match_item_name(raw, threshold=75) using rapidfuzz WRatio; call after clean_ocr_text in _extract_title_from_data
TODO: add module-level _last_roi_hash/_last_ocr_result cache in inventory_vision.py; skip OCR if title strip hash matches previous call
