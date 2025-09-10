"""
Tests for the log splitter functionality.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from src.split_logs_by_user import split_one_file


class TestLogSplitter:
    """Test cases for log splitting functionality."""
    
    def setup_method(self):
        """Setup test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        # Change to test directory so relative paths work
        import os
        os.chdir(self.test_dir)
        
        # Create required directory structure
        (self.test_dir / 'logs' / 'raw').mkdir(parents=True)
        (self.test_dir / 'logs' / 'splits').mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_split_one_file_basic(self):
        """Test basic log splitting functionality."""
        # Create sample log content with two users
        sample_log_content = """2024-01-15 10:30:45.123 INFO [User: USER001] Login successful
2024-01-15 10:31:22.456 INFO [User: USER002] File uploaded
2024-01-15 10:32:10.789 ERROR [User: USER001] Access denied
2024-01-16 09:15:30.111 INFO [User: USER001] Session started
2024-01-16 09:20:45.222 INFO [User: USER002] Document viewed"""
        
        # Write sample log to raw directory
        test_log_path = self.test_dir / 'logs' / 'raw' / 'test.log'
        with open(test_log_path, 'w', encoding='utf-8') as f:
            f.write(sample_log_content)
        
        # Run the splitter
        lines_processed = split_one_file(test_log_path)
        
        # Verify lines processed
        assert lines_processed == 5
        
        # Check that split files were created
        user001_file_2024_01_15 = self.test_dir / 'logs' / 'splits' / '2024-01-15' / 'USER001.log'
        user002_file_2024_01_15 = self.test_dir / 'logs' / 'splits' / '2024-01-15' / 'USER002.log'
        user001_file_2024_01_16 = self.test_dir / 'logs' / 'splits' / '2024-01-16' / 'USER001.log'
        user002_file_2024_01_16 = self.test_dir / 'logs' / 'splits' / '2024-01-16' / 'USER002.log'
        
        assert user001_file_2024_01_15.exists()
        assert user002_file_2024_01_15.exists()
        assert user001_file_2024_01_16.exists()
        assert user002_file_2024_01_16.exists()
        
        # Verify content of USER001 file for 2024-01-15
        with open(user001_file_2024_01_15, 'r', encoding='utf-8') as f:
            user001_content = f.read().strip()
        
        expected_lines = [
            "2024-01-15 10:30:45.123 INFO [User: USER001] Login successful",
            "2024-01-15 10:32:10.789 ERROR [User: USER001] Access denied"
        ]
        
        for expected_line in expected_lines:
            assert expected_line in user001_content
    
    def test_split_one_file_nonexistent(self):
        """Test behavior with non-existent file."""
        nonexistent_path = self.test_dir / 'logs' / 'raw' / 'nonexistent.log'
        lines_processed = split_one_file(nonexistent_path)
        assert lines_processed == 0
    
    def test_split_one_file_empty(self):
        """Test behavior with empty file."""
        empty_log_path = self.test_dir / 'logs' / 'raw' / 'empty.log'
        empty_log_path.touch()
        
        lines_processed = split_one_file(empty_log_path)
        assert lines_processed == 0
