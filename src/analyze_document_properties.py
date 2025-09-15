# analyze_document_properties.py
import re
import os
from pathlib import Path
import polars as pl
import datetime
from collections import defaultdict

def extract_user_from_log(line):
    """Extract user from a log line."""
    user_match = re.search(r'\[User: ([^\]]+)\]', line)
    if user_match:
        return user_match.group(1)
    return "Unknown"

def analyze_document_properties(logs_dir, output_dir, verbose=False):
    """
    Analyze logs for document properties changes and dialog openings.
    
    Args:
        logs_dir (str or Path): Directory containing log files
        output_dir (str or Path): Directory to write output files
        verbose (bool): Whether to print verbose output
    """
    logs_dir = Path(logs_dir)
    output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"Analyzing document properties changes in logs...")
    
    # Dictionary to store document properties changes data
    properties_changes_data = {
        "total_changes": 0,
        "unique_users": set(),
        "documents_affected": [],  # List of document counts per change
        "user_changes": defaultdict(int)  # Track changes per user
    }
    
    # Dictionary to store edit dialog openings data
    edit_dialog_data = {
        "total_openings": 0,
        "unique_users": set(),
        "user_openings": defaultdict(int)  # Track openings per user
    }
    
    # Pattern for document attributes changed
    properties_change_pattern = re.compile(r'Document attributes changed: (\d+) document')
    
    # Pattern for edit attributes dialog opened
    edit_dialog_pattern = re.compile(r'Edit attributes dialog opened from document view')
    
    # Process log files - look in splits subdirectories
    log_files = []
    
    # Find all log files in all subdirectories of logs_dir
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith('.log'):
                log_files.append(os.path.join(root, file))
    
    log_files = sorted(log_files)
    total_files = len(log_files)
    
    if verbose:
        print(f"Found {total_files} log files to process")
    
    for i, log_file in enumerate(log_files):
        if verbose and i % 100 == 0:
            print(f"Processing file {i+1}/{total_files}: {os.path.basename(log_file)}")
            
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Check for document attributes changed
                properties_match = properties_change_pattern.search(line)
                if properties_match:
                    # Extract number of documents and user
                    doc_count = int(properties_match.group(1))
                    user = extract_user_from_log(line)
                    
                    # Update properties changes data
                    properties_changes_data["total_changes"] += 1
                    properties_changes_data["unique_users"].add(user)
                    properties_changes_data["documents_affected"].append(doc_count)
                    properties_changes_data["user_changes"][user] += 1
                
                # Check for edit attributes dialog opened
                dialog_match = edit_dialog_pattern.search(line)
                if dialog_match:
                    # Extract user
                    user = extract_user_from_log(line)
                    
                    # Update edit dialog data
                    edit_dialog_data["total_openings"] += 1
                    edit_dialog_data["unique_users"].add(user)
                    edit_dialog_data["user_openings"][user] += 1
    
    # Create summary dataframe
    summary_records = []
    
    # Document attributes changes summary
    if properties_changes_data["total_changes"] > 0:
        doc_counts = properties_changes_data["documents_affected"]
        total_documents = sum(doc_counts)
        avg_documents = total_documents / len(doc_counts)
        min_documents = min(doc_counts)
        max_documents = max(doc_counts)
        
        summary_records.append({
            "action_type": "Document Attributes Changed",
            "total_actions": properties_changes_data["total_changes"],
            "unique_users": len(properties_changes_data["unique_users"]),
            "total_documents_affected": total_documents,
            "avg_documents_per_action": round(avg_documents, 2),
            "min_documents_per_action": min_documents,
            "max_documents_per_action": max_documents
        })
    
    # Edit dialog openings summary
    if edit_dialog_data["total_openings"] > 0:
        summary_records.append({
            "action_type": "Edit Dialog Opened",
            "total_actions": edit_dialog_data["total_openings"],
            "unique_users": len(edit_dialog_data["unique_users"]),
            "total_documents_affected": None,  # Not applicable for dialog openings
            "avg_documents_per_action": None,
            "min_documents_per_action": None,
            "max_documents_per_action": None
        })
    
    # Create dataframe for summary data
    if summary_records:
        df_summary = pl.DataFrame(summary_records)
        
        # Save to CSV
        summary_output_file = output_dir / "document_properties_summary.csv"
        df_summary.write_csv(summary_output_file)
        
        if verbose:
            print(f"Saved document properties summary to {summary_output_file}")
            if properties_changes_data["total_changes"] > 0:
                print(f"Found {properties_changes_data['total_changes']} document property changes by {len(properties_changes_data['unique_users'])} users")
                print(f"Total documents affected: {sum(properties_changes_data['documents_affected'])}")
            if edit_dialog_data["total_openings"] > 0:
                print(f"Found {edit_dialog_data['total_openings']} edit dialog openings by {len(edit_dialog_data['unique_users'])} users")
    else:
        if verbose:
            print("No document properties data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_summary = pl.DataFrame({
            "action_type": [],
            "total_actions": [],
            "unique_users": [],
            "total_documents_affected": [],
            "avg_documents_per_action": [],
            "min_documents_per_action": [],
            "max_documents_per_action": []
        })
        
        # Save empty dataframe
        summary_output_file = output_dir / "document_properties_summary.csv"
        df_summary.write_csv(summary_output_file)
        
        if verbose:
            print(f"Saved empty document properties summary template to {summary_output_file}")
    
    # Create detailed dataframe for document counts distribution
    if properties_changes_data["documents_affected"]:
        # Count frequency of each document count
        doc_count_freq = defaultdict(int)
        for count in properties_changes_data["documents_affected"]:
            doc_count_freq[count] += 1
        
        # Create records for document count distribution
        distribution_records = []
        for doc_count, frequency in sorted(doc_count_freq.items()):
            distribution_records.append({
                "documents_per_change": doc_count,
                "frequency": frequency,
                "percentage": round((frequency / len(properties_changes_data["documents_affected"])) * 100, 1)
            })
        
        # Create dataframe for distribution data
        df_distribution = pl.DataFrame(distribution_records)
        
        # Save to CSV
        distribution_output_file = output_dir / "document_properties_distribution.csv"
        df_distribution.write_csv(distribution_output_file)
        
        if verbose:
            print(f"Saved document properties distribution to {distribution_output_file}")
    else:
        # Create empty distribution dataframe
        df_distribution = pl.DataFrame({
            "documents_per_change": [],
            "frequency": [],
            "percentage": []
        })
        
        distribution_output_file = output_dir / "document_properties_distribution.csv"
        df_distribution.write_csv(distribution_output_file)
        
        if verbose:
            print(f"Saved empty document properties distribution template to {distribution_output_file}")
    
    # Create user-based distribution data for the dashboard
    user_distribution_records = []
    
    # Add document changes per user
    for user, count in properties_changes_data["user_changes"].items():
        user_distribution_records.append({
            "employee_code": user,
            "event_type": "Document attributes changed",
            "count": count
        })
    
    # Add edit dialog openings per user
    for user, count in edit_dialog_data["user_openings"].items():
        user_distribution_records.append({
            "employee_code": user,
            "event_type": "Edit attributes dialog opened",
            "count": count
        })
    
    if user_distribution_records:
        df_user_distribution = pl.DataFrame(user_distribution_records)
        
        # Save user distribution data
        user_distribution_output_file = output_dir / "document_properties_user_distribution.csv"
        df_user_distribution.write_csv(user_distribution_output_file)
        
        if verbose:
            print(f"Saved document properties user distribution to {user_distribution_output_file}")
    else:
        # Create empty user distribution dataframe
        df_user_distribution = pl.DataFrame({
            "employee_code": [],
            "event_type": [],
            "count": []
        })
        
        user_distribution_output_file = output_dir / "document_properties_user_distribution.csv"
        df_user_distribution.write_csv(user_distribution_output_file)
        
        if verbose:
            print(f"Saved empty document properties user distribution template to {user_distribution_output_file}")
    
    return df_summary, df_distribution

if __name__ == "__main__":
    # This block allows the script to be run directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze logs for document properties changes')
    parser.add_argument('--input', type=str, default='logs/splits', help='Directory containing log files')
    parser.add_argument('--output', type=str, default='out', help='Directory to write output files')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    analyze_document_properties(args.input, args.output, args.verbose)