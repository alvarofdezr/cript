@echo off
REM Quick setup script for CRIPT on Windows
REM
REM Usage:
REM   setup.bat
REM

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║            CRIPT Setup Script (Windows)                        ║
echo ║   Cryptographic Ratcheting Implementation Protocol              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Installing UV package manager...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo ✓ UV installed
    echo.
)

for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
echo ✓ UV is installed: %UV_VERSION%
echo.

echo 📦 Syncing CRIPT dependencies...
call uv sync --group dev

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   Setup Complete! ✓                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo.
echo 1. Activate virtual environment:
echo    .venv\Scripts\activate
echo.
echo 2. Run tests:
echo    uv run pytest tests/ -v
echo.
echo 3. Run examples:
echo    uv run python examples/01_basic.py
echo.
echo 4. Start server:
echo    uv run python -m cript.network.server
echo.
echo 5. View documentation:
echo    type UV_GUIDE.md
echo    type README.md
echo.
