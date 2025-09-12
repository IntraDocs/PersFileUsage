"""
Panel Selection Analysis for Personnel File Portal Logs.
Analyzes panel activation patterns, concurrent employee panels, and switching behavior.

Business Rules:
- Maximum 5 concurrent employee panels allowed per user
- Base panels (employees, documents, import, reports, management) don't count toward limit
"""
import re
import csv
import logging
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict, Counter
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base panels that are standard across all users
BASE_PANELS = {'employees', 'documents', 'import', 'reports', 'management'}

# Business rules
MAX_CONCURRENT_EMPLOYEE_PANELS = 5

# Regex patterns for panel operations
PANEL_ACTIVATED_PATTERN = re.compile(r'Switch Panel Activated: (?P<panel>\w+)')
PANEL_ADDED_PATTERN = re.compile(r'Switch Panel Added: (?P<panel>\w+)')
PANEL_REMOVED_PATTERN = re.compile(r'Switch Panel Removed: (?P<panel>\w+)')

# Standard patterns from split_logs_by_user.py
DATE_PATTERN = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2}\.\d+)')
USER_PATTERN = re.compile(r'\[User:\s*(?P<user>[A-Z0-9]+)\]')


class PanelTracker:
    """Tracks panel state for a single user."""
    
    def __init__(self, user: str):
        self.user = user
        self.base_panel_activations = Counter()
        self.employee_panels_opened = set()
        self.current_employee_panels = set()
        self.max_concurrent_employee_panels = 0
        self.employee_panel_switches = 0
        self.last_activated_employee_panel = None
        self.activation_history = []  # Track order of panel activations
        
    def process_panel_activated(self, panel: str):
        """Process a panel activation event."""
        if panel in BASE_PANELS:
            self.base_panel_activations[panel] += 1
        else:
            # This is an employee panel
            # Check if this is a switch to a previously activated panel
            if (self.last_activated_employee_panel and 
                self.last_activated_employee_panel != panel and
                panel in self.current_employee_panels):
                
                # This is a switch if the panel was previously activated (is in history)
                # and it's not the immediately previous activation
                if panel in self.activation_history and self.activation_history:
                    self.employee_panel_switches += 1
            
            # Update activation tracking
            self.last_activated_employee_panel = panel
            if panel not in self.activation_history:
                self.activation_history.append(panel)
    
    def process_panel_added(self, panel: str):
        """Process a panel added event."""
        if panel not in BASE_PANELS:
            # This is an employee panel
            self.employee_panels_opened.add(panel)
            self.current_employee_panels.add(panel)
            
            # Enforce business rule: maximum 5 concurrent employee panels
            if len(self.current_employee_panels) > MAX_CONCURRENT_EMPLOYEE_PANELS:
                # Remove the oldest panel to stay within limit
                # Note: In real logs, we should see corresponding "Switch Panel Removed" events
                # If not, this indicates potential log data issues or forced panel closure
                oldest_panels = list(self.current_employee_panels)
                panels_to_remove = oldest_panels[:len(self.current_employee_panels) - MAX_CONCURRENT_EMPLOYEE_PANELS]
                for panel_to_remove in panels_to_remove:
                    self.current_employee_panels.discard(panel_to_remove)
            
            self.max_concurrent_employee_panels = max(
                self.max_concurrent_employee_panels, 
                len(self.current_employee_panels)
            )
    
    def process_panel_removed(self, panel: str):
        """Process a panel removed event."""
        if panel not in BASE_PANELS:
            # This is an employee panel
            self.current_employee_panels.discard(panel)
            if self.last_activated_employee_panel == panel:
                self.last_activated_employee_panel = None
            # Remove from activation history when panel is closed
            if panel in self.activation_history:
                self.activation_history.remove(panel)
    
    def get_summary(self) -> Dict:
        """Get summary statistics for this user."""
        return {
            'user': self.user,
            'base_panel_activations': dict(self.base_panel_activations),
            'total_base_activations': sum(self.base_panel_activations.values()),
            'unique_employee_panels_opened': len(self.employee_panels_opened),
            'max_concurrent_employee_panels': self.max_concurrent_employee_panels,
            'employee_panel_switches': self.employee_panel_switches,
            'has_switched_employee_panels': self.employee_panel_switches > 0
        }


def analyze_panel_usage(log_files: List[Path]) -> Dict:
    """
    Analyze panel usage across all log files.
    
    Args:
        log_files: List of log file paths to analyze
        
    Returns:
        Dictionary with analysis results
    """
    user_trackers = {}
    total_lines_processed = 0
    
    logger.info(f"Starting panel analysis on {len(log_files)} files")
    
    for log_file in log_files:
        logger.info(f"Processing {log_file}")
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    total_lines_processed += 1
                    
                    # Extract user from line
                    user_match = USER_PATTERN.search(line)
                    if not user_match:
                        continue
                    
                    user = user_match.group('user')
                    if user == 'Unknown':
                        continue
                    
                    # Initialize tracker for new users
                    if user not in user_trackers:
                        user_trackers[user] = PanelTracker(user)
                    
                    tracker = user_trackers[user]
                    
                    # Check for panel operations
                    if 'Switch Panel Activated:' in line:
                        match = PANEL_ACTIVATED_PATTERN.search(line)
                        if match:
                            tracker.process_panel_activated(match.group('panel'))
                    
                    elif 'Switch Panel Added:' in line:
                        match = PANEL_ADDED_PATTERN.search(line)
                        if match:
                            tracker.process_panel_added(match.group('panel'))
                    
                    elif 'Switch Panel Removed:' in line:
                        match = PANEL_REMOVED_PATTERN.search(line)
                        if match:
                            tracker.process_panel_removed(match.group('panel'))
                    
                    if total_lines_processed % 50000 == 0:
                        logger.info(f"Processed {total_lines_processed} lines...")
        
        except Exception as e:
            logger.error(f"Error processing {log_file}: {e}")
            continue
    
    logger.info(f"Completed processing {total_lines_processed} lines")
    
    # Generate user summaries
    user_summaries = []
    for tracker in user_trackers.values():
        user_summaries.append(tracker.get_summary())
    
    # Generate aggregate statistics
    aggregate_stats = generate_aggregate_stats(user_summaries)
    
    return {
        'total_lines_processed': total_lines_processed,
        'total_users_analyzed': len(user_summaries),
        'user_summaries': user_summaries,
        'aggregate_stats': aggregate_stats
    }


def generate_aggregate_stats(user_summaries: List[Dict]) -> Dict:
    """Generate aggregate statistics from user summaries."""
    
    # Base panel usage aggregation
    base_panel_totals = Counter()
    for summary in user_summaries:
        for panel, count in summary['base_panel_activations'].items():
            base_panel_totals[panel] += count
    
    # Concurrent employee panels distribution
    concurrent_distribution = Counter()
    for summary in user_summaries:
        concurrent_distribution[summary['max_concurrent_employee_panels']] += 1
    
    # Employee panel switching statistics
    users_with_switches = sum(1 for s in user_summaries if s['has_switched_employee_panels'])
    switch_percentage = (users_with_switches / len(user_summaries) * 100) if user_summaries else 0
    
    # Top users by various metrics
    top_base_users = sorted(user_summaries, key=lambda x: x['total_base_activations'], reverse=True)[:10]
    top_employee_panel_users = sorted(user_summaries, key=lambda x: x['unique_employee_panels_opened'], reverse=True)[:10]
    top_concurrent_users = sorted(user_summaries, key=lambda x: x['max_concurrent_employee_panels'], reverse=True)[:10]
    top_switchers = sorted(user_summaries, key=lambda x: x['employee_panel_switches'], reverse=True)[:10]
    
    return {
        'base_panel_usage': {
            'total_activations_by_panel': dict(base_panel_totals),
            'most_popular_base_panel': base_panel_totals.most_common(1)[0] if base_panel_totals else None,
            'top_users_by_base_activations': [
                {'user': u['user'], 'total_activations': u['total_base_activations']} 
                for u in top_base_users
            ]
        },
        'employee_panel_usage': {
            'concurrent_panel_distribution': dict(concurrent_distribution),
            'users_by_max_concurrent': {
                '0_panels': concurrent_distribution[0],
                '1_panel': concurrent_distribution[1],
                '2_panels': concurrent_distribution[2],
                '3_panels': concurrent_distribution[3],
                '4_or_more_panels': sum(concurrent_distribution[i] for i in range(4, max(concurrent_distribution.keys()) + 1)) if concurrent_distribution else 0
            },
            'top_users_by_unique_panels': [
                {'user': u['user'], 'unique_panels': u['unique_employee_panels_opened']} 
                for u in top_employee_panel_users
            ],
            'top_users_by_concurrent': [
                {'user': u['user'], 'max_concurrent': u['max_concurrent_employee_panels']} 
                for u in top_concurrent_users
            ]
        },
        'switching_behavior': {
            'users_who_switched': users_with_switches,
            'total_users': len(user_summaries),
            'percentage_switched': round(switch_percentage, 2),
            'top_switchers': [
                {'user': u['user'], 'switches': u['employee_panel_switches']} 
                for u in top_switchers
            ]
        }
    }


def save_analysis_results(results: Dict, output_dir: Path):
    """Save analysis results to CSV files in output directory."""
    try:
        output_dir.mkdir(exist_ok=True)
        
        # 1. Save user summaries (main detailed data)
        user_summaries_file = output_dir / 'panel_selection_user_summaries.csv'
        save_user_summaries_csv(results['user_summaries'], user_summaries_file)
        
        # 2. Save base panel usage summary
        base_panel_file = output_dir / 'panel_selection_base_panels.csv'
        save_base_panel_usage_csv(results['aggregate_stats']['base_panel_usage'], base_panel_file)
        
        # 3. Save concurrent panel distribution
        concurrent_file = output_dir / 'panel_selection_concurrent_distribution.csv'
        save_concurrent_distribution_csv(results['aggregate_stats']['employee_panel_usage'], concurrent_file)
        
        # 4. Save top performers
        top_performers_file = output_dir / 'panel_selection_top_performers.csv'
        save_top_performers_csv(results['aggregate_stats'], top_performers_file)
        
        # 5. Save aggregate statistics summary
        aggregate_file = output_dir / 'panel_selection_summary.csv'
        save_aggregate_summary_csv(results, aggregate_file)
        
        logger.info(f"Results saved to CSV files in {output_dir}")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise


def save_user_summaries_csv(user_summaries: List[Dict], output_file: Path):
    """Save detailed user summaries to CSV."""
    if not user_summaries:
        return
    
    fieldnames = [
        'user',
        'total_base_activations',
        'employees_activations',
        'documents_activations', 
        'import_activations',
        'reports_activations',
        'management_activations',
        'unique_employee_panels_opened',
        'max_concurrent_employee_panels',
        'employee_panel_switches',
        'has_switched_employee_panels'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for summary in user_summaries:
            row = {
                'user': summary['user'],
                'total_base_activations': summary['total_base_activations'],
                'unique_employee_panels_opened': summary['unique_employee_panels_opened'],
                'max_concurrent_employee_panels': summary['max_concurrent_employee_panels'],
                'employee_panel_switches': summary['employee_panel_switches'],
                'has_switched_employee_panels': summary['has_switched_employee_panels']
            }
            
            # Add individual base panel counts
            base_activations = summary['base_panel_activations']
            for panel in ['employees', 'documents', 'import', 'reports', 'management']:
                row[f'{panel}_activations'] = base_activations.get(panel, 0)
            
            writer.writerow(row)


def save_base_panel_usage_csv(base_usage: Dict, output_file: Path):
    """Save base panel usage statistics to CSV."""
    rows = [['panel', 'total_activations']]
    
    for panel, count in sorted(base_usage['total_activations_by_panel'].items(), 
                              key=lambda x: x[1], reverse=True):
        rows.append([panel, count])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def save_concurrent_distribution_csv(emp_usage: Dict, output_file: Path):
    """Save concurrent panel distribution to CSV."""
    rows = [['concurrent_panels', 'user_count', 'percentage']]
    
    total_users = sum(emp_usage['users_by_max_concurrent'].values())
    
    for key, count in sorted(emp_usage['users_by_max_concurrent'].items()):
        percentage = (count / total_users * 100) if total_users > 0 else 0
        rows.append([key, count, f"{percentage:.2f}%"])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def save_top_performers_csv(stats: Dict, output_file: Path):
    """Save top performing users across different metrics to CSV."""
    rows = [['metric', 'rank', 'user', 'value']]
    
    # Top base panel users
    for i, user_data in enumerate(stats['base_panel_usage']['top_users_by_base_activations'][:10], 1):
        rows.append(['base_activations', i, user_data['user'], user_data['total_activations']])
    
    # Top employee panel users
    for i, user_data in enumerate(stats['employee_panel_usage']['top_users_by_unique_panels'][:10], 1):
        rows.append(['unique_employee_panels', i, user_data['user'], user_data['unique_panels']])
    
    # Top concurrent users
    for i, user_data in enumerate(stats['employee_panel_usage']['top_users_by_concurrent'][:10], 1):
        rows.append(['max_concurrent_panels', i, user_data['user'], user_data['max_concurrent']])
    
    # Top switchers
    for i, user_data in enumerate(stats['switching_behavior']['top_switchers'][:10], 1):
        rows.append(['panel_switches', i, user_data['user'], user_data['switches']])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def save_aggregate_summary_csv(results: Dict, output_file: Path):
    """Save aggregate summary statistics to CSV."""
    rows = [['metric', 'value', 'category']]
    
    # Basic metrics
    rows.append(['total_lines_processed', results['total_lines_processed'], 'processing'])
    rows.append(['total_users_analyzed', results['total_users_analyzed'], 'processing'])
    
    # Base panel totals
    base_totals = results['aggregate_stats']['base_panel_usage']['total_activations_by_panel']
    for panel, count in base_totals.items():
        rows.append([f'{panel}_total_activations', count, 'base_panels'])
    
    # Employee panel statistics
    emp_stats = results['aggregate_stats']['employee_panel_usage']
    users_with_panels = sum(count for key, count in emp_stats['users_by_max_concurrent'].items() if key != '0_panels')
    rows.append(['total_users_with_employee_panels', users_with_panels, 'employee_panels'])
    
    # Switching behavior
    switching = results['aggregate_stats']['switching_behavior']
    rows.append(['users_who_switched', switching['users_who_switched'], 'switching'])
    rows.append(['switching_percentage', f"{switching['percentage_switched']:.2f}%", 'switching'])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def print_summary_report(results: Dict):
    """Print a human-readable summary report."""
    stats = results['aggregate_stats']
    
    print("\n" + "="*80)
    print("PANEL SELECTION ANALYSIS REPORT")
    print("="*80)
    
    print(f"\n📊 OVERVIEW")
    print(f"   Total lines processed: {results['total_lines_processed']:,}")
    print(f"   Total users analyzed: {results['total_users_analyzed']:,}")
    
    # Base panel usage
    print(f"\n🏠 BASE PANEL USAGE")
    base_usage = stats['base_panel_usage']
    print(f"   Total activations across all base panels: {sum(base_usage['total_activations_by_panel'].values()):,}")
    
    print(f"\n   Activations by panel:")
    for panel, count in sorted(base_usage['total_activations_by_panel'].items(), key=lambda x: x[1], reverse=True):
        print(f"     {panel:<12}: {count:,}")
    
    if base_usage['most_popular_base_panel']:
        panel, count = base_usage['most_popular_base_panel']
        print(f"\n   Most popular base panel: {panel} ({count:,} activations)")
    
    # Employee panel concurrent usage
    print(f"\n👥 EMPLOYEE PANEL CONCURRENT USAGE")
    emp_usage = stats['employee_panel_usage']
    concurrent_dist = emp_usage['users_by_max_concurrent']
    
    print(f"   Users by maximum concurrent employee panels:")
    print(f"     0 panels: {concurrent_dist['0_panels']:,} users")
    print(f"     1 panel:  {concurrent_dist['1_panel']:,} users")
    print(f"     2 panels: {concurrent_dist['2_panels']:,} users")
    print(f"     3 panels: {concurrent_dist['3_panels']:,} users")
    print(f"     4+ panels: {concurrent_dist['4_or_more_panels']:,} users")
    
    # Switching behavior
    print(f"\n🔄 EMPLOYEE PANEL SWITCHING BEHAVIOR")
    switching = stats['switching_behavior']
    print(f"   Users who switched between employee panels: {switching['users_who_switched']:,}")
    print(f"   Total users with employee panel activity: {switching['total_users']:,}")
    print(f"   Percentage who switched: {switching['percentage_switched']}%")
    
    # Top performers
    print(f"\n🏆 TOP PERFORMERS")
    
    print(f"\n   Top 5 users by base panel activations:")
    for i, user_data in enumerate(base_usage['top_users_by_base_activations'][:5], 1):
        print(f"     {i}. {user_data['user']} ({user_data['total_activations']:,} activations)")
    
    print(f"\n   Top 5 users by unique employee panels opened:")
    for i, user_data in enumerate(emp_usage['top_users_by_unique_panels'][:5], 1):
        print(f"     {i}. {user_data['user']} ({user_data['unique_panels']} unique panels)")
    
    print(f"\n   Top 5 users by max concurrent employee panels:")
    for i, user_data in enumerate(emp_usage['top_users_by_concurrent'][:5], 1):
        print(f"     {i}. {user_data['user']} ({user_data['max_concurrent']} concurrent panels)")
    
    print(f"\n   Top 5 users by employee panel switches:")
    for i, user_data in enumerate(switching['top_switchers'][:5], 1):
        print(f"     {i}. {user_data['user']} ({user_data['switches']} switches)")
    
    print("\n" + "="*80)


def main():
    """Main function to run panel analysis."""
    # Get all split log files
    splits_dir = Path('logs/splits')
    
    if not splits_dir.exists():
        logger.error(f"Splits directory does not exist: {splits_dir}")
        logger.info("Please run the log splitter first: python src/split_logs_by_user.py")
        return
    
    # Find all user log files
    log_files = []
    for date_dir in splits_dir.iterdir():
        if date_dir.is_dir():
            for log_file in date_dir.glob('*.log'):
                log_files.append(log_file)
    
    if not log_files:
        logger.warning(f"No log files found in {splits_dir}")
        return
    
    logger.info(f"Found {len(log_files)} log files to analyze")
    
    # Run analysis
    results = analyze_panel_usage(log_files)
    
    # Save results to CSV files in out directory
    output_dir = Path('out')
    output_dir.mkdir(exist_ok=True)
    save_analysis_results(results, output_dir)
    
    # Print summary
    print_summary_report(results)


if __name__ == "__main__":
    main()