# analyze-misc-functions.ps1
# Analyze logs for miscellaneous functions

Write-Host "Starting miscellaneous functions analysis..." -ForegroundColor Green

# Ensure the output directory exists
if (-not (Test-Path "out")) {
    New-Item -Path "out" -ItemType Directory
    Write-Host "Created output directory: out" -ForegroundColor Cyan
}

# Run the analyzer
Write-Host "Analyzing miscellaneous functions..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe src/analyze_misc_functions.py --logs-dir logs --output-dir out --verbose
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error in miscellaneous functions analysis. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Analysis Complete! ===" -ForegroundColor Green
Write-Host "Miscellaneous functions analysis has been completed." -ForegroundColor Cyan
Write-Host "You can now run the Streamlit dashboard to see the results: streamlit run app.py" -ForegroundColor White

# Show output file
if (Test-Path "out/misc_functions.csv") {
    Write-Host "`nGenerated file:" -ForegroundColor Cyan
    Write-Host "  - out/misc_functions.csv" -ForegroundColor White
}
else {
    Write-Host "`nOutput file was not created." -ForegroundColor Red
}