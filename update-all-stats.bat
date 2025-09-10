@echo off
REM update-all-stats.bat
REM Complete analysis pipeline for Personnel File Portal logs

echo Starting complete analysis pipeline...

echo.
echo === Step 1: Splitting logs by user ===
.\.venv\Scripts\python.exe src/split_logs_by_user.py
if %errorlevel% neq 0 (
    echo Error in log splitting. Exiting.
    pause
    exit /b 1
)

echo.
echo === Step 2: Analyzing user agents ===
.\.venv\Scripts\python.exe src/analyze_user_agents.py --input logs/splits --output out
if %errorlevel% neq 0 (
    echo Error in user agent analysis. Exiting.
    pause
    exit /b 1
)

echo.
echo === Step 3: Analyzing active users ===
.\.venv\Scripts\python.exe src/analyze_active_users.py --input logs/splits --output out
if %errorlevel% neq 0 (
    echo Error in active users analysis. Exiting.
    pause
    exit /b 1
)

echo.
echo === Analysis Complete! ===
echo All statistics have been updated. You can now:
echo   - Run the Streamlit dashboard: streamlit run app.py
echo   - Or use VS Code task: 'Run Streamlit dashboard'

echo.
echo Generated files:
if exist "out" (
    dir /b out\*.csv
) else (
    echo   No output directory found
)

pause
