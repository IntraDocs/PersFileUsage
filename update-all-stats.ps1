# update-all-stats.ps1
# Complete analysis pipeline for Personnel File Portal logs

Write-Host "Starting complete analysis pipeline..." -ForegroundColor Green

# Step 1: Split logs by user
Write-Host "`n=== Step 1: Splitting logs by user ===" -ForegroundColor Yellow
& .\.venv\Scripts\python.exe src/split_logs_by_user.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error in log splitting. Exiting." -ForegroundColor Red
    exit 1
}

# Step 2: Analyze user agents
Write-Host "`n=== Step 2: Analyzing user agents ===" -ForegroundColor Yellow
& .\.venv\Scripts\python.exe src/analyze_user_agents.py --input logs/splits --output out
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error in user agent analysis. Exiting." -ForegroundColor Red
    exit 1
}

# Step 3: Analyze active users
Write-Host "`n=== Step 3: Analyzing active users ===" -ForegroundColor Yellow
& .\.venv\Scripts\python.exe src/analyze_active_users.py --input logs/splits --output out
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error in active users analysis. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Analysis Complete! ===" -ForegroundColor Green
Write-Host "All statistics have been updated. You can now:" -ForegroundColor Cyan
Write-Host "  - Run the Streamlit dashboard: streamlit run app.py" -ForegroundColor White
Write-Host "  - Or use VS Code task: 'Run Streamlit dashboard'" -ForegroundColor White

# Optional: Show output files
Write-Host "`nGenerated files:" -ForegroundColor Cyan
if (Test-Path "out") {
    Get-ChildItem "out" -Filter "*.csv" | ForEach-Object {
        Write-Host "  - out/$($_.Name)" -ForegroundColor White
    }
}
else {
    Write-Host "  No output directory found" -ForegroundColor Red
}
