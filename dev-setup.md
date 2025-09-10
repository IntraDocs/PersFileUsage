# Development Setup Guide

## Prerequisites
- Windows 11
- Python 3.12+ installed
- Git
- VS Code with Python extension

## Initial Setup

### 1. Clone and Setup Environment
```powershell
# Navigate to project directory
cd E:\Development\Source\Other\persfile-logs

# Create virtual environment
python -m venv .venv

# Activate environment
.\.venv\Scripts\Activate.ps1

# Verify Python version
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. VS Code Configuration
The project includes pre-configured VS Code settings:
- Python interpreter set to `.venv`
- Pytest testing enabled
- Format on save enabled
- Debugging configurations ready

### 3. Development Workflow

#### Running the Splitter
```powershell
# Method 1: Direct execution
python src/split_logs_by_user.py

# Method 2: VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "Run splitter"

# Method 3: VS Code debugging
# F5 or "Debug splitter" configuration
```

#### Running Tests
```powershell
# Method 1: Command line
pytest tests/ -v

# Method 2: VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "Run tests"

# Method 3: VS Code Test Explorer
# Use the Test icon in the sidebar
```

### 4. Adding New Features

#### Adding a New Function
1. Add function to `src/split_logs_by_user.py`
2. Add corresponding tests to `tests/test_split.py`
3. Run tests to verify functionality
4. Update documentation if needed

#### Adding Dependencies
1. Add to `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Test that everything still works

### 5. Testing Strategy

#### Unit Tests
- Test individual functions in isolation
- Use temporary directories for file operations
- Mock external dependencies when needed

#### Integration Tests
- Test end-to-end workflow
- Use sample log files
- Verify output file structure and content

#### Sample Test Data
Create test log files in `tests/data/` (git-ignored):
```
2024-01-15 10:30:45.123 INFO [User: TESTUSER1] Sample log entry
2024-01-15 10:31:22.456 ERROR [User: TESTUSER2] Another log entry
```

### 6. Code Style Guidelines
- Use type hints for function parameters and returns
- Follow PEP 8 naming conventions
- Add docstrings for all functions
- Keep functions focused and testable
- Use meaningful variable names

### 7. Debugging Tips

#### Common Issues
- Path separator issues: Use `pathlib.Path` for cross-platform compatibility
- Encoding issues: Always specify `encoding='utf-8'` and `errors='ignore'`
- Regex issues: Test patterns with online regex testers first

#### VS Code Debugging
- Set breakpoints in code
- Use "Debug splitter" configuration
- Check variables in Debug Console
- Step through code line by line

### 8. Git Workflow
```powershell
# Check status
git status

# Add changes
git add .

# Commit with meaningful message
git commit -m "Add feature: XYZ"

# Push to remote (when configured)
git push origin main
```
