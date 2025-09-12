# src/analyze_sort_usage.py
# Usage: python src/analyze_sort_usage.py --input logs/splits --output out
from __future__ import annotations
from pathlib import Path
import argparse
import re
import polars as pl
from datetime import datetime

# Regex pattern for extracting sort information
SORT_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+).*'
    r'\[User:\s*(?P<user>[A-Z0-9]+)\].*'
    r'Result grid sort changed\. new order:\s*\{[^}]*\}(?P<sort_field>\w+)\s+(?P<sort_direction>ASC|DESC)'
)

def find_log_files(input_dir: Path) -> list[Path]:
    """Find all .log files in the input directory structure."""
    return [p for p in input_dir.rglob("*.log") if p.is_file()]

def extract_sort_events_from_file(log_file: Path) -> list[dict]:
    """Extract sort events from a single log file."""
    sort_events = []
    
    try:
        with log_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or "Result grid sort changed" not in line:
                    continue
                
                match = SORT_PATTERN.match(line)
                if match:
                    timestamp_str = match.group("timestamp")
                    user_id = match.group("user")
                    sort_field = match.group("sort_field")
                    sort_direction = match.group("sort_direction")
                    
                    # Parse timestamp for date extraction
                    try:
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                        date = dt.date().isoformat()
                        hour = dt.hour
                        
                        sort_events.append({
                            "date": date,
                            "hour": hour,
                            "timestamp": timestamp_str,
                            "user_id": user_id,
                            "sort_field": sort_field,
                            "sort_direction": sort_direction,
                            "sort_combination": f"{sort_field} {sort_direction}",
                            "file_path": str(log_file)
                        })
                    except ValueError:
                        # Skip lines with invalid timestamps
                        continue
                        
    except Exception as e:
        print(f"Error processing file {log_file}: {e}")
    
    return sort_events

def analyze_sort_usage(input_dir: Path, output_dir: Path) -> None:
    """Analyze sort usage patterns and generate reports."""
    
    # Find all log files
    log_files = find_log_files(input_dir)
    print(f"Found {len(log_files)} log files to analyze for sort usage")
    
    # Extract all sort events
    all_sort_events = []
    for i, log_file in enumerate(log_files, 1):
        if i % 100 == 0:
            print(f"Processing file {i}/{len(log_files)}: {log_file.name}")
        sort_events = extract_sort_events_from_file(log_file)
        all_sort_events.extend(sort_events)
    
    if not all_sort_events:
        print("No sort events found")
        create_empty_sort_reports(output_dir)
        return
    
    # Create DataFrame
    df = pl.DataFrame(all_sort_events)
    print(f"Extracted {len(all_sort_events)} sort events")
    
    # Generate reports
    generate_sort_field_summary(df, output_dir)
    generate_sort_direction_summary(df, output_dir)
    generate_sort_combination_summary(df, output_dir)
    generate_daily_sort_usage(df, output_dir)
    generate_hourly_sort_usage(df, output_dir)
    generate_user_sort_patterns(df, output_dir)
    
    print(f"Sort usage reports generated in {output_dir}")

def generate_sort_field_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of which fields are sorted most often."""
    sort_field_stats = (
        df.group_by("sort_field")
        .agg([
            pl.count("sort_field").alias("total_uses"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("date").alias("days_used")
        ])
        .sort("total_uses", descending=True)
    )
    
    sort_field_stats.write_csv(output_dir / "sort_field_summary.csv")

def generate_sort_direction_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of ASC vs DESC usage."""
    direction_stats = (
        df.group_by("sort_direction")
        .agg([
            pl.count("sort_direction").alias("total_uses"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("date").alias("days_used")
        ])
        .sort("total_uses", descending=True)
    )
    
    direction_stats.write_csv(output_dir / "sort_direction_summary.csv")

def generate_sort_combination_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of field+direction combinations."""
    combination_stats = (
        df.group_by("sort_combination")
        .agg([
            pl.count("sort_combination").alias("total_uses"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("date").alias("days_used")
        ])
        .sort("total_uses", descending=True)
    )
    
    combination_stats.write_csv(output_dir / "sort_combination_summary.csv")

def generate_daily_sort_usage(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate daily sort usage statistics."""
    daily_stats = (
        df.group_by("date")
        .agg([
            pl.count("sort_field").alias("total_sort_actions"),
            pl.n_unique("user_id").alias("users_using_sort"),
            pl.n_unique("sort_field").alias("different_fields_sorted"),
            pl.n_unique("sort_combination").alias("different_combinations")
        ])
        .sort("date")
    )
    
    daily_stats.write_csv(output_dir / "daily_sort_usage.csv")

def generate_hourly_sort_usage(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate hourly sort usage patterns."""
    hourly_stats = (
        df.group_by("hour")
        .agg([
            pl.count("sort_field").alias("total_sort_actions"),
            pl.n_unique("user_id").alias("avg_users_sorting"),
            pl.n_unique("sort_field").alias("different_fields_sorted")
        ])
        .sort("hour")
    )
    
    hourly_stats.write_csv(output_dir / "hourly_sort_usage.csv")

def generate_user_sort_patterns(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate per-user sort behavior analysis."""
    user_stats = (
        df.group_by("user_id")
        .agg([
            pl.count("sort_field").alias("total_sort_actions"),
            pl.n_unique("sort_field").alias("different_fields_used"),
            pl.n_unique("sort_combination").alias("different_combinations_used"),
            pl.n_unique("date").alias("days_active_sorting"),
            pl.col("sort_field").mode().first().alias("most_used_field"),
            pl.col("sort_direction").mode().first().alias("preferred_direction")
        ])
        .sort("total_sort_actions", descending=True)
    )
    
    user_stats.write_csv(output_dir / "user_sort_patterns.csv")

def create_empty_sort_reports(output_dir: Path) -> None:
    """Create empty CSV files with proper headers when no data is found."""
    
    # Empty sort field summary
    pl.DataFrame({
        "sort_field": [], "total_uses": [], "unique_users": [], "days_used": []
    }).write_csv(output_dir / "sort_field_summary.csv")
    
    # Empty sort direction summary
    pl.DataFrame({
        "sort_direction": [], "total_uses": [], "unique_users": [], "days_used": []
    }).write_csv(output_dir / "sort_direction_summary.csv")
    
    # Empty sort combination summary
    pl.DataFrame({
        "sort_combination": [], "total_uses": [], "unique_users": [], "days_used": []
    }).write_csv(output_dir / "sort_combination_summary.csv")
    
    # Empty daily usage
    pl.DataFrame({
        "date": [], "total_sort_actions": [], "users_using_sort": [], 
        "different_fields_sorted": [], "different_combinations": []
    }).write_csv(output_dir / "daily_sort_usage.csv")
    
    # Empty hourly usage
    pl.DataFrame({
        "hour": [], "total_sort_actions": [], "avg_users_sorting": [], "different_fields_sorted": []
    }).write_csv(output_dir / "hourly_sort_usage.csv")
    
    # Empty user patterns
    pl.DataFrame({
        "user_id": [], "total_sort_actions": [], "different_fields_used": [],
        "different_combinations_used": [], "days_active_sorting": [],
        "most_used_field": [], "preferred_direction": []
    }).write_csv(output_dir / "user_sort_patterns.csv")

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze sort functionality usage from split log files")
    parser.add_argument("--input", default="logs/splits", help="Input directory with split log files")
    parser.add_argument("--output", default="out", help="Output directory for CSV reports")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyze_sort_usage(input_dir, output_dir)

if __name__ == "__main__":
    main()
