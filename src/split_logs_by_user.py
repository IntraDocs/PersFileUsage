"""
Log splitter for personnel file portal logs.
Splits daily logs by user into separate files.
"""
import re
import logging
from pathlib import Path
from typing import Optional


# Regex patterns for parsing log lines
DATE_PATTERN = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}\.\d+')
USER_PATTERN = re.compile(r'\[User:\s*(?P<user>[A-Z0-9]+)\]')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def split_one_file(in_path: Path) -> int:
    """
    Split a single log file by date and user.
    
    Args:
        in_path: Path to the input log file
        
    Returns:
        Number of lines processed
    """
    if not in_path.exists():
        logger.warning(f"File does not exist: {in_path}")
        return 0
    
    lines_processed = 0
    current_date = None
    
    logger.info(f"Processing file: {in_path}")
    
    try:
        with open(in_path, 'r', encoding='utf-8', errors='ignore') as infile:
            for line in infile:
                line = line.rstrip('\n\r')
                
                # Extract date from line
                date_match = DATE_PATTERN.match(line)
                if date_match:
                    current_date = date_match.group('date')
                
                # Extract user from line
                user_match = USER_PATTERN.search(line)
                if user_match and current_date:
                    user = user_match.group('user')
                    
                    # Create output directory for this date
                    output_dir = Path('logs/splits') / current_date
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Append line to user's file for this date
                    output_file = output_dir / f"{user}.log"
                    with open(output_file, 'a', encoding='utf-8') as outfile:
                        outfile.write(line + '\n')
                
                lines_processed += 1
                
                # Log progress every 10000 lines
                if lines_processed % 10000 == 0:
                    logger.info(f"Processed {lines_processed} lines...")
    
    except Exception as e:
        logger.error(f"Error processing file {in_path}: {e}")
        raise
    
    logger.info(f"Completed processing {in_path}: {lines_processed} lines")
    return lines_processed


def main():
    """Main function to process all log files in logs/raw directory."""
    raw_logs_dir = Path('logs/raw')
    
    if not raw_logs_dir.exists():
        logger.error(f"Raw logs directory does not exist: {raw_logs_dir}")
        return
    
    log_files = list(raw_logs_dir.glob('*.log'))
    
    if not log_files:
        logger.warning(f"No .log files found in {raw_logs_dir}")
        return
    
    total_lines = 0
    
    logger.info(f"Found {len(log_files)} log files to process")
    
    for log_file in log_files:
        lines = split_one_file(log_file)
        total_lines += lines
    
    logger.info(f"Processing complete. Total lines processed: {total_lines}")


if __name__ == "__main__":
    main()
