# Setup

Setup development environment for Arc Raiders AutoScrapper.

## Windows
```bash
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

## Linux
```bash
bash scripts/setup-linux.sh
```

## Validation
```bash
uv run ruff check src/
```
