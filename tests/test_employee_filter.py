# tests/test_employee_filter.py
import pytest
from pathlib import Path
from src.analyze_employee_filter import (
    extract_employee_filter_events_from_file, 
    EMPLOYEE_FILTER_PATTERN,
    CRITERIA_PATTERN,
    classify_filter_type,
    get_filter_pattern
)

def test_employee_filter_pattern_regex():
    """Test the regex pattern for extracting employee filter information."""
    
    # Test with example log line from user (must include "Entries:")
    test_line = "2025-09-10 07:44:37.8471 11.1.2.0 DEBUG 28 [User: IC217927] [UserAgent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36] Employee filter executed with criteria: Entries: {http://www.raet.nl/dossier/hr}medewerkerCode='176947', {http://www.raet.nl/dossier/hr}datumUitDienst='>=#2025-09-10# ='"
    match = EMPLOYEE_FILTER_PATTERN.match(test_line)
    
    assert match is not None
    assert match.group("timestamp") == "2025-09-10 07:44:37.8471"
    assert match.group("user") == "IC217927"
    assert "medewerkerCode='176947'" in match.group("criteria")
    assert "datumUitDienst='>=#2025-09-10# ='" in match.group("criteria")

def test_criteria_pattern_extraction():
    """Test extracting individual criteria from the criteria string."""
    
    criteria_text = "Entries: {http://www.raet.nl/dossier/hr}medewerkerCode='176947', {http://www.raet.nl/dossier/hr}datumUitDienst='>=#2025-09-10# ='"
    matches = CRITERIA_PATTERN.findall(criteria_text)
    
    assert len(matches) == 2
    assert matches[0] == ("medewerkerCode", "176947")
    assert matches[1] == ("datumUitDienst", ">=#2025-09-10# =")

def test_classify_filter_type():
    """Test the filter type classification."""
    
    # Test basic filters (single word)
    assert classify_filter_type("176947") == "single_word"
    assert classify_filter_type("ABC123") == "single_word"
    assert classify_filter_type("test") == "single_word"
    
    # Test compare filters with specific patterns
    assert classify_filter_type(">=#2025-09-10# =") == ">=[value]"
    assert classify_filter_type(">=100") == ">=[value]"
    assert classify_filter_type("<=50") == "<=[value]"
    assert classify_filter_type("<2025-01-01") == "<[value]"
    assert classify_filter_type(">500") == ">[value]"
    assert classify_filter_type("=123") == "=[value]"
    
    # Test combined filters (multiple words)
    assert classify_filter_type("John Doe") == "multiple_words"
    assert classify_filter_type("Test Value Here") == "multiple_words"
    assert classify_filter_type("Multiple word filter") == "multiple_words"
    
    # Test empty filter
    assert classify_filter_type("") == "empty"

def test_get_filter_pattern():
    """Test the filter pattern extraction."""
    
    # Test comparison patterns
    assert get_filter_pattern(">=1000") == ">="
    assert get_filter_pattern(">=kjads") == ">="
    assert get_filter_pattern("<=500") == "<="
    assert get_filter_pattern("<2025") == "<"
    assert get_filter_pattern(">100") == ">"
    assert get_filter_pattern("=123") == "="
    
    # Test word count patterns
    assert get_filter_pattern("single") == "single_word"
    assert get_filter_pattern("two words") == "2_words"
    assert get_filter_pattern("three word phrase") == "3_words"
    assert get_filter_pattern("this is four words") == "4_words"
    
    # Test empty
    assert get_filter_pattern("") == "empty"

def test_extract_employee_filter_events_from_empty_file(tmp_path):
    """Test extracting employee filter events from an empty file."""
    
    # Create a temporary empty log file
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    
    events = extract_employee_filter_events_from_file(log_file)
    assert events == []

def test_extract_employee_filter_events_from_file_with_data(tmp_path):
    """Test extracting employee filter events from a file with test data."""
    
    # Create a temporary log file with test data
    log_file = tmp_path / "test.log"
    test_content = """2025-09-10 07:44:37.8471 11.1.2.0 DEBUG 28 [User: IC217927] [UserAgent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36] Employee filter executed with criteria: Entries: {http://www.raet.nl/dossier/hr}medewerkerCode='176947', {http://www.raet.nl/dossier/hr}datumUitDienst='>=#2025-09-10# ='
2025-09-10 08:30:15.123 [User: RO308749] Some other action
2025-09-10 09:15:22.456 [User: RT932273] Employee filter executed with criteria: Entries: {http://www.raet.nl/dossier/hr}naam='John Doe'
Invalid log line
2025-09-10 10:45:33.789 [User: IC118451] Employee filter executed with criteria: Entries: {http://www.raet.nl/dossier/hr}salaris='>=50000'"""

    log_file.write_text(test_content)

    events = extract_employee_filter_events_from_file(log_file)

    # Should extract 4 filter events (2 from first line, 1 from third line, 1 from last line)
    assert len(events) == 4    # Check first event (medewerkerCode)
    assert events[0]["user_id"] == "IC217927"
    assert events[0]["field_name"] == "medewerkerCode"
    assert events[0]["filter_value"] == "176947"
    assert events[0]["filter_type"] == "single_word"
    assert events[0]["date"] == "2025-09-10"
    assert events[0]["hour"] == 7
    
    # Check second event (datumUitDienst)
    assert events[1]["user_id"] == "IC217927"
    assert events[1]["field_name"] == "datumUitDienst"
    assert events[1]["filter_value"] == ">=#2025-09-10# ="
    assert events[1]["filter_type"] == ">=[value]"
    
    # Check third event (naam with spaces)
    assert events[2]["user_id"] == "RT932273"
    assert events[2]["field_name"] == "naam"
    assert events[2]["filter_value"] == "John Doe"
    assert events[2]["filter_type"] == "multiple_words"
    
    # Check fourth event (salaris comparison)
    assert events[3]["user_id"] == "IC118451"
    assert events[3]["field_name"] == "salaris"
    assert events[3]["filter_value"] == ">=50000"
    assert events[3]["filter_type"] == ">=[value]"

def test_criteria_pattern_with_various_namespaces():
    """Test criteria pattern with different namespace formats."""
    
    test_cases = [
        ("{http://www.raet.nl/dossier/hr}medewerkerCode='176947'", [("medewerkerCode", "176947")]),
        ("{ns1}field1='value1', {ns2}field2='value2'", [("field1", "value1"), ("field2", "value2")]),
        ("{some.long.namespace}testField='test value'", [("testField", "test value")]),
    ]
    
    for criteria_text, expected in test_cases:
        matches = CRITERIA_PATTERN.findall(criteria_text)
        assert matches == expected

if __name__ == "__main__":
    pytest.main([__file__])
