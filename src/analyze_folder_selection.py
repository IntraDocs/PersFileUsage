# src/analyze_folder_selection.py
# Usage: python src/analyze_folder_selection.py --input logs/splits --output out
from __future__ import annotations
from pathlib import Path
import argparse
import re
import polars as pl
from datetime import datetime

# Regex pattern for extracting folder selection information
FOLDER_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+).*'
    r'\[User:\s*(?P<user>[A-Z0-9]+)\].*'
    r'FolderSelected:\s*(?P<folder_name>.+?)$'
)

def find_log_files(input_dir: Path) -> list[Path]:
    """Find all .log files in the input directory structure."""
    return [p for p in input_dir.rglob("*.log") if p.is_file()]

def extract_folder_events_from_file(log_file: Path) -> list[dict]:
    """Extract folder selection events from a single log file."""
    folder_events = []
    
    try:
        with log_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or "FolderSelected:" not in line:
                    continue
                
                match = FOLDER_PATTERN.match(line)
                if match:
                    timestamp_str = match.group("timestamp")
                    user_id = match.group("user")
                    folder_name = match.group("folder_name").strip()
                    
                    # Parse timestamp for date extraction
                    try:
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                        date = dt.date().isoformat()
                        hour = dt.hour
                        
                        folder_events.append({
                            "date": date,
                            "hour": hour,
                            "timestamp": timestamp_str,
                            "user_id": user_id,
                            "folder_name": folder_name,
                            "file_path": str(log_file)
                        })
                    except ValueError:
                        # Skip lines with invalid timestamps
                        continue
                        
    except Exception as e:
        print(f"Error processing file {log_file}: {e}")
    
    return folder_events

def get_total_unique_users(output_dir: Path) -> int:
    """Get total number of unique users from user agents data."""
    user_agents_path = output_dir / "user_agents.csv"
    if user_agents_path.exists():
        try:
            df = pl.read_csv(user_agents_path)
            return df["user_id"].n_unique()
        except Exception:
            return 0
    return 0

def analyze_folder_selection(input_dir: Path, output_dir: Path) -> None:
    """Analyze folder selection patterns and generate reports."""
    
    # Find all log files
    log_files = find_log_files(input_dir)
    print(f"Found {len(log_files)} log files to analyze for folder selection")
    
    # Extract all folder events
    all_folder_events = []
    for i, log_file in enumerate(log_files, 1):
        if i % 100 == 0:
            print(f"Processing file {i}/{len(log_files)}: {log_file.name}")
        folder_events = extract_folder_events_from_file(log_file)
        all_folder_events.extend(folder_events)
    
    if not all_folder_events:
        print("No folder selection events found")
        create_empty_folder_reports(output_dir)
        return
    
    # Create DataFrame
    df = pl.DataFrame(all_folder_events)
    print(f"Extracted {len(all_folder_events)} folder selection events")
    
    # Get total unique users for percentage calculations
    total_users = get_total_unique_users(output_dir)
    users_using_folders = df["user_id"].n_unique()
    
    # Generate reports
    generate_folder_popularity_summary(df, output_dir)
    generate_daily_folder_usage(df, output_dir)
    generate_hourly_folder_usage(df, output_dir)
    generate_user_folder_patterns(df, output_dir)
    generate_folder_usage_summary(df, output_dir, total_users, users_using_folders)
    
    print(f"Folder selection reports generated in {output_dir}")
    print(f"Users using folder selection: {users_using_folders}/{total_users} ({users_using_folders/total_users*100:.1f}%)" if total_users > 0 else f"Users using folder selection: {users_using_folders}")

def generate_folder_popularity_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of which folders are selected most often."""
    folder_stats = (
        df.group_by("folder_name")
        .agg([
            pl.count("folder_name").alias("total_selections"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("date").alias("days_used")
        ])
        .sort("total_selections", descending=True)
    )
    
    folder_stats.write_csv(output_dir / "folder_popularity_summary.csv")

def generate_daily_folder_usage(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate daily folder usage statistics."""
    daily_stats = (
        df.group_by("date")
        .agg([
            pl.count("folder_name").alias("total_folder_selections"),
            pl.n_unique("user_id").alias("users_selecting_folders"),
            pl.n_unique("folder_name").alias("different_folders_selected")
        ])
        .sort("date")
    )
    
    daily_stats.write_csv(output_dir / "daily_folder_usage.csv")

def generate_hourly_folder_usage(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate hourly folder usage patterns."""
    hourly_stats = (
        df.group_by("hour")
        .agg([
            pl.count("folder_name").alias("total_folder_selections"),
            pl.n_unique("user_id").alias("avg_users_selecting"),
            pl.n_unique("folder_name").alias("different_folders_selected")
        ])
        .sort("hour")
    )
    
    hourly_stats.write_csv(output_dir / "hourly_folder_usage.csv")

def generate_user_folder_patterns(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate per-user folder selection behavior analysis."""
    
    # First get the most used folder per user
    user_folder_counts = (
        df.group_by(["user_id", "folder_name"])
        .agg(pl.count("folder_name").alias("count"))
        .sort("count", descending=True)
    )
    
    # Get the top folder for each user
    most_used_per_user = (
        user_folder_counts
        .group_by("user_id")
        .agg(pl.col("folder_name").first().alias("most_used_folder"))
    )
    
    user_stats = (
        df.group_by("user_id")
        .agg([
            pl.count("folder_name").alias("total_folder_selections"),
            pl.n_unique("folder_name").alias("different_folders_used"),
            pl.n_unique("date").alias("days_active_selecting")
        ])
        .join(most_used_per_user, on="user_id", how="left")
        .sort("total_folder_selections", descending=True)
    )
    
    user_stats.write_csv(output_dir / "user_folder_patterns.csv")

def generate_folder_usage_summary(df: pl.DataFrame, output_dir: Path, total_users: int, users_using_folders: int) -> None:
    """Generate summary statistics about folder selection usage."""
    
    # Calculate percentage of users using folder selection
    percentage_using_folders = (users_using_folders / total_users * 100) if total_users > 0 else 0
    
    # Get most popular folder
    most_popular_folder = (
        df.group_by("folder_name")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)["folder_name"]
        .first()
    )
    
    # Calculate average selections per user
    avg_selections_per_user = (df.height / users_using_folders) if users_using_folders > 0 else 0
    
    # Create summary DataFrame with proper types
    summary_data = {
        "metric": [
            "total_folder_selections",
            "users_using_folders",
            "total_users_in_system", 
            "percentage_users_using_folders",
            "different_folders_available",
            "most_popular_folder",
            "avg_selections_per_user"
        ],
        "value": [
            str(df.height),
            str(users_using_folders),
            str(total_users),
            f"{percentage_using_folders:.1f}",
            str(df["folder_name"].n_unique()),
            str(most_popular_folder),
            f"{avg_selections_per_user:.1f}"
        ]
    }
    
    summary_df = pl.DataFrame(summary_data)
    summary_df.write_csv(output_dir / "folder_selection_summary.csv")

def create_empty_folder_reports(output_dir: Path) -> None:
    """Create empty CSV files with proper headers when no data is found."""
    
    # Empty folder popularity summary
    pl.DataFrame({
        "folder_name": [], "total_selections": [], "unique_users": [], "days_used": []
    }).write_csv(output_dir / "folder_popularity_summary.csv")
    
    # Empty daily usage
    pl.DataFrame({
        "date": [], "total_folder_selections": [], "users_selecting_folders": [], 
        "different_folders_selected": []
    }).write_csv(output_dir / "daily_folder_usage.csv")
    
    # Empty hourly usage
    pl.DataFrame({
        "hour": [], "total_folder_selections": [], "avg_users_selecting": [], "different_folders_selected": []
    }).write_csv(output_dir / "hourly_folder_usage.csv")
    
    # Empty user patterns
    pl.DataFrame({
        "user_id": [], "total_folder_selections": [], "different_folders_used": [],
        "days_active_selecting": [], "most_used_folder": []
    }).write_csv(output_dir / "user_folder_patterns.csv")
    
    # Empty summary
    pl.DataFrame({
        "metric": [], "value": []
    }).write_csv(output_dir / "folder_selection_summary.csv")

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze folder selection usage from split log files")
    parser.add_argument("--input", default="logs/splits", help="Input directory with split log files")
    parser.add_argument("--output", default="out", help="Output directory for CSV reports")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyze_folder_selection(input_dir, output_dir)

if __name__ == "__main__":
    main()
