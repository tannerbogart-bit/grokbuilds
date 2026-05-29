@echo off
echo ============================================
echo   GC AI Dashboard - Diagnostics
echo ============================================
echo.

cd /d "%~dp0"

echo 1. Checking Python...
python --version
echo.

echo 2. Checking if virtual environment exists...
if exist ".venv\Scripts\python.exe" (
    echo Virtual environment found.
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b
)
echo.

echo 3. Checking key packages...
.venv\Scripts\python.exe -c "import streamlit; print('streamlit:', streamlit.__version__)" 2>nul || echo streamlit: NOT INSTALLED
.venv\Scripts\python.exe -c "import pandas; print('pandas:', pandas.__version__)" 2>nul || echo pandas: NOT INSTALLED
echo.

echo 4. Checking if app.py has syntax errors...
.venv\Scripts\python.exe -m py_compile app.py
if %errorlevel% neq 0 (
    echo ERROR: There is a problem with app.py
) else (
    echo app.py looks syntactically correct.
)
echo.

echo 5. Checking port 8501...
netstat -ano | findstr :8501 >nul
if %errorlevel% == 0 (
    echo Port 8501 appears to be in use.
) else (
    echo Port 8501 is free.
)
echo.

echo ============================================
echo Diagnostics complete.
echo ============================================
pause