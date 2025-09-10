# Instructions for PF-Logs

## Overview
This tool processes personnel file portal log files, splitting them by date and user for easier analysis.

## Input Format
- Place log files in `logs/raw/` directory
- Files must have `.log` extension
- Each log line should contain:
  - Timestamp: `YYYY-MM-DD HH:MM:SS.mmm`
  - User identifier: `[User: USERNAME]` (alphanumeric)

## Output Format
- Files are created in `logs/splits/YYYY-MM-DD/{USER}.log`
- Original log lines are preserved exactly as-is
- Multiple input files are processed sequentially

## Processing Logic
1. Scan each line for date pattern at the beginning
2. Extract user from anywhere in the line using `[User: USERNAME]` pattern
3. If both date and user are found, append line to appropriate output file
4. Create directories as needed
5. Lines without user or date are skipped

## Error Handling
- Invalid UTF-8 characters are ignored (not crashed)
- Missing directories are created automatically
- Non-existent input files are logged but don't stop processing
- Processing continues even if individual lines fail

## Performance Notes
- Streaming processing: files are read line-by-line
- Memory usage stays constant regardless of file size
- Progress logging every 10,000 lines
- Output files are opened in append mode

## Regex Patterns Used
```python
# Date extraction (start of line)
DATE_PATTERN = r'^(?P<date>\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}\.\d+'

# User extraction (anywhere in line)
USER_PATTERN = r'\[User:\s*(?P<user>[A-Z0-9]+)\]'
```
