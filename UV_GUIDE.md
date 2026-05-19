# UV - Package Manager Guide for CRIPT

[UV](https://docs.astral.sh/uv/) es el nuevo package manager ultra-rápido de Astral (creadores de Ruff).

## 🚀 Instalación

### Windows
```powershell
# Con scoop
scoop install uv

# O descargar desde: https://github.com/astral-sh/uv/releases
```

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verificar instalación
```bash
uv --version
# Output: uv 0.x.x
```

## 📦 Uso en CRIPT

### Estructura recomendada
```
cript/
├── pyproject.toml        # Source of truth (única declaración de deps)
├── uv.lock              # Generated automáticamente (reproducibilidad)
├── .gitignore           # Ignora venv/ local
└── ...
```

### ✅ Diferencia IMPORTANTE vs pip

**Con pip:**
```bash
pip install -e .               # Instala dependencias
pip install -e ".[dev]"        # Instala con dev deps
pip freeze > requirements.txt  # Crea lock file manualmente
```

**Con uv (MUCHO más rápido):**
```bash
uv sync                        # Instala + crea venv (automático!)
uv sync --group dev           # Con dev dependencies
# uv.lock se crea automáticamente
```

---

## 📋 Comandos Comunes

### Desarrollo

```bash
# Crear venv y instalar dependencias
uv sync

# Con dependencias de desarrollo
uv sync --group dev

# Ejecutar comando en venv
uv run python examples/01_basic.py

# Ejecutar tests
uv run pytest tests/ -v

# Ejecutar con coverage
uv run pytest tests/ --cov=src/cript
```

### Agregar dependencias

```bash
# Agregar runtime dependency
uv add cryptography

# Agregar dev dependency
uv add --dev pytest

# Agregar con versión específica
uv add "cryptography>=41.0.0,<42"
```

### Actualizar dependencias

```bash
# Actualizar todas
uv lock --upgrade

# Actualizar un paquete
uv lock --upgrade-package pytest

# Verificar qué se actualizaría
uv lock --dry-run
```

### Reproducibilidad

```bash
# En CI/CD, usar lock file:
uv sync --frozen  # Falla si lock no es compatible

# Después de cambiar pyproject.toml:
uv lock
git add uv.lock
```

---

## 🔄 Flujo de Trabajo Completo

### 1. Primer Setup (Local)
```bash
cd cript
uv sync --group dev
uv run pytest tests/ -v
```

### 2. Agregar nueva dependencia
```bash
uv add httpx        # Runtime
uv add --dev black  # Dev
uv lock             # Actualizar lock
git add pyproject.toml uv.lock
git commit -m "chore: add new dependencies"
```

### 3. CI/CD (GitHub Actions)
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v2
      - run: uv sync --frozen --group dev
      - run: uv run pytest tests/
      - run: uv run black --check src/ tests/
```

### 4. Production Deployment
```bash
# En servidor Ubuntu:
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone ...
cd cript
uv sync --frozen  # Usa lock file exacto
uv run python -m cript.network.server
```

---

## 📊 Comparación: pip vs uv

| Operación | pip | uv |
|-----------|-----|-----|
| Install deps | ~5-10s | ~200-500ms |
| Install large project | ~30s | ~1-2s |
| Lock generation | Manual | Automático |
| Reproducibility | ❌ Difícil | ✅ Fácil (uv.lock) |
| Python install | ❌ No | ✅ Sí (`uv python install`) |
| Compatibility | ✅ Universal | ✅ PEP 517/518 |
| Learning curve | ✅ Fácil | ✅ Muy fácil |

---

## 🎯 Ventajas de UV para CRIPT

### 1. **Super rápido**
   - Instalación ~100x más rápida que pip
   - Lock file en millisegundos

### 2. **Reproducible**
   - `uv.lock` garantiza reproducibilidad
   - Mismo lock = mismo entorno siempre

### 3. **Pythons management**
   ```bash
   uv python list              # Listar Pythons disponibles
   uv python install 3.12      # Instalar Python automáticamente
   uv run --python 3.11 pytest # Usar versión específica
   ```

### 4. **Simple**
   - Un comando: `uv sync`
   - No necesitas `pip install -e .` y `pip freeze`
   - Todo centralizado en `pyproject.toml`

### 5. **Moderno**
   - Escrito en Rust (ultra-optimizado)
   - Usado por Astral (creadores de Ruff)
   - Futuro del packaging Python

---

## 🔧 Configuración en pyproject.toml

```toml
[tool.uv]
# Instalar con venv automático
managed = true

# Grupos de dependencias
dev-dependencies = [
    "pytest>=7.0",
    "black>=23.0",
]

[tool.uv.sources]
# Crear fuentes custom si es necesario
# my-package = { path = "../my-package" }
```

---

## ⚠️ Notas Importantes

### NO uses `setup.py` con `uv`
```bash
# ❌ INCORRECTO
python setup.py install

# ✅ CORRECTO
uv sync
uv run python -m cript.network.server
```

### NO necesitas `requirements.txt`
```bash
# ❌ REDUNDANTE
pip install -r requirements.txt

# ✅ CORRECTO - uv lo genera automáticamente
uv sync
```

### Siempre commitea `uv.lock`
```bash
git add pyproject.toml uv.lock
git commit -m "deps: update dependencies"
```

### En `.gitignore` agrega:
```
.venv/           # venv local creado por uv
__pycache__/
*.pyc
.uv/             # Cache de uv
```

---

## 📚 Recursos

- **Documentación oficial**: https://docs.astral.sh/uv/
- **GitHub**: https://github.com/astral-sh/uv
- **Quickstart**: https://docs.astral.sh/uv/getting-started/

---

## 🎓 Ejemplo Completo para CRIPT

### Setup inicial
```bash
# Clone y setup
git clone https://github.com/alvarofdezr/cript.git
cd cript

# Instalar UV si no tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sincronizar dependencias (crea .venv automáticamente)
uv sync --group dev

# Activar venv
source .venv/bin/activate  # Linux/Mac
# o en Windows: .venv\Scripts\activate
```

### Desarrollo
```bash
# Correr ejemplos
uv run python examples/01_basic.py

# Tests
uv run pytest tests/ -v

# Linting
uv run black src/ tests/
uv run flake8 src/ tests/

# Server
uv run python -m cript.network.server
```

### Deployment (Ubuntu)
```bash
# En servidor remoto
sudo apt update && sudo apt install -y python3.10 build-essential
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/alvarofdezr/cript.git
cd cript
uv sync --frozen          # Usar lock file
uv run python -m cript.network.server
```

---

**¡UV es el futuro del packaging Python!** 🚀
