# Simple helper to expose your local Streamlit app as a temporary public link
# This lets others view it "live" without deploying anywhere.

Write-Host ""
Write-Host "=== Make Your Local App Temporarily Live ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Yellow
Write-Host "1. Make sure Streamlit is already running (streamlit run app.py)"
Write-Host "2. This script will give you a public URL you can share"
Write-Host "3. The link will stop working when you close this window or stop Streamlit"
Write-Host ""

$port = 8501

Write-Host "Starting localtunnel on port $port..." -ForegroundColor Green
Write-Host "A public URL will appear below (it starts with https://...loca.lt)" -ForegroundColor Green
Write-Host ""
Write-Host "Share that link with whoever you want to test with." -ForegroundColor Yellow
Write-Host "Press Ctrl + C in this window to stop sharing." -ForegroundColor Red
Write-Host ""

npx localtunnel --port $port