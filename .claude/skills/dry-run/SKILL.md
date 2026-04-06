---
name: dry-run
description: Run a dry-run scan and interpret the debug output images in ocr_debug/
disable-model-invocation: true
---

Run a dry-run scan to validate OCR and decision pipeline without clicking:

```bash
uv run autoscrapper scan --dry-run
```

After the scan completes, debug images land in `ocr_debug/` with timestamps. Inspect:

| File pattern | What it shows |
|---|---|
| `*_infobox_detect_overlay.png` | Infobox detection — green box = detected, red = missed |
| `*_ctx_menu_processed.png` | Context menu crop after binarization — should show clear text |
| `*_infobox_action_sell_processed.png` | Sell/recycle button OCR region — check text is legible |

**Common failures to look for:**
- Infobox not detected → wrong crop region or window resize
- OCR reads garbled text → binarization threshold too aggressive or image too dark
- Item name reads as "unreadable" → upscale or contrast issue
- Action button OCR returns wrong text → binarization inverted (black-on-white vs white-on-black)

**If items are misidentified:** Check the fuzzy match score in logs. Low scores mean the OCR string diverged from the known item name — usually a preprocessing issue, not a rules issue.
