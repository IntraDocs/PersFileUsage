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
    
    # Dictionary to store Excel export data by result type
    excel_export_data = {
        "total_exports": 0,
        "unique_users": set(),
        "by_result_type": defaultdict(lambda: {"total_exports": 0, "unique_users": set(), "file_sizes": []})
    }
    
    # Dictionary to store resultgrid toggle data
    toggle_data = {
        "total_toggles": 0,
        "unique_users": set(),
        "by_element": defaultdict(lambda: {"total_toggles": 0, "unique_users": set()})
    }
    
    # Dictionary to store view page switch data
    view_switch_data = {
        "total_switches": 0,
        "unique_users": set()
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
    
    # Pattern for Excel exports
    excel_export_pattern = re.compile(r'Excel export: ResultType=\'([^\']+)\', ResultsView=\'([^\']+)\', FileName=\'([^\']+)\', FileSize=([^\ ]+)')
    
    # Pattern for resultgrid toggle events
    toggle_pattern = re.compile(r'Element toggled: element:\'\{[^}]+\}([^\']+)\'')
    
    # Pattern for view page switches
    view_switch_pattern = re.compile(r'View Page: Switched to other document\. Position:\d+')
    
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
                
                # Check for Excel exports
                excel_export_match = excel_export_pattern.search(line)
                if excel_export_match:
                    # Extract export details and user
                    result_type = excel_export_match.group(1)  # e.g., 'rs', 'es', etc.
                    result_view = excel_export_match.group(2)
                    file_name = excel_export_match.group(3)
                    
                    # Parse file size (e.g., "91,55 KB")
                    file_size_str = excel_export_match.group(4)
                    try:
                        # Handle different file size formats (try both comma and dot as decimal separator)
                        file_size_value = float(file_size_str.replace(',', '.').split()[0])
                        file_size_unit = file_size_str.split()[-1]
                        
                        # Convert to bytes for consistency
                        if file_size_unit.lower() == 'kb':
                            file_size_bytes = file_size_value * 1024
                        elif file_size_unit.lower() == 'mb':
                            file_size_bytes = file_size_value * 1024 * 1024
                        else:
                            file_size_bytes = file_size_value  # Assume bytes
                    except (ValueError, IndexError):
                        file_size_bytes = 0  # Default if parsing fails
                    
                    user = extract_user_from_log(line)
                    
                    # Update overall Excel export data
                    excel_export_data["total_exports"] += 1
                    excel_export_data["unique_users"].add(user)
                    
                    # Update data for specific result type
                    excel_export_data["by_result_type"][result_type]["total_exports"] += 1
                    excel_export_data["by_result_type"][result_type]["unique_users"].add(user)
                    excel_export_data["by_result_type"][result_type]["file_sizes"].append(file_size_bytes)
                
                # Check for resultgrid toggle events
                toggle_match = toggle_pattern.search(line)
                if toggle_match:
                    # Extract element name (without namespace) and user
                    element_name = toggle_match.group(1)
                    user = extract_user_from_log(line)
                    
                    # Update overall toggle data
                    toggle_data["total_toggles"] += 1
                    toggle_data["unique_users"].add(user)
                    
                    # Update data for specific element
                    toggle_data["by_element"][element_name]["total_toggles"] += 1
                    toggle_data["by_element"][element_name]["unique_users"].add(user)
                
                # Check for view page switches
                view_switch_match = view_switch_pattern.search(line)
                if view_switch_match:
                    # Extract user
                    user = extract_user_from_log(line)
                    
                    # Update view switch data
                    view_switch_data["total_switches"] += 1
                    view_switch_data["unique_users"].add(user)
    
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
    
    # Process Excel export data
    excel_export_records = []
    
    # Overall Excel export statistics
    if excel_export_data["total_exports"] > 0:
        excel_export_records.append({
            "result_type": "overall",
            "result_type_description": "All Types",
            "total_exports": excel_export_data["total_exports"],
            "unique_users": len(excel_export_data["unique_users"])
        })
        
        # Result type specific statistics
        result_type_descriptions = {
            "rs": "ResultSet",
            "es": "EntitySearchResultSet",
            "vd": "VersionDetails",
            "dh": "DocumentHistory",
            "db": "DropboxResultSet",
            "id": "IndexDocuments"
        }
        
        for result_type, data in excel_export_data["by_result_type"].items():
            # Calculate average file size if there are file sizes recorded
            avg_size = 0
            if data["file_sizes"]:
                avg_size = sum(data["file_sizes"]) / len(data["file_sizes"])
            
            # Get description for result type
            result_type_desc = result_type_descriptions.get(result_type, result_type)
            
            excel_export_records.append({
                "result_type": result_type,
                "result_type_description": result_type_desc,
                "total_exports": data["total_exports"],
                "unique_users": len(data["unique_users"]),
                "avg_file_size_bytes": avg_size
            })
        
        # Create dataframe for Excel export data
        df_excel_exports = pl.DataFrame(excel_export_records)
        
        # Save to CSV
        excel_output_file = output_dir / "excel_exports.csv"
        df_excel_exports.write_csv(excel_output_file)
        
        if verbose:
            print(f"Saved Excel export data to {excel_output_file}")
            print(f"Found {excel_export_data['total_exports']} Excel exports by {len(excel_export_data['unique_users'])} users")
    else:
        if verbose:
            print("No Excel export data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_excel_exports = pl.DataFrame({
            "result_type": [],
            "result_type_description": [],
            "total_exports": [],
            "unique_users": [],
            "avg_file_size_bytes": []
        })
        
        # Save empty dataframe
        excel_output_file = output_dir / "excel_exports.csv"
        df_excel_exports.write_csv(excel_output_file)
        
        if verbose:
            print(f"Saved empty Excel export data template to {excel_output_file}")
    
    # Process resultgrid toggle data
    toggle_records = []
    
    # Overall toggle statistics
    if toggle_data["total_toggles"] > 0:
        toggle_records.append({
            "element": "overall",
            "element_description": "All Elements",
            "total_toggles": toggle_data["total_toggles"],
            "unique_users": len(toggle_data["unique_users"])
        })
        
        # Element specific statistics
        for element, data in toggle_data["by_element"].items():
            toggle_records.append({
                "element": element,
                "element_description": element,  # For now, same as element name
                "total_toggles": data["total_toggles"],
                "unique_users": len(data["unique_users"])
            })
        
        # Create dataframe for toggle data
        df_toggles = pl.DataFrame(toggle_records)
        
        # Save to CSV
        toggle_output_file = output_dir / "resultgrid_toggles.csv"
        df_toggles.write_csv(toggle_output_file)
        
        if verbose:
            print(f"Saved resultgrid toggle data to {toggle_output_file}")
            print(f"Found {toggle_data['total_toggles']} toggle events by {len(toggle_data['unique_users'])} users")
    else:
        if verbose:
            print("No resultgrid toggle data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_toggles = pl.DataFrame({
            "element": [],
            "element_description": [],
            "total_toggles": [],
            "unique_users": []
        })
        
        # Save empty dataframe
        toggle_output_file = output_dir / "resultgrid_toggles.csv"
        df_toggles.write_csv(toggle_output_file)
        
        if verbose:
            print(f"Saved empty resultgrid toggle data template to {toggle_output_file}")
    
    # Process view page switch data
    view_switch_records = []
    
    if view_switch_data["total_switches"] > 0:
        view_switch_records.append({
            "function_name": "View Page: Switch to other document",
            "total_switches": view_switch_data["total_switches"],
            "unique_users": len(view_switch_data["unique_users"])
        })
        
        # Create dataframe for view switch data
        df_view_switches = pl.DataFrame(view_switch_records)
        
        # Save to CSV
        view_switch_output_file = output_dir / "view_page_switches.csv"
        df_view_switches.write_csv(view_switch_output_file)
        
        if verbose:
            print(f"Saved view page switch data to {view_switch_output_file}")
            print(f"Found {view_switch_data['total_switches']} view page switches by {len(view_switch_data['unique_users'])} users")
    else:
        if verbose:
            print("No view page switch data found in logs")
        
        # Create an empty dataframe with the expected schema
        df_view_switches = pl.DataFrame({
            "function_name": [],
            "total_switches": [],
            "unique_users": []
        })
        
        # Save empty dataframe
        view_switch_output_file = output_dir / "view_page_switches.csv"
        df_view_switches.write_csv(view_switch_output_file)
        
        if verbose:
            print(f"Saved empty view page switch data template to {view_switch_output_file}")
    
    return df_functions, df_doc_views, df_downloads, df_excel_exports, df_toggles, df_view_switches

if __name__ == "__main__":
    # This block allows the script to be run directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze logs for miscellaneous function calls')
    parser.add_argument('--logs-dir', type=str, default='logs', help='Directory containing log files')
    parser.add_argument('--output-dir', type=str, default='out', help='Directory to write output files')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    analyze_misc_functions(args.logs_dir, args.output_dir, args.verbose)