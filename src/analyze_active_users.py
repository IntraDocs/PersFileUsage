# src/analyze_active_users.py
# Usage: python src/analyze_active_users.py --input logs/splits --output out
from __future__ import annotations
from pathlib import Path
import argparse
import re
import polars as pl
from datetime import datetime

# Regex pattern for extracting timestamp and user
TIMESTAMP_USER_PATTERN = re.compile(r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+).*\[User:\s*(?P<user>[A-Z0-9]+)\]')

def find_log_files(input_dir: Path) -> list[Path]:
    """Find all .log files in the input directory structure."""
    return [p for p in input_dir.rglob("*.log") if p.is_file()]

def extract_activity_from_file(log_file: Path) -> list[dict]:
    """Extract user activity data from a single log file."""
    activities = []
    
    try:
        with log_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                match = TIMESTAMP_USER_PATTERN.match(line)
                if match:
                    timestamp_str = match.group("timestamp")
                    user_id = match.group("user")
                    
                    # Parse timestamp
                    try:
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                        date = dt.date().isoformat()
                        hour = dt.hour
                        minute = dt.minute
                        
                        activities.append({
                            "date": date,
                            "hour": hour,
                            "minute": minute,
                            "timestamp": timestamp_str,
                            "user_id": user_id,
                            "file_path": str(log_file)
                        })
                    except ValueError:
                        # Skip lines with invalid timestamps
                        continue
                        
    except Exception as e:
        print(f"Error processing file {log_file}: {e}")
    
    return activities

def analyze_active_users(input_dir: Path, output_dir: Path) -> None:
    """Analyze active users and generate reports."""
    
    # Find all log files
    log_files = find_log_files(input_dir)
    print(f"Found {len(log_files)} log files to analyze")
    
    # Extract all activities
    all_activities = []
    for i, log_file in enumerate(log_files, 1):
        if i % 100 == 0:
            print(f"Processing file {i}/{len(log_files)}: {log_file.name}")
        activities = extract_activity_from_file(log_file)
        all_activities.extend(activities)
    
    if not all_activities:
        print("No activity data found")
        # Create empty files
        create_empty_reports(output_dir)
        return
    
    # Create DataFrame
    df = pl.DataFrame(all_activities)
    print(f"Extracted {len(all_activities)} activity records")
    
    # Generate reports
    generate_hourly_activity_report(df, output_dir)
    generate_daily_activity_report(df, output_dir)
    generate_peak_hours_report(df, output_dir)
    generate_user_activity_summary(df, output_dir)
    
    print(f"Reports generated in {output_dir}")

def generate_hourly_activity_report(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate hourly active users report."""
    hourly_stats = (
        df.group_by(["date", "hour"])
        .agg([
            pl.n_unique("user_id").alias("unique_users"),
            pl.count("user_id").alias("total_activities"),
            pl.min("timestamp").alias("first_activity"),
            pl.max("timestamp").alias("last_activity")
        ])
        .sort(["date", "hour"])
    )
    
    hourly_stats.write_csv(output_dir / "hourly_active_users.csv")

def generate_daily_activity_report(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate daily active users summary."""
    daily_stats = (
        df.group_by("date")
        .agg([
            pl.n_unique("user_id").alias("unique_users"),
            pl.count("user_id").alias("total_activities"),
            pl.min("hour").alias("first_hour"),
            pl.max("hour").alias("last_hour"),
            pl.min("timestamp").alias("first_activity"),
            pl.max("timestamp").alias("last_activity")
        ])
        .sort("date")
    )
    
    daily_stats.write_csv(output_dir / "daily_active_users.csv")

def generate_peak_hours_report(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate peak hours analysis across all days."""
    peak_hours = (
        df.group_by("hour")
        .agg([
            pl.n_unique("user_id").alias("avg_unique_users"),
            pl.count("user_id").alias("total_activities")
        ])
        .sort("hour")
    )
    
    peak_hours.write_csv(output_dir / "peak_hours_analysis.csv")

def generate_user_activity_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate per-user activity summary."""
    user_summary = (
        df.group_by(["date", "user_id"])
        .agg([
            pl.count("user_id").alias("total_activities"),
            pl.n_unique("hour").alias("active_hours"),
            pl.min("hour").alias("first_hour"),
            pl.max("hour").alias("last_hour"),
            pl.min("timestamp").alias("first_activity"),
            pl.max("timestamp").alias("last_activity")
        ])
        .sort(["date", "user_id"])
    )
    
    user_summary.write_csv(output_dir / "user_activity_summary.csv")

def create_empty_reports(output_dir: Path) -> None:
    """Create empty CSV files with proper headers when no data is found."""
    
    # Empty hourly report
    pl.DataFrame({
        "date": [], "hour": [], "unique_users": [], "total_activities": [],
        "first_activity": [], "last_activity": []
    }).write_csv(output_dir / "hourly_active_users.csv")
    
    # Empty daily report
    pl.DataFrame({
        "date": [], "unique_users": [], "total_activities": [],
        "first_hour": [], "last_hour": [], "first_activity": [], "last_activity": []
    }).write_csv(output_dir / "daily_active_users.csv")
    
    # Empty peak hours report
    pl.DataFrame({
        "hour": [], "avg_unique_users": [], "total_activities": []
    }).write_csv(output_dir / "peak_hours_analysis.csv")
    
    # Empty user summary report
    pl.DataFrame({
        "date": [], "user_id": [], "total_activities": [], "active_hours": [],
        "first_hour": [], "last_hour": [], "first_activity": [], "last_activity": []
    }).write_csv(output_dir / "user_activity_summary.csv")

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze active users from split log files")
    parser.add_argument("--input", default="logs/splits", help="Input directory with split log files")
    parser.add_argument("--output", default="out", help="Output directory for CSV reports")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyze_active_users(input_dir, output_dir)

if __name__ == "__main__":
    main()
