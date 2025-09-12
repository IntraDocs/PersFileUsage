# analyze_misc_functions.py
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

def analyze_misc_functions(logs_dir, output_dir, verbose=False):
    """
    Analyze logs for specific function calls and create summary statistics.
    
    Args:
        logs_dir (str or Path): Directory containing log files
        output_dir (str or Path): Directory to write output files
        verbose (bool): Whether to print verbose output
    """
    logs_dir = Path(logs_dir)
    output_dir = Path(output_dir)
    
    if verbose:
        print(f"Analyzing miscellaneous functions in logs...")
    
    # Dictionary to store function call data
    function_data = defaultdict(lambda: {"total_usage": 0, "unique_users": set(), "document_counts": []})
    
    # Dictionary to store document viewing data per mimetype
    document_view_data = defaultdict(lambda: {"total_views": 0, "unique_users": set()})
    
    # Dictionary to store document download data
    document_download_data = {
        "total_downloads": 0,
        "unique_users": set(),
        "sizes": []
    }
    
    # Define patterns to look for
    patterns = {
        "Open Employee Dossier from a document": re.compile(r'Open Employee Dossier called'),
        "Assign document(s) to an employee": re.compile(r'Assign (\d+) documents to employee'),
        "Copy document(s) to employee": re.compile(r'Copy (\d+) documents to employee'),
        # Add more patterns here for other functions you want to track
    }
    
    # Pattern for document viewing
    document_view_pattern = re.compile(r'View Page: Viewing document\. Mimetype:([^\.]+)\.')
    
    # Pattern for document downloads
    document_download_pattern = re.compile(r'Download: Downloaded document: (\d+) bytes')
    
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
        if verbose and i % 10 == 0:
            print(f"Processing file {i+1}/{total_files}: {os.path.basename(log_file)}")
            
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Check each pattern
                for function_name, pattern in patterns.items():
                    match = pattern.search(line)
                    if match:
                        # Extract user
                        user = extract_user_from_log(line)
                        
                        # Update function data
                        function_data[function_name]["total_usage"] += 1
                        function_data[function_name]["unique_users"].add(user)
                        
                        # If this is an Assign or Copy function, capture document count
                        if function_name in ["Assign document(s) to an employee", "Copy document(s) to employee"] and match.groups():
                            doc_count = int(match.group(1))
                            function_data[function_name]["document_counts"].append(doc_count)
                
                # Check for document viewing
                doc_view_match = document_view_pattern.search(line)
                if doc_view_match:
                    # Extract mimetype and user
                    mimetype = doc_view_match.group(1).strip()
                    user = extract_user_from_log(line)
                    
                    # Update document view data
                    document_view_data[mimetype]["total_views"] += 1
                    document_view_data[mimetype]["unique_users"].add(user)
                
                # Check for document downloads
                doc_download_match = document_download_pattern.search(line)
                if doc_download_match:
                    # Extract download size and user
                    size_bytes = int(doc_download_match.group(1))
                    user = extract_user_from_log(line)
                    
                    # Update document download data
                    document_download_data["total_downloads"] += 1
                    document_download_data["unique_users"].add(user)
                    document_download_data["sizes"].append(size_bytes)
    
    # Convert to dataframe
    records = []
    for function_name, data in function_data.items():
        record = {
            "function_name": function_name,
            "total_usage": data["total_usage"],
            "unique_users": len(data["unique_users"])
        }
        
        # Add document count statistics for Assign and Copy functions
        if function_name in ["Assign document(s) to an employee", "Copy document(s) to employee"] and data["document_counts"]:
            doc_counts = data["document_counts"]
            record["total_documents"] = sum(doc_counts)
            record["avg_documents"] = sum(doc_counts) / len(doc_counts)
            record["min_documents"] = min(doc_counts)
            record["max_documents"] = max(doc_counts)
        
        records.append(record)
    
    # Create dataframe for function data
    if records:
        df_functions = pl.DataFrame(records)
        
        # Save to CSV
        output_file = output_dir / "misc_functions.csv"
        df_functions.write_csv(output_file)
        
        if verbose:
            print(f"Saved miscellaneous functions data to {output_file}")
            print(f"Found {len(records)} functions with data")
    else:
        if verbose:
            print("No function call data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_functions = pl.DataFrame({
            "function_name": [],
            "total_usage": [],
            "unique_users": []
        }).with_columns([
            pl.col("total_usage").cast(pl.Int32),
            pl.col("unique_users").cast(pl.Int32)
        ])
        
        # Save empty dataframe
        output_file = output_dir / "misc_functions.csv"
        df_functions.write_csv(output_file)
        
        if verbose:
            print(f"Saved empty miscellaneous functions data template to {output_file}")
    
    # Process document view data
    doc_records = []
    for mimetype, data in document_view_data.items():
        doc_records.append({
            "mimetype": mimetype,
            "total_views": data["total_views"],
            "unique_users": len(data["unique_users"])
        })
    
    # Create dataframe for document view data
    if doc_records:
        df_doc_views = pl.DataFrame(doc_records)
        
        # Save to CSV
        doc_output_file = output_dir / "document_views.csv"
        df_doc_views.write_csv(doc_output_file)
        
        if verbose:
            print(f"Saved document view data to {doc_output_file}")
            print(f"Found {len(doc_records)} mimetypes with data")
    else:
        if verbose:
            print("No document view data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_doc_views = pl.DataFrame({
            "mimetype": [],
            "total_views": [],
            "unique_users": []
        }).with_columns([
            pl.col("total_views").cast(pl.Int32),
            pl.col("unique_users").cast(pl.Int32)
        ])
        
        # Save empty dataframe
        doc_output_file = output_dir / "document_views.csv"
        df_doc_views.write_csv(doc_output_file)
        
        if verbose:
            print(f"Saved empty document view data template to {doc_output_file}")
    
    # Process document download data
    if document_download_data["total_downloads"] > 0:
        # Calculate size statistics
        sizes = document_download_data["sizes"]
        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        median_size = sorted(sizes)[len(sizes) // 2]
        
        # Size distribution categories (in bytes)
        size_categories = {
            "< 10KB": 0,
            "10KB - 100KB": 0,
            "100KB - 1MB": 0,
            "1MB - 10MB": 0,
            "> 10MB": 0
        }
        
        for size in sizes:
            if size < 10 * 1024:  # < 10KB
                size_categories["< 10KB"] += 1
            elif size < 100 * 1024:  # 10KB - 100KB
                size_categories["10KB - 100KB"] += 1
            elif size < 1024 * 1024:  # 100KB - 1MB
                size_categories["100KB - 1MB"] += 1
            elif size < 10 * 1024 * 1024:  # 1MB - 10MB
                size_categories["1MB - 10MB"] += 1
            else:  # > 10MB
                size_categories["> 10MB"] += 1
        
        # Create summary records
        download_records = [
            {"metric": "total_downloads", "value": document_download_data["total_downloads"]},
            {"metric": "unique_users", "value": len(document_download_data["unique_users"])},
            {"metric": "avg_size_bytes", "value": avg_size},
            {"metric": "min_size_bytes", "value": min_size},
            {"metric": "max_size_bytes", "value": max_size},
            {"metric": "median_size_bytes", "value": median_size}
        ]
        
        # Add size distribution records
        for category, count in size_categories.items():
            download_records.append({
                "metric": f"size_category_{category.replace(' ', '_').replace('<', 'lt').replace('>', 'gt')}",
                "value": count
            })
        
        # Create dataframe for download data
        df_downloads = pl.DataFrame(download_records)
        
        # Save to CSV
        download_output_file = output_dir / "document_downloads.csv"
        df_downloads.write_csv(download_output_file)
        
        if verbose:
            print(f"Saved document download data to {download_output_file}")
            print(f"Found {document_download_data['total_downloads']} downloads by {len(document_download_data['unique_users'])} users")
    else:
        if verbose:
            print("No document download data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_downloads = pl.DataFrame({
            "metric": [],
            "value": []
        })
        
        # Save empty dataframe
        download_output_file = output_dir / "document_downloads.csv"
        df_downloads.write_csv(download_output_file)
        
        if verbose:
            print(f"Saved empty document download data template to {download_output_file}")
    
    return df_functions, df_doc_views, df_downloads

if __name__ == "__main__":
    # This block allows the script to be run directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze logs for miscellaneous function calls')
    parser.add_argument('--logs-dir', type=str, default='logs', help='Directory containing log files')
    parser.add_argument('--output-dir', type=str, default='out', help='Directory to write output files')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    analyze_misc_functions(args.logs_dir, args.output_dir, args.verbose)