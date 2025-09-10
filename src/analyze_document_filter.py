#!/usr/bin/env python3
"""
Document Filter Analysis Script

Analyzes document filter usage patterns from Personnel File Portal logs.
Only processes lines containing "Document filter executed with criteria: Entries:"

Usage:
    python analyze_document_filter.py --input logs/splits --output out
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
import polars as pl
from typing import List, Dict, Any, Tuple


def extract_criteria_patterns(criteria_text: str) -> List[Tuple[str, str]]:
    """
    Extract field-value pairs from document filter criteria.
    
    Args:
        criteria_text: The criteria portion of the log line
        
    Returns:
        List of (field_name, filter_value) tuples
    """
    # Pattern to match field definitions like {namespace}field='value'
    pattern = r'\{[^}]+\}([^=]+)=\'([^\']*)\''
    matches = re.findall(pattern, criteria_text)
    return matches


def classify_filter_type(filter_value: str) -> str:
    """
    Classify the type of filter based on the filter value.
    
    Args:
        filter_value: The filter value string
        
    Returns:
        Filter type classification
    """
    if not filter_value.strip():
        return "empty"
    
    # Check for comparison operators
    if filter_value.startswith('>='):
        return ">=[value]"
    elif filter_value.startswith('<='):
        return "<=[value]"
    elif filter_value.startswith('>'):
        return ">[value]"
    elif filter_value.startswith('<'):
        return "<[value]"
    elif filter_value.startswith('='):
        return "=[value]"
    
    # Check for multiple words
    words = filter_value.split()
    if len(words) > 1:
        return "multiple_words"
    else:
        return "single_word"


def get_filter_pattern(filter_value: str) -> str:
    """
    Get the pattern of the filter value for grouping similar filters.
    
    Args:
        filter_value: The filter value string
        
    Returns:
        Pattern string for grouping
    """
    if not filter_value.strip():
        return "empty"
    
    # Check for comparison operators first
    if filter_value.startswith('>='):
        return ">="
    elif filter_value.startswith('<='):
        return "<="
    elif filter_value.startswith('>'):
        return ">"
    elif filter_value.startswith('<'):
        return "<"
    elif filter_value.startswith('='):
        return "="
    
    # For non-comparison filters, return word count pattern
    words = filter_value.split()
    if len(words) == 1:
        return "single_word"
    elif len(words) == 2:
        return "2_words"
    elif len(words) == 3:
        return "3_words"
    elif len(words) == 4:
        return "4_words"
    else:
        return f"{len(words)}_words"


def extract_document_filter_events_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract document filter events from a single log file.
    Only processes lines with "Document filter executed with criteria: Entries:"
    
    Args:
        file_path: Path to the log file
        
    Returns:
        List of document filter event dictionaries
    """
    events = []
    
    # Pattern to match document filter log lines
    pattern = r'(\d{4}-\d{2}-\d{2}) (\d{2}):\d{2}:\d{2}\.\d+ .+ \[User: ([^\]]+)\] .+ Document filter executed with criteria: Entries: (.+)$'
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if 'Document filter executed with criteria: Entries:' in line:
                    match = re.search(pattern, line)
                    if match:
                        date_str, hour_str, user_id, criteria = match.groups()
                        
                        # Extract field-value pairs from criteria
                        field_value_pairs = extract_criteria_patterns(criteria)
                        
                        for field_name, filter_value in field_value_pairs:
                            filter_type = classify_filter_type(filter_value)
                            filter_pattern = get_filter_pattern(filter_value)
                            
                            events.append({
                                'date': date_str,
                                'hour': int(hour_str),
                                'user_id': user_id,
                                'field_name': field_name,
                                'filter_value': filter_value,
                                'filter_type': filter_type,
                                'filter_pattern': filter_pattern,
                                'file_path': str(file_path)
                            })
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    
    return events


def generate_field_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Generate summary statistics for document filter fields."""
    return (
        df.group_by("field_name")
        .agg([
            pl.len().alias("total_filters"),
            pl.col("user_id").n_unique().alias("unique_users")
        ])
        .sort("total_filters", descending=True)
    )


def generate_filter_type_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Generate summary statistics for document filter types."""
    return (
        df.group_by("filter_type")
        .agg([
            pl.len().alias("total_usage"),
            pl.col("user_id").n_unique().alias("unique_users"),
            pl.col("field_name").n_unique().alias("different_fields")
        ])
        .sort("total_usage", descending=True)
    )


def generate_filter_pattern_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Generate summary statistics for document filter patterns."""
    return (
        df.group_by("filter_pattern")
        .agg([
            pl.len().alias("total_usage"),
            pl.col("user_id").n_unique().alias("unique_users"),
            pl.col("field_name").n_unique().alias("different_fields")
        ])
        .sort("total_usage", descending=True)
    )


def generate_daily_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Generate daily document filter usage statistics."""
    return (
        df.group_by("date")
        .agg([
            pl.len().alias("total_filters"),
            pl.col("user_id").n_unique().alias("users_using_filters"),
            pl.col("field_name").n_unique().alias("different_fields_filtered")
        ])
        .sort("date")
    )


def generate_hourly_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Generate hourly document filter usage statistics."""
    return (
        df.group_by("hour")
        .agg([
            pl.len().alias("total_filters"),
            pl.col("user_id").n_unique().alias("users_using_filters"),
            pl.col("field_name").n_unique().alias("different_fields_filtered")
        ])
        .sort("hour")
    )


def generate_user_pattern_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Generate user-level document filter pattern statistics."""
    return (
        df.group_by(["user_id", "filter_pattern"])
        .agg([
            pl.len().alias("usage_count"),
            pl.col("field_name").n_unique().alias("different_fields")
        ])
        .sort(["user_id", "usage_count"], descending=[False, True])
    )


def generate_overall_summary(df: pl.DataFrame, user_agents_df: pl.DataFrame = None) -> pl.DataFrame:
    """Generate overall document filter usage summary."""
    total_filters = df.height
    users_using_filters = df["user_id"].n_unique()
    different_fields = df["field_name"].n_unique()
    
    # Get total users from user agents data if available
    total_users = users_using_filters  # Default fallback
    if user_agents_df is not None and user_agents_df.height > 0:
        total_users = user_agents_df["user_id"].n_unique()
    
    percentage_using_filters = (users_using_filters / total_users * 100) if total_users > 0 else 0.0
    avg_filters_per_user = total_filters / users_using_filters if users_using_filters > 0 else 0.0
    
    # Get most popular field and most common filter type
    most_popular_field = "N/A"
    most_common_filter_type = "N/A"
    
    if df.height > 0:
        field_summary = generate_field_summary(df)
        if field_summary.height > 0:
            most_popular_field = field_summary.row(0)[0]
        
        type_summary = generate_filter_type_summary(df)
        if type_summary.height > 0:
            most_common_filter_type = type_summary.row(0)[0]
    
    summary_data = [
        ("total_document_filters", str(total_filters)),
        ("users_using_filters", str(users_using_filters)),
        ("total_users_in_system", str(total_users)),
        ("percentage_users_using_filters", f"{percentage_using_filters:.1f}"),
        ("different_fields_filtered", str(different_fields)),
        ("most_popular_field", most_popular_field),
        ("most_common_filter_type", most_common_filter_type),
        ("avg_filters_per_user", f"{avg_filters_per_user:.1f}")
    ]
    
    return pl.DataFrame(summary_data, schema={"metric": pl.Utf8, "value": pl.Utf8})


def main():
    parser = argparse.ArgumentParser(description='Analyze document filter usage from Personnel File Portal logs')
    parser.add_argument('--input', required=True, help='Input directory containing split log files')
    parser.add_argument('--output', required=True, help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # Find all log files
    log_files = []
    for date_dir in input_dir.iterdir():
        if date_dir.is_dir():
            log_files.extend(list(date_dir.glob("*.log")))
    
    print(f"Found {len(log_files)} log files to analyze for document filter usage")
    
    # Extract all document filter events
    all_events = []
    for i, log_file in enumerate(log_files, 1):
        if i % 100 == 0:
            print(f"Processing file {i}/{len(log_files)}: {log_file.name}")
        
        events = extract_document_filter_events_from_file(log_file)
        all_events.extend(events)
    
    print(f"Extracted {len(all_events)} document filter events")
    
    if not all_events:
        print("No document filter events found. Exiting.")
        return
    
    # Create DataFrame
    df = pl.DataFrame(all_events)
    
    # Load user agents data for total user count
    user_agents_df = None
    user_agents_file = output_dir / "user_agents.csv"
    if user_agents_file.exists():
        try:
            user_agents_df = pl.read_csv(user_agents_file)
        except Exception as e:
            print(f"Warning: Could not load user agents data: {e}")
    
    # Generate all reports
    field_summary = generate_field_summary(df)
    type_summary = generate_filter_type_summary(df)
    pattern_summary = generate_filter_pattern_summary(df)
    daily_summary = generate_daily_summary(df)
    hourly_summary = generate_hourly_summary(df)
    user_patterns = generate_user_pattern_summary(df)
    overall_summary = generate_overall_summary(df, user_agents_df)
    
    # Save reports
    field_summary.write_csv(output_dir / "document_filter_fields.csv")
    type_summary.write_csv(output_dir / "document_filter_types.csv")
    pattern_summary.write_csv(output_dir / "document_filter_patterns.csv")
    daily_summary.write_csv(output_dir / "daily_document_filter_usage.csv")
    hourly_summary.write_csv(output_dir / "hourly_document_filter_usage.csv")
    user_patterns.write_csv(output_dir / "user_document_filter_patterns.csv")
    overall_summary.write_csv(output_dir / "document_filter_summary.csv")
    
    print("Document filter reports generated in", output_dir)
    
    # Print summary
    users_using_filters = df["user_id"].n_unique()
    total_users = users_using_filters
    if user_agents_df is not None and user_agents_df.height > 0:
        total_users = user_agents_df["user_id"].n_unique()
    
    percentage = (users_using_filters / total_users * 100) if total_users > 0 else 0.0
    print(f"Users using document filters: {users_using_filters}/{total_users} ({percentage:.1f}%)")


if __name__ == "__main__":
    main()
