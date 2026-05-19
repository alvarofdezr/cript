# Quick Start with UV

For the fastest setup, use UV:

## Linux / macOS
```bash
bash setup.sh
```

## Windows
```bash
setup.bat
```

## Manual Setup

### 1. Install UV
```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Sync Dependencies
```bash
uv sync --group dev
```

### 3. Run Tests
```bash
uv run pytest tests/ -v
```

### 4. Run Examples
```bash
uv run python examples/01_basic.py
```

---

**See UV_GUIDE.md for complete documentation**
