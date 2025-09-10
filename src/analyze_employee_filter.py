# src/analyze_employee_filter.py
# Usage: python src/analyze_employee_filter.py --input logs/splits --output out
from __future__ import annotations
from pathlib import Path
import argparse
import re
import polars as pl
from datetime import datetime

# Regex pattern for extracting employee filter information
EMPLOYEE_FILTER_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+).*'
    r'\[User:\s*(?P<user>[A-Z0-9]+)\].*'
    r'Employee filter executed with criteria: Entries:.*?'
    r'(?P<criteria>.+)$'
)

# Pattern to extract individual filter criteria
CRITERIA_PATTERN = re.compile(
    r'\{[^}]*\}(?P<field_name>[^=]+)=\'(?P<filter_value>[^\']*)\''
)

def classify_filter_type(filter_value: str) -> str:
    """Classify the type of filter based on the filter value."""
    if not filter_value:
        return 'empty'
    
    # Compare patterns: extract the operator pattern
    if re.match(r'^>=', filter_value):
        return '>=[value]'
    elif re.match(r'^<=', filter_value):
        return '<=[value]'
    elif re.match(r'^>', filter_value):
        return '>[value]'
    elif re.match(r'^<', filter_value):
        return '<[value]'
    elif re.match(r'^=', filter_value):
        return '=[value]'
    
    # Combined: contains spaces (multiple words)
    if ' ' in filter_value:
        return 'multiple_words'
    
    # Basic: simple string without spaces or comparison operators
    return 'single_word'

def get_filter_pattern(filter_value: str) -> str:
    """Get the filter pattern without the actual value."""
    if not filter_value:
        return 'empty'
    
    # Extract comparison operators
    if re.match(r'^>=', filter_value):
        return '>='
    elif re.match(r'^<=', filter_value):
        return '<='
    elif re.match(r'^>', filter_value):
        return '>'
    elif re.match(r'^<', filter_value):
        return '<'
    elif re.match(r'^=', filter_value):
        return '='
    
    # Count words for non-comparison filters
    word_count = len(filter_value.split())
    if word_count > 1:
        return f'{word_count}_words'
    else:
        return 'single_word'

def find_log_files(input_dir: Path) -> list[Path]:
    """Find all .log files in the input directory structure."""
    return [p for p in input_dir.rglob("*.log") if p.is_file()]

def extract_employee_filter_events_from_file(log_file: Path) -> list[dict]:
    """Extract employee filter events from a single log file."""
    filter_events = []
    
    try:
        with log_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or "Employee filter executed with criteria: Entries:" not in line:
                    continue
                
                match = EMPLOYEE_FILTER_PATTERN.match(line)
                if match:
                    timestamp_str = match.group("timestamp")
                    user_id = match.group("user")
                    criteria = match.group("criteria")
                    
                    # Parse timestamp for date extraction
                    try:
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                        date = dt.date().isoformat()
                        hour = dt.hour
                        
                        # Extract individual criteria
                        criteria_matches = CRITERIA_PATTERN.findall(criteria)
                        
                        for field_name, filter_value in criteria_matches:
                            # Clean up field name (remove namespace parts)
                            clean_field_name = field_name.strip()
                            
                            # Classify filter type and get pattern
                            filter_type = classify_filter_type(filter_value)
                            filter_pattern = get_filter_pattern(filter_value)
                            
                            filter_events.append({
                                "date": date,
                                "hour": hour,
                                "timestamp": timestamp_str,
                                "user_id": user_id,
                                "field_name": clean_field_name,
                                "filter_value": filter_value,
                                "filter_type": filter_type,
                                "filter_pattern": filter_pattern,
                                "file_path": str(log_file)
                            })
                    except ValueError:
                        # Skip lines with invalid timestamps
                        continue
                        
    except Exception as e:
        print(f"Error processing file {log_file}: {e}")
    
    return filter_events

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

def analyze_employee_filter(input_dir: Path, output_dir: Path) -> None:
    """Analyze employee filter usage patterns and generate reports."""
    
    # Find all log files
    log_files = find_log_files(input_dir)
    print(f"Found {len(log_files)} log files to analyze for employee filter usage")
    
    # Extract all filter events
    all_filter_events = []
    for i, log_file in enumerate(log_files, 1):
        if i % 100 == 0:
            print(f"Processing file {i}/{len(log_files)}: {log_file.name}")
        filter_events = extract_employee_filter_events_from_file(log_file)
        all_filter_events.extend(filter_events)
    
    if not all_filter_events:
        print("No employee filter events found")
        create_empty_filter_reports(output_dir)
        return
    
    # Create DataFrame
    df = pl.DataFrame(all_filter_events)
    print(f"Extracted {len(all_filter_events)} employee filter events")
    
    # Get total unique users for percentage calculations
    total_users = get_total_unique_users(output_dir)
    users_using_filters = df["user_id"].n_unique()
    
    # Generate reports
    generate_field_usage_summary(df, output_dir)
    generate_filter_type_summary(df, output_dir)
    generate_filter_pattern_summary(df, output_dir)
    generate_daily_filter_usage(df, output_dir)
    generate_hourly_filter_usage(df, output_dir)
    generate_user_filter_patterns(df, output_dir)
    generate_filter_usage_summary(df, output_dir, total_users, users_using_filters)
    
    print(f"Employee filter reports generated in {output_dir}")
    print(f"Users using employee filters: {users_using_filters}/{total_users} ({users_using_filters/total_users*100:.1f}%)" if total_users > 0 else f"Users using employee filters: {users_using_filters}")

def generate_field_usage_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of which fields are filtered most often."""
    field_stats = (
        df.group_by("field_name")
        .agg([
            pl.len().alias("total_filters"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("date").alias("days_used")
        ])
        .sort("total_filters", descending=True)
    )
    
    field_stats.write_csv(output_dir / "employee_filter_fields.csv")

def generate_filter_type_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of filter types used."""
    type_stats = (
        df.group_by("filter_type")
        .agg([
            pl.len().alias("total_usage"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("field_name").alias("different_fields")
        ])
        .sort("total_usage", descending=True)
    )
    
    type_stats.write_csv(output_dir / "employee_filter_types.csv")

def generate_filter_pattern_summary(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate summary of filter patterns used (without values)."""
    pattern_stats = (
        df.group_by("filter_pattern")
        .agg([
            pl.len().alias("total_usage"),
            pl.n_unique("user_id").alias("unique_users"),
            pl.n_unique("field_name").alias("different_fields")
        ])
        .sort("total_usage", descending=True)
    )
    
    pattern_stats.write_csv(output_dir / "employee_filter_patterns.csv")

def generate_daily_filter_usage(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate daily filter usage statistics."""
    daily_stats = (
        df.group_by("date")
        .agg([
            pl.len().alias("total_filters"),
            pl.n_unique("user_id").alias("users_using_filters"),
            pl.n_unique("field_name").alias("different_fields_filtered")
        ])
        .sort("date")
    )
    
    daily_stats.write_csv(output_dir / "daily_employee_filter_usage.csv")

def generate_hourly_filter_usage(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate hourly filter usage patterns."""
    hourly_stats = (
        df.group_by("hour")
        .agg([
            pl.len().alias("total_filters"),
            pl.n_unique("user_id").alias("users_using_filters"),
            pl.n_unique("field_name").alias("different_fields_filtered")
        ])
        .sort("hour")
    )
    
    hourly_stats.write_csv(output_dir / "hourly_employee_filter_usage.csv")

def generate_user_filter_patterns(df: pl.DataFrame, output_dir: Path) -> None:
    """Generate per-user filter usage behavior analysis."""
    
    # Get most used field per user
    user_field_counts = (
        df.group_by(["user_id", "field_name"])
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
    )
    
    most_used_per_user = (
        user_field_counts
        .group_by("user_id")
        .agg(pl.col("field_name").first().alias("most_used_field"))
    )
    
    user_stats = (
        df.group_by("user_id")
        .agg([
            pl.len().alias("total_filters"),
            pl.n_unique("field_name").alias("different_fields_used"),
            pl.n_unique("date").alias("days_active_filtering")
        ])
        .join(most_used_per_user, on="user_id", how="left")
        .sort("total_filters", descending=True)
    )
    
    user_stats.write_csv(output_dir / "user_employee_filter_patterns.csv")

def generate_filter_usage_summary(df: pl.DataFrame, output_dir: Path, total_users: int, users_using_filters: int) -> None:
    """Generate summary statistics about employee filter usage."""
    
    # Calculate percentage of users using employee filters
    percentage_using_filters = (users_using_filters / total_users * 100) if total_users > 0 else 0
    
    # Get most popular field
    most_popular_field = (
        df.group_by("field_name")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)["field_name"]
        .first()
    )
    
    # Get most common filter type
    most_common_type = (
        df.group_by("filter_type")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)["filter_type"]
        .first()
    )
    
    # Calculate average filters per user
    avg_filters_per_user = (df.height / users_using_filters) if users_using_filters > 0 else 0
    
    # Create summary DataFrame with proper types
    summary_data = {
        "metric": [
            "total_employee_filters",
            "users_using_filters",
            "total_users_in_system", 
            "percentage_users_using_filters",
            "different_fields_filtered",
            "most_popular_field",
            "most_common_filter_type",
            "avg_filters_per_user"
        ],
        "value": [
            str(df.height),
            str(users_using_filters),
            str(total_users),
            f"{percentage_using_filters:.1f}",
            str(df["field_name"].n_unique()),
            str(most_popular_field),
            str(most_common_type),
            f"{avg_filters_per_user:.1f}"
        ]
    }
    
    summary_df = pl.DataFrame(summary_data)
    summary_df.write_csv(output_dir / "employee_filter_summary.csv")

def create_empty_filter_reports(output_dir: Path) -> None:
    """Create empty CSV files with proper headers when no data is found."""
    
    # Empty field usage
    pl.DataFrame({
        "field_name": [], "total_filters": [], "unique_users": [], "days_used": []
    }).write_csv(output_dir / "employee_filter_fields.csv")
    
    # Empty filter types
    pl.DataFrame({
        "filter_type": [], "total_usage": [], "unique_users": [], "different_fields": []
    }).write_csv(output_dir / "employee_filter_types.csv")
    
    # Empty filter patterns
    pl.DataFrame({
        "filter_pattern": [], "total_usage": [], "unique_users": [], "different_fields": []
    }).write_csv(output_dir / "employee_filter_patterns.csv")
    
    # Empty daily usage
    pl.DataFrame({
        "date": [], "total_filters": [], "users_using_filters": [], "different_fields_filtered": []
    }).write_csv(output_dir / "daily_employee_filter_usage.csv")
    
    # Empty hourly usage
    pl.DataFrame({
        "hour": [], "total_filters": [], "users_using_filters": [], "different_fields_filtered": []
    }).write_csv(output_dir / "hourly_employee_filter_usage.csv")
    
    # Empty user patterns
    pl.DataFrame({
        "user_id": [], "total_filters": [], "different_fields_used": [],
        "days_active_filtering": [], "most_used_field": []
    }).write_csv(output_dir / "user_employee_filter_patterns.csv")
    
    # Empty summary
    pl.DataFrame({
        "metric": [], "value": []
    }).write_csv(output_dir / "employee_filter_summary.csv")

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze employee filter usage from split log files")
    parser.add_argument("--input", default="logs/splits", help="Input directory with split log files")
    parser.add_argument("--output", default="out", help="Output directory for CSV reports")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyze_employee_filter(input_dir, output_dir)

if __name__ == "__main__":
    main()
