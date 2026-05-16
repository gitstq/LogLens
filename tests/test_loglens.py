"""
LogLens Tests
=============

Unit tests for LogLens log analysis tool.
"""

import pytest
from datetime import datetime

from loglens.models import LogEntry, LogLevel, LogStats, ErrorPattern
from loglens.parser import LogParser
from loglens.analyzer import LogAnalyzer


class TestLogParser:
    """Tests for LogParser class."""
    
    def test_parse_common_format(self):
        """Test parsing common log format."""
        parser = LogParser()
        
        # Test INFO level
        entry = parser.parse_line("[INFO] Application started", 1)
        assert entry.level == LogLevel.INFO
        assert "Application started" in entry.message
        
        # Test ERROR level
        entry = parser.parse_line("[ERROR] Connection failed", 2)
        assert entry.level == LogLevel.ERROR
        assert "Connection failed" in entry.message
    
    def test_parse_json_format(self):
        """Test parsing JSON log format."""
        parser = LogParser()
        
        json_line = '{"level": "ERROR", "message": "Database error", "timestamp": "2024-01-15T10:30:00"}'
        entry = parser.parse_line(json_line, 1)
        
        assert entry.level == LogLevel.ERROR
        assert entry.message == "Database error"
        assert entry.timestamp is not None
    
    def test_parse_apache_format(self):
        """Test parsing Apache/Nginx log format."""
        parser = LogParser()
        
        apache_line = '192.168.1.1 - - [15/Jan/2024:10:30:00 +0000] "GET /api/users HTTP/1.1" 200 1234'
        entry = parser.parse_line(apache_line, 1)
        
        assert entry.level == LogLevel.INFO  # 200 status
        assert "GET /api/users" in entry.message
        assert entry.source == "192.168.1.1"
    
    def test_parse_apache_error(self):
        """Test parsing Apache error status."""
        parser = LogParser()
        
        apache_line = '192.168.1.1 - - [15/Jan/2024:10:30:00 +0000] "GET /api/error HTTP/1.1" 500 1234'
        entry = parser.parse_line(apache_line, 1)
        
        assert entry.level == LogLevel.ERROR  # 500 status
    
    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        parser = LogParser()
        
        # ISO format
        entry = parser.parse_line("2024-01-15T10:30:00 [INFO] Message", 1)
        assert entry.timestamp is not None
        
        # Simple format
        entry = parser.parse_line("2024-01-15 10:30:00 [INFO] Message", 1)
        assert entry.timestamp is not None
    
    def test_parse_empty_line(self):
        """Test parsing empty line."""
        parser = LogParser()
        
        entry = parser.parse_line("", 1)
        assert entry.message == ""
        assert entry.level == LogLevel.UNKNOWN


class TestLogAnalyzer:
    """Tests for LogAnalyzer class."""
    
    @pytest.fixture
    def sample_entries(self):
        """Create sample log entries for testing."""
        return [
            LogEntry(level=LogLevel.INFO, message="App started", raw_line="", line_number=1),
            LogEntry(level=LogLevel.ERROR, message="Connection failed", raw_line="", line_number=2),
            LogEntry(level=LogLevel.WARNING, message="High memory usage", raw_line="", line_number=3),
            LogEntry(level=LogLevel.ERROR, message="Connection failed", raw_line="", line_number=4),
            LogEntry(level=LogLevel.INFO, message="Request processed", raw_line="", line_number=5),
        ]
    
    def test_analyze_entries(self, sample_entries):
        """Test basic analysis."""
        analyzer = LogAnalyzer(detect_patterns=False)
        stats = analyzer.analyze_entries(sample_entries)
        
        assert stats.total_lines == 5
        assert stats.parsed_entries == 5
        assert stats.by_level.get("INFO") == 2
        assert stats.by_level.get("ERROR") == 2
        assert stats.by_level.get("WARNING") == 1
    
    def test_error_pattern_detection(self, sample_entries):
        """Test error pattern detection."""
        analyzer = LogAnalyzer(detect_patterns=True)
        stats = analyzer.analyze_entries(sample_entries)
        
        assert len(stats.error_patterns) > 0
        # Connection failed appears twice
        connection_pattern = next(
            (p for p in stats.error_patterns if "connection" in p.pattern.lower()),
            None
        )
        assert connection_pattern is not None
        assert connection_pattern.count == 2
    
    def test_filter_by_level(self, sample_entries):
        """Test filtering by level."""
        analyzer = LogAnalyzer()
        
        errors = analyzer.filter_by_level(sample_entries, [LogLevel.ERROR])
        assert len(errors) == 2
        
        warnings = analyzer.filter_by_level(sample_entries, [LogLevel.WARNING])
        assert len(warnings) == 1
    
    def test_filter_by_pattern(self, sample_entries):
        """Test filtering by pattern."""
        analyzer = LogAnalyzer()
        
        results = analyzer.filter_by_pattern(sample_entries, "connection")
        assert len(results) == 2
        
        results = analyzer.filter_by_pattern(sample_entries, "memory")
        assert len(results) == 1
    
    def test_get_errors(self, sample_entries):
        """Test getting all errors."""
        analyzer = LogAnalyzer()
        
        errors = analyzer.get_errors(sample_entries)
        assert len(errors) == 2
    
    def test_get_warnings(self, sample_entries):
        """Test getting all warnings."""
        analyzer = LogAnalyzer()
        
        warnings = analyzer.get_warnings(sample_entries)
        assert len(warnings) == 1
    
    def test_head_tail(self, sample_entries):
        """Test head and tail methods."""
        analyzer = LogAnalyzer()
        
        head = analyzer.head(sample_entries, 2)
        assert len(head) == 2
        assert head[0].line_number == 1
        
        tail = analyzer.tail(sample_entries, 2)
        assert len(tail) == 2
        assert tail[-1].line_number == 5


class TestModels:
    """Tests for data models."""
    
    def test_log_level_from_string(self):
        """Test LogLevel conversion."""
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("info") == LogLevel.INFO
        assert LogLevel.from_string("ERROR") == LogLevel.ERROR
        assert LogLevel.from_string("unknown") == LogLevel.UNKNOWN
    
    def test_log_entry_creation(self):
        """Test LogEntry creation."""
        entry = LogEntry(
            level=LogLevel.INFO,
            message="Test message",
            raw_line="[INFO] Test message",
            line_number=1,
        )
        
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.line_number == 1
    
    def test_log_stats_rates(self):
        """Test LogStats rate calculation."""
        stats = LogStats(
            total_lines=100,
            parsed_entries=100,
            by_level={"ERROR": 10, "WARNING": 20, "INFO": 70}
        )
        
        stats.calculate_rates()
        
        assert stats.error_rate == 10.0
        assert stats.warning_rate == 20.0
    
    def test_error_pattern_add_occurrence(self):
        """Test ErrorPattern occurrence tracking."""
        pattern = ErrorPattern(
            pattern="connection failed",
            count=1,
            level=LogLevel.ERROR,
            first_occurrence=1,
            last_occurrence=1,
            sample_messages=["Connection failed at startup"]
        )
        
        pattern.add_occurrence(5, "Connection failed again")
        
        assert pattern.count == 2
        assert pattern.last_occurrence == 5
        assert len(pattern.sample_messages) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
