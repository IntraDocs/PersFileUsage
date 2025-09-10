# PF-Logs: Personnel File Portal Log Splitter

This tool splits daily log files from a personnel file portal by date and user, creating organized output files for easier analysis.

## Features

- Splits log files by date and user
- Streaming processing (memory efficient)
- Preserves original log line format
- UTF-8 encoding with error handling
- Windows 11 compatible

## Quick Start

### Setup Environment

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Usage

1. Place your log files in `logs/raw/` directory (*.log and *.arc files)
2. Run the splitter:

```powershell
python src/split_logs_by_user.py
```

3. Find split files in `logs/splits/YYYY-MM-DD/{USER}.log`

### Running Tests

```powershell
pytest tests/ -v
```

## Project Structure

```
pf-logs/
├── logs/
│   ├── raw/          # Input log files (*.log and *.arc)
│   └── splits/       # Output files by date/user
├── src/
│   ├── __init__.py
│   └── split_logs_by_user.py  # Main splitter logic
├── tests/
│   └── test_split.py # Unit tests
├── .vscode/          # VS Code configuration
├── requirements.txt
└── README.md
```

## Log Format Requirements

The tool expects log lines with:
- Date format: `YYYY-MM-DD HH:MM:SS.mmm`
- User format: `[User: USERNAME]`

Example log line:
```
2024-01-15 10:30:45.123 INFO [User: USER001] Login successful
```

## VS Code Integration

Use Ctrl+Shift+P and run:
- **Tasks: Run Task** → "Run splitter"
- **Tasks: Run Task** → "Run tests"
- **Debug** → "Debug splitter"
