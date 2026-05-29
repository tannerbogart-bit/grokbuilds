@echo off
echo ============================================
echo   Starting GC AI Dashboard
echo ============================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking if port 8501 is already in use...
netstat -ano | findstr :8501 >nul
if %errorlevel% == 0 (
    echo WARNING: Something is already running on port 8501!
    echo You may need to close other Streamlit instances.
    echo.
    pause
)

echo.
echo Starting Streamlit...
echo Once it starts, open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C in this window to stop the app.
echo ============================================

streamlit run app.py --server.headless true

pause