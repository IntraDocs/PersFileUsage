# Personnel File Portal Usage Dashboard

This dashboard visualizes usage data from the Personnel File Portal system. It provides insights into user behavior, browser usage, activity patterns, and feature usage.

## 🎯 Features

- **User Agents Analysis**: Browser, OS, and device statistics
- **Active Users**: Daily and hourly activity patterns
- **Peak Hours Analysis**: When the system is most actively used
- **Sort Usage Analysis**: How users sort data in the system
- **Folder Selection Analysis**: Which folders are most accessed
- **Employee Filter Analysis**: How users filter employee data
- **Document Filter Analysis**: How users filter document data
- **Panel Selection Analysis**: Which panels users are using
- **Data Privacy**: Only analyzed CSV results are shared, raw logs excluded

## 📊 Dashboard Usage

### Run Locally

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

### Deployed App

This dashboard is deployed on Streamlit Cloud and can be accessed [here](https://intradocs-persfileusage.streamlit.app) (link will be active after deployment).

## 🛠️ Data Generation

The dashboard relies on CSV data files in the `out/` directory. These files are already included in the repository.

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
