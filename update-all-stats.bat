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
echo === Step 4: Analyzing sort usage ===
.\.venv\Scripts\python.exe src/analyze_sort_usage.py --input logs/splits --output out
if %errorlevel% neq 0 (
    echo Error in sort usage analysis. Exiting.
    pause
    exit /b 1
)

echo.
echo === Step 5: Analyzing folder selection ===
.\.venv\Scripts\python.exe src/analyze_folder_selection.py --input logs/splits --output out
if %errorlevel% neq 0 (
    echo Error in folder selection analysis. Exiting.
    pause
    exit /b 1
)

echo.
echo === Step 6: Analyzing employee filter usage ===
.\.venv\Scripts\python.exe src/analyze_employee_filter.py --input logs/splits --output out
if %errorlevel% neq 0 (
    echo Error in employee filter analysis. Exiting.
    pause
    exit /b 1
)

echo.
echo === Step 7: Analyzing document filter usage ===
.\.venv\Scripts\python.exe src/analyze_document_filter.py --input logs/splits --output out
if %errorlevel% neq 0 (
    echo Error in document filter analysis. Exiting.
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
