# tests/test_folder_selection.py
import pytest
from pathlib import Path
from src.analyze_folder_selection import extract_folder_events_from_file, FOLDER_PATTERN

def test_folder_pattern_regex():
    """Test the regex pattern for extracting folder selection information."""
    
    # Test with example log line from user
    test_line = "2025-09-10 07:43:31.0799 11.1.2.0 DEBUG 31 [User: IC150729] [UserAgent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0] FolderSelected: 05. Verlof"
    match = FOLDER_PATTERN.match(test_line)
    
    assert match is not None
    assert match.group("timestamp") == "2025-09-10 07:43:31.0799"
    assert match.group("user") == "IC150729"
    assert match.group("folder_name") == "05. Verlof"

def test_folder_pattern_with_different_folder_names():
    """Test the regex pattern with different folder names."""
    
    test_cases = [
        ("2025-01-09 15:30:45.123 [User: IC118451] FolderSelected: 02. Verlof", "02. Verlof"),
        ("2025-01-09 15:30:45.123 [User: RO308749] FolderSelected: 03. Personeels dossier", "03. Personeels dossier"),
        ("2025-01-09 15:30:45.123 [User: RT932273] FolderSelected: 01. Ziekteverzuim", "01. Ziekteverzuim"),
        ("2025-01-09 15:30:45.123 [User: RT932273] FolderSelected: Loopbaan en Pers", "Loopbaan en Pers"),
    ]
    
    for test_line, expected_folder in test_cases:
        match = FOLDER_PATTERN.match(test_line)
        assert match is not None
        assert match.group("folder_name") == expected_folder

def test_folder_pattern_no_match():
    """Test that the regex doesn't match lines without FolderSelected."""
    
    test_lines = [
        "2025-01-09 15:30:45.123 [User: IC118451] Some other action.",
        "2025-01-09 15:30:45.123 Regular log line without user info",
        "Not a log line at all"
    ]
    
    for test_line in test_lines:
        match = FOLDER_PATTERN.match(test_line)
        assert match is None

def test_extract_folder_events_from_empty_file(tmp_path):
    """Test extracting folder events from an empty file."""
    
    # Create a temporary empty log file
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    
    events = extract_folder_events_from_file(log_file)
    assert events == []

def test_extract_folder_events_from_file_with_data(tmp_path):
    """Test extracting folder events from a file with test data."""
    
    # Create a temporary log file with test data
    log_file = tmp_path / "test.log"
    test_content = """2025-09-10 07:43:31.0799 11.1.2.0 DEBUG 31 [User: IC150729] [UserAgent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0] FolderSelected: 05. Verlof
2025-01-09 16:45:30.456 [User: RO308749] Some other action
2025-01-09 17:20:15.789 [User: RT932273] FolderSelected: 02. Ziekteverzuim
Invalid log line
2025-01-09 18:10:00.000 [User: IC118451] FolderSelected: 03. Personeels dossier"""
    
    log_file.write_text(test_content)
    
    events = extract_folder_events_from_file(log_file)
    
    # Should extract 3 folder selection events
    assert len(events) == 3
    
    # Check first event
    assert events[0]["user_id"] == "IC150729"
    assert events[0]["folder_name"] == "05. Verlof"
    assert events[0]["date"] == "2025-09-10"
    assert events[0]["hour"] == 7
    
    # Check second event
    assert events[1]["user_id"] == "RT932273"
    assert events[1]["folder_name"] == "02. Ziekteverzuim"
    
    # Check third event
    assert events[2]["user_id"] == "IC118451"
    assert events[2]["folder_name"] == "03. Personeels dossier"

if __name__ == "__main__":
    pytest.main([__file__])
