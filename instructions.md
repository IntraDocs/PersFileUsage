# Instructions for PF-Logs: Personnel File Portal Log Analysis

## Project Language Requirements
**All code, comments, documentation, and instructions in this project must be written in English.** This includes:
- Python code comments and docstrings
- Variable and function names
- Git commit messages
- Documentation files (including this instructions.md)
- Error messages and logging output
- VS Code task descriptions

This ensures consistency and maintainability for international development teams.

## Project Overview
This project analyzes log files from the Youforce Personnel File Portal. It consists of six main components:
1. **Log Splitter**: Splits daily log files by date and user
2. **User Agent Analyzer**: Analyzes browser and device usage by users
3. **Active Users Analyzer**: Analyzes user activity per hour and day
4. **Sort Usage Analyzer**: Analyzes usage patterns of sort functionality
5. **Panel Selection Analyzer**: Analyzes panel switching behavior and concurrent usage patterns
6. **Streamlit Dashboard**: Visualizes all analysis results in an interactive interface

## Complete Workflow

### Option A: Single Command (Recommended)
**VS Code Task (Easiest)**:
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → **"Run complete analysis pipeline"**

**PowerShell Command**:
```powershell
.\update-all-stats.ps1
```

**Batch Command**:
```cmd
update-all-stats.bat
```

### Option B: Manual Step-by-Step

### Step 1: Log Splitting
- Place raw log files in `logs/raw/` directory (e.g. `Youforce_Personnel_File_Portal_JWT_User_SD-P-DOIIS25.log`)
- **Supported formats**: Both `.log` and `.arc` files are processed automatically
- Run: `python src/split_logs_by_user.py` or VS Code task "Run splitter"
- Output: `logs/splits/YYYY-MM-DD/{USER}.log` files

### Step 2: User Agent Analysis
- Run: `python src/analyze_user_agents.py --input logs/splits --output out` or VS Code task "Run UA analysis"
- Output: CSV files in `out/` directory with browser/OS statistics

### Step 3: Active Users Analysis
- Run: `python src/analyze_active_users.py --input logs/splits --output out` or VS Code task "Run Active Users analysis"
- Output: Hourly and daily activity statistics in `out/` directory

### Step 4: Run Panel Selection Analysis
```powershell
python src/analyze_selected_panels.py logs/2024-08-25_split.log
```
This analyzes which panels users select and switch between, including base panels and employee panels. Results are saved to `data/panel_analysis_results.json`.

### Step 6: View Results in Dashboard
- Run: `python src/analyze_sort_usage.py --input logs/splits --output out` or VS Code task "Run Sort Usage analysis"
- Output: Sort functionality usage statistics in `out/` directory

### Step 5: Panel Selection Analysis
- Run: `python src/analyze_selected_panels.py logs/splits` or VS Code task "Run Panel Selection analysis"
- Output: Panel usage patterns and concurrent panel statistics in `data/` directory

### Step 6: Dashboard Viewing
- Run: `streamlit run app.py` or VS Code task "Run Streamlit dashboard"
- Open browser to the displayed URL for interactive dashboard with all analyses

## Log Format Details

### Input Log Format (Raw)
```
2025-09-10 09:39:02.1143 11.1.2.0 DEBUG 85 [User: IC118451] [UserAgent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...] Switch Panel Activated: employees
```

Components:
- **Timestamp**: `YYYY-MM-DD HH:MM:SS.mmm`
- **IP Address**: `11.1.2.0`
- **Log Level**: `DEBUG`
- **Thread ID**: `85`
- **User**: `[User: IC118451]` (alphanumeric ID)
- **User Agent**: `[UserAgent: browser string]` (complete browser identification)
- **Message**: Description of the action

### Output Format (Split)
- Directory structure: `logs/splits/YYYY-MM-DD/{USER}.log`
- Original log lines are preserved exactly
- Each user gets their own file per day

## Processing Logic

### Log Splitter (`split_logs_by_user.py`)
1. Scan each line for date pattern at the beginning
2. Extract user from `[User: USERNAME]` pattern
3. If both found: append line to appropriate output file
4. Create directories automatically
5. Skip lines without user or date
6. **Processes both `.log` and `.arc` files from raw directory**

### User Agent Analyzer (`analyze_user_agents.py`)
1. Scan all `.log` files in `logs/splits/`
2. Extract first line with UserAgent per user/day
3. Parse browser, OS, device information with `user-agents` library
4. Generate aggregated CSV reports
5. Automatically deduplicates within (date, user) combinations

### Dashboard (`app.py`)
- Streamlit web interface for data visualization
- Filters on date and browser
- KPIs: unique users, browsers, operating systems
- Interactive charts with Altair
- Overview table with all data

## Error Handling
- **Encoding**: UTF-8 with error='ignore' for invalid characters
- **Missing Files**: Log but don't stop when files are missing
- **Directory Creation**: Automatically create output directories
- **Progress**: Logging every 10,000 lines for large files
- **Graceful Degradation**: Dashboard shows "No data" message if analysis hasn't been run yet

## Performance Characteristics
- **Memory Efficient**: Streaming processing, constant memory usage
- **Scalable**: Can handle large log files (GB+)
- **Append Mode**: Output files in append mode for restart capability
- **Parallel Safe**: User agent analysis can run in parallel on different days

## VS Code Integration
Use Ctrl+Shift+P → "Tasks: Run Task":
- **"Run complete analysis pipeline"**: Execute all steps in sequence (RECOMMENDED)
- **"Run splitter"**: Execute log splitting only
- **"Run tests"**: Run unit tests  
- **"Run UA analysis"**: Run user agent analysis only
- **"Run Active Users analysis"**: Run user activity analysis only
- **"Run Sort Usage analysis"**: Run sort functionality analysis only
- **"Run Streamlit dashboard"**: Start web dashboard
- **"Install requirements"**: Install Python dependencies

## Active Users Analysis Details

### Hourly Analysis
- **Purpose**: Identify peak hours and patterns in system usage
- **Granularity**: Per hour per day
- **Metrics**: Unique users per hour, total number of activities
- **Output**: `hourly_active_users.csv` with heatmap data

### Daily Analysis  
- **Purpose**: Overview of daily user counts
- **Metrics**: Unique users per day, active hours, first/last activity
- **Output**: `daily_active_users.csv` with trend data

### Peak Hours Analysis
- **Purpose**: Identify general peak hours across all days
- **Aggregation**: Average users per hour (all days combined)
- **Output**: `peak_hours_analysis.csv` for optimization planning

### Per-User Analysis
- **Purpose**: Individual user patterns
- **Metrics**: Active hours per user, first/last activity, activity frequency
- **Output**: `user_activity_summary.csv` for usage analysis

## Dashboard Features

### Tab 1: User Agents
- Browser and device analysis (existing functionality)
- KPIs: Unique users, browsers, operating systems
- Interactive charts and filters

### Tab 2: Active Users
- **Daily Activity Overview**: Trend of daily user counts
- **Hourly Heatmap**: Visualization of activity per hour per day
- **KPIs**: Total unique users, average daily users, peak day

### Tab 3: Peak Hours Analysis  
- **Peak Hours Chart**: Bar chart of activity per hour (all days)
- **Peak/Quiet Hours**: Identification of busiest and quietest hours
- **Planning Insights**: Data for system maintenance and resource planning

### Tab 4: Sort Usage Analysis
- **Sort Field Popularity**: Which fields are sorted most often
- **Direction Preference**: ASC vs DESC usage patterns
- **Popular Combinations**: Most used field+direction combinations
- **Daily Trends**: Sort usage trends over time
- **Usage Statistics**: Total actions, unique users, field diversity

## Regex Patterns
```python
# Date extraction (start of line)
DATE_PATTERN = r'^(?P<date>\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}\.\d+'

# User extraction (anywhere in line)  
USER_PATTERN = r'\[User:\s*(?P<user>[A-Z0-9]+)\]'

# UserAgent extraction (for analysis)
RE_UA = r'\[UserAgent:\s*(?P<ua>.+?)\]'

# Timestamp and User extraction (for activity analysis)
TIMESTAMP_USER_PATTERN = r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+).*\[User:\s*(?P<user>[A-Z0-9]+)\]'
```

## Dependencies
- **polars**: High-performance dataframes
- **user-agents**: Browser/OS detection
- **streamlit**: Web dashboard framework  
- **altair**: Data visualization
- **pytest**: Unit testing framework

## Output Files

### User Agent Analysis
- `out/user_agents.csv`: Main dataset with all user agent information
- `out/agg_browsers_by_date.csv`: Browser usage per date
- `out/agg_os_by_date.csv`: Operating system usage per date  
- `out/agg_devices_by_date.csv`: Device type usage per date

### Active Users Analysis
- `out/hourly_active_users.csv`: Unique users per hour per day
- `out/daily_active_users.csv`: Daily user statistics  
- `out/peak_hours_analysis.csv`: Peak hours analysis (all days combined)
- `out/user_activity_summary.csv`: Per-user activity overview

### Sort Usage Analysis
- `out/sort_field_summary.csv`: Sort field popularity statistics
- `out/sort_direction_summary.csv`: ASC vs DESC usage statistics
- `out/sort_combination_summary.csv`: Field+direction combination statistics
- `out/daily_sort_usage.csv`: Daily sort usage trends
- `out/hourly_sort_usage.csv`: Hourly sort usage patterns
- `out/user_sort_patterns.csv`: Per-user sort behavior analysis

### Log Splitting
- `logs/splits/YYYY-MM-DD/{USER}.log`: Split log files per user per day
