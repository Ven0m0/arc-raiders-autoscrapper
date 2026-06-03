# Cross-Reference: Commands, Skills, and Agents

This file maps related commands, skills, and agents so you can find the right tool for each task.

## OCR & Vision Pipeline

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/ocr-corpus-replay` | Validate OCR changes against failure corpus |
| Command | `/calibrate-vision` | Recalibrate context-menu crop constants |
| Command | `/add-fixture` | Lock OCR misread as regression test |
| Command | `/clean-debug` | Prune stale debug images |
| Command | `/benchmark` | Compare tessdata model variants |
| Command | `/threshold-change` | Safe fuzzy-match threshold adjustment |
| Skill | `ocr-corpus-replay` | Detailed corpus replay procedure |
| Skill | `calibrate-vision` | Vision constant recalibration workflow |
| Skill | `add-fixture` | Fixture capture workflow |
| Skill | `clean-debug` | Debug image cleanup |
| Skill | `benchmark` | Tesseract model benchmark |
| Skill | `threshold-change` | Threshold change safety protocol |
| Skill | `threshold-corpus-replay` | Replay corpus against candidate threshold value |
| Skill | `ocr-debug` | Internal: coordinate spaces, preprocessing, caches |
| Skill | `ocr-unavailable` | Internal: "UNAVAILABLE" misread triage |
| Agent | `ocr-reviewer` | Review OCR/scanner changes for bugs |
| Agent | `visual-analysis-ocr` | Image text extraction specialist |

## Scan & Detection

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/diagnose-scan` | Dry-run scan with failure routing |
| Command | `/scan-report` | Summarize scan output by failure type |
| Command | `/scan-dryrun` | Run a safe dry-run scan |
| Skill | `diagnose-scan` | Full scan diagnosis workflow |
| Skill | `scan-report` | Scan output classification |
| Skill | `scan-failed` | Internal: wrong action diagnosis |
| Skill | `failure-to-fix` | End-to-end scan failure pipeline |
| Skill | `triage-failures` | Analyze failure corpus patterns |
| Agent | `scan-validator` | Review scanner/interaction changes |
| Agent | `interaction-reviewer` | Review screen capture and input code |

## Rules & Item Actions

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/add-rule` | Add/edit custom item rules |
| Skill | `add-rule` | Rule addition workflow |
| Skill | `scan-failed` | Internal: decision error diagnosis |
| Agent | `rules-reviewer` | Review rule logic and precedence |

## Data & MetaForge

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/patch-update` | Full pipeline after game patches |
| Command | `/update-generated` | Regenerate snapshot data and rules |
| Command | `/metaforge` | API lookup reference |
| Skill | `patch-update` | Game patch update pipeline |
| Skill | `data-snapshot-updater` | MetaForge data refresh |
| Skill | `metaforge-arc-raiders` | API endpoint reference |
| Agent | `data-pipeline-reviewer` | Review data pipeline changes |
| Agent | `progress-reviewer` | Review quest/progress data |

## Config & Persistence

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/config-bump` | Safely version-bump config fields |
| Skill | `config-bump` | Config migration workflow |
| Agent | `config-reviewer` | Review config schema changes |

## Code Quality & CI

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/verify` | Full validation (lint + types + tests) |
| Command | `/lint` | Run Ruff linter |
| Command | `/dead-code-sweep` | Find and remove dead code |
| Command | `/precommit-fix` | Fix pre-commit hook failures |
| Command | `/ci-promote` | Validate, push, open PR |
| Command | `/todo-scan` | Scan TODOs and predict next step |
| Skill | `verify` | Validation suite workflow |
| Skill | `dead-code-sweep` | Dead code removal workflow |
| Skill | `precommit-fix` | Pre-commit fix guide |
| Skill | `ci-promote` | PR creation checklist |
| Skill | `todo-scan` | TODO triage workflow |
| Skill | `upstream-sync` | Sync fork from upstream |
| Skill | `merge-to-main` | Commit, sync upstream, merge, push to fork |
| Agent | `security-reviewer` | Security review |
| Agent | `performance-reviewer` | Performance review |
| Agent | `api-reviewer` | API change review |
| Agent | `test-generator` | Generate pytest test cases for new/modified code |

## TUI

| Resource | Name | Purpose |
|----------|------|---------|
| Command | `/run-app` | Launch the TUI |
| Agent | `tui-reviewer` | Review Textual UI changes |

## Workflow Chains

### Diagnose and Fix a Scan Issue
```
/diagnose-scan → /scan-report → classify failure → dispatch agent → /verify → /ci-promote
```

### After a Game Patch
```
/patch-update → /add-rule (for gaps) → /verify → /ci-promote
```

### OCR Accuracy Improvement
```
/benchmark → /threshold-change → /ocr-corpus-replay → /add-fixture → /verify
```

### Before Committing Any Change
```
/verify → /precommit-fix (if needed) → /upstream-sync → /ci-promote
```

### Cleanup Before Commit
```
/clean-debug → /dead-code-sweep → /verify
```

### Sync Fork with Upstream
```
/upstream-sync → /merge-to-main
```
