"""
Tests for the selected panels analysis functionality.
"""
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from src.analyze_selected_panels import analyze_panel_usage, PanelTracker


class TestSelectedPanelsAnalysis:
    """Test cases for panel selection analysis."""
    
    def setup_method(self):
        """Setup test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        # Change to test directory so relative paths work
        import os
        os.chdir(self.test_dir)
        
        # Create required directory structure
        (self.test_dir / 'logs' / 'splits' / '2024-01-15').mkdir(parents=True)
        (self.test_dir / 'data').mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_panel_tracker_base_panels(self):
        """Test PanelTracker with base panel activations."""
        tracker = PanelTracker("USER001")
        
        # Activate base panels
        tracker.process_panel_activated("employees")
        tracker.process_panel_activated("documents")
        tracker.process_panel_activated("employees")  # Second time
        
        summary = tracker.get_summary()
        
        assert summary['user'] == "USER001"
        assert summary['base_panel_activations']['employees'] == 2
        assert summary['base_panel_activations']['documents'] == 1
        assert summary['total_base_activations'] == 3
        assert summary['max_concurrent_employee_panels'] == 0
        assert summary['employee_panel_switches'] == 0
    
    def test_panel_tracker_employee_panels(self):
        """Test PanelTracker with employee panel operations."""
        tracker = PanelTracker("USER002")
        
        # Add employee panels
        tracker.process_panel_added("EMP001")
        tracker.process_panel_added("EMP002")
        
        # Activate employee panels
        tracker.process_panel_activated("EMP001")
        tracker.process_panel_activated("EMP002")  # Switch
        
        # Remove one panel
        tracker.process_panel_removed("EMP001")
        
        summary = tracker.get_summary()
        
        assert summary['unique_employee_panels_opened'] == 2
        assert summary['max_concurrent_employee_panels'] == 2
        assert summary['employee_panel_switches'] == 1
        assert summary['has_switched_employee_panels'] == True
    
    def test_panel_tracker_complex_scenario(self):
        """Test complex panel switching scenario."""
        tracker = PanelTracker("USER003")
        
        # Add multiple employee panels
        tracker.process_panel_added("ABC123")
        tracker.process_panel_added("DEF456")
        tracker.process_panel_added("GHI789")
        
        # Activate and switch between them
        tracker.process_panel_activated("ABC123")
        tracker.process_panel_activated("DEF456")  # Switch 1
        tracker.process_panel_activated("GHI789")  # Switch 2
        tracker.process_panel_activated("ABC123")  # Switch 3
        
        # Remove one panel and add another
        tracker.process_panel_removed("DEF456")
        tracker.process_panel_added("JKL012")
        tracker.process_panel_activated("JKL012")  # Switch 4
        
        summary = tracker.get_summary()
        
        assert summary['unique_employee_panels_opened'] == 4
        assert summary['max_concurrent_employee_panels'] == 3  # Before DEF456 was removed
        assert summary['employee_panel_switches'] == 4
    
    def test_analyze_panel_usage_integration(self):
        """Test the full analysis pipeline with sample data."""
        # Create sample log content
        sample_log_content = """2024-01-15 10:30:45.123 INFO [User: USER001] Switch Panel Activated: employees
2024-01-15 10:31:22.456 INFO [User: USER002] Switch Panel Added: EMP123
2024-01-15 10:32:10.789 INFO [User: USER002] Switch Panel Activated: EMP123
2024-01-15 10:33:15.111 INFO [User: USER001] Switch Panel Activated: documents
2024-01-15 10:34:20.222 INFO [User: USER002] Switch Panel Added: EMP456
2024-01-15 10:35:25.333 INFO [User: USER002] Switch Panel Activated: EMP456
2024-01-15 10:36:30.444 INFO [User: USER001] Switch Panel Activated: reports
2024-01-15 10:37:35.555 INFO [User: USER002] Switch Panel Removed: EMP123"""
        
        # Write sample log to splits directory
        test_log_path = self.test_dir / 'logs' / 'splits' / '2024-01-15' / 'USER001.log'
        with open(test_log_path, 'w', encoding='utf-8') as f:
            f.write(sample_log_content)
        
        # Run analysis
        results = analyze_panel_usage([test_log_path])
        
        # Verify basic structure
        assert 'total_lines_processed' in results
        assert 'total_users_analyzed' in results
        assert 'user_summaries' in results
        assert 'aggregate_stats' in results
        
        # Verify user data
        assert results['total_users_analyzed'] == 2
        
        # Find USER001 and USER002 in results
        user_summaries = {u['user']: u for u in results['user_summaries']}
        
        assert 'USER001' in user_summaries
        assert 'USER002' in user_summaries
        
        user001 = user_summaries['USER001']
        user002 = user_summaries['USER002']
        
        # Check USER001 (only base panels)
        assert user001['total_base_activations'] == 3  # employees, documents, reports
        assert user001['max_concurrent_employee_panels'] == 0
        assert user001['employee_panel_switches'] == 0
        
        # Check USER002 (employee panels)
        assert user002['unique_employee_panels_opened'] == 2  # EMP123, EMP456
        assert user002['max_concurrent_employee_panels'] == 2  # Both added before removal
        assert user002['employee_panel_switches'] == 1  # Switch from EMP123 to EMP456
        
        # Check aggregate stats structure
        agg_stats = results['aggregate_stats']
        assert 'base_panel_usage' in agg_stats
        assert 'employee_panel_usage' in agg_stats
        assert 'switching_behavior' in agg_stats
        
        # Check switching statistics
        switching = agg_stats['switching_behavior']
        assert switching['users_who_switched'] == 1  # Only USER002
        assert switching['total_users'] == 2
        assert switching['percentage_switched'] == 50.0  # 1 out of 2 users
    
    def test_empty_log_files(self):
        """Test analysis with empty log files."""
        # Create empty log file
        empty_log_path = self.test_dir / 'logs' / 'splits' / '2024-01-15' / 'EMPTY.log'
        empty_log_path.touch()
        
        results = analyze_panel_usage([empty_log_path])
        
        assert results['total_lines_processed'] == 0
        assert results['total_users_analyzed'] == 0
        assert len(results['user_summaries']) == 0
    
    def test_unknown_user_filtering(self):
        """Test that Unknown users are filtered out."""
        sample_log_content = """2024-01-15 10:30:45.123 INFO [User: Unknown] Switch Panel Activated: employees
2024-01-15 10:31:22.456 INFO [User: USER001] Switch Panel Activated: documents"""
        
        test_log_path = self.test_dir / 'logs' / 'splits' / '2024-01-15' / 'TEST.log'
        with open(test_log_path, 'w', encoding='utf-8') as f:
            f.write(sample_log_content)
        
        results = analyze_panel_usage([test_log_path])
        
        # Should only analyze USER001, not Unknown
        assert results['total_users_analyzed'] == 1
        assert results['user_summaries'][0]['user'] == 'USER001'