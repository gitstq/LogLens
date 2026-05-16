"""
LogLens Log Analyzer
====================

Intelligent log analyzer with pattern detection and statistics.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional

from loglens.models import ErrorPattern, LogEntry, LogFormat, LogLevel, LogStats
from loglens.parser import LogParser


class LogAnalyzer:
    """
    Intelligent log analyzer with pattern detection and statistics.
    
    Features:
    - Automatic format detection
    - Error pattern recognition
    - Statistical analysis
    - Time range analysis
    - Source tracking
    """
    
    # Common error patterns to detect
    ERROR_SIGNATURES = [
        (r"exception|error|failed|failure", LogLevel.ERROR),
        (r"warning|warn", LogLevel.WARNING),
        (r"critical|fatal|panic", LogLevel.CRITICAL),
        (r"timeout|timed out", LogLevel.ERROR),
        (r"connection refused|connection reset", LogLevel.ERROR),
        (r"out of memory|oom", LogLevel.CRITICAL),
        (r"stack trace|traceback", LogLevel.ERROR),
        (r"null pointer|NullPointerException", LogLevel.ERROR),
        (r"access denied|permission denied|forbidden", LogLevel.ERROR),
        (r"not found|404", LogLevel.WARNING),
        (r"internal server error|500", LogLevel.ERROR),
    ]
    
    def __init__(
        self,
        parser: Optional[LogParser] = None,
        log_format: LogFormat = LogFormat.AUTO,
        detect_patterns: bool = True,
        pattern_threshold: float = 0.7,
    ):
        """
        Initialize the log analyzer.
        
        Args:
            parser: Optional custom parser instance
            log_format: Log format to use for parsing
            detect_patterns: Whether to detect error patterns
            pattern_threshold: Similarity threshold for pattern grouping
        """
        self.parser = parser or LogParser(log_format)
        self.detect_patterns = detect_patterns
        self.pattern_threshold = pattern_threshold
        self._entries: list[LogEntry] = []
    
    def analyze_file(self, file_path: str) -> LogStats:
        """
        Analyze a log file and return statistics.
        
        Args:
            file_path: Path to the log file
            
        Returns:
            LogStats object with analysis results
        """
        entries = list(self.parser.parse_file(file_path))
        return self.analyze_entries(entries)
    
    def analyze_lines(self, lines: list[str]) -> LogStats:
        """
        Analyze log lines and return statistics.
        
        Args:
            lines: List of log lines to analyze
            
        Returns:
            LogStats object with analysis results
        """
        entries = list(self.parser.parse_lines(lines))
        return self.analyze_entries(entries)
    
    def analyze_entries(self, entries: list[LogEntry]) -> LogStats:
        """
        Analyze parsed log entries and return statistics.
        
        Args:
            entries: List of LogEntry objects
            
        Returns:
            LogStats object with analysis results
        """
        self._entries = entries
        
        stats = LogStats()
        stats.total_lines = len(entries)
        stats.parsed_entries = len([e for e in entries if e.message])
        
        # Count by level
        level_counter = Counter()
        for entry in entries:
            level_counter[entry.level.value] += 1
        stats.by_level = dict(level_counter)
        
        # Count by source
        source_counter = Counter()
        for entry in entries:
            if entry.source:
                source_counter[entry.source] += 1
        stats.sources = dict(source_counter)
        
        # Time range analysis
        timestamps = [e.timestamp for e in entries if e.timestamp]
        if timestamps:
            stats.time_range = (min(timestamps), max(timestamps))
        
        # Error pattern detection
        if self.detect_patterns:
            stats.error_patterns = self._detect_error_patterns(entries)
        
        # Calculate rates
        stats.calculate_rates()
        
        return stats
    
    def _detect_error_patterns(self, entries: list[LogEntry]) -> list[ErrorPattern]:
        """Detect and group error patterns in log entries."""
        error_entries = [
            e for e in entries 
            if e.level in (LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.FATAL, LogLevel.WARNING)
        ]
        
        if not error_entries:
            return []
        
        patterns: list[ErrorPattern] = []
        
        for entry in error_entries:
            # Normalize message for pattern matching
            normalized = self._normalize_message(entry.message)
            
            # Try to match existing pattern
            matched = False
            for pattern in patterns:
                if self._is_similar(normalized, pattern.pattern):
                    pattern.add_occurrence(entry.line_number, entry.message)
                    matched = True
                    break
            
            if not matched:
                # Create new pattern
                patterns.append(ErrorPattern(
                    pattern=normalized,
                    count=1,
                    level=entry.level,
                    first_occurrence=entry.line_number,
                    last_occurrence=entry.line_number,
                    sample_messages=[entry.message],
                ))
        
        # Sort by count descending
        patterns.sort(key=lambda p: p.count, reverse=True)
        
        return patterns
    
    def _normalize_message(self, message: str) -> str:
        """Normalize log message for pattern matching."""
        # Remove specific values (numbers, UUIDs, paths, etc.)
        normalized = message.lower()
        
        # Replace numbers
        normalized = re.sub(r"\b\d+\b", "<num>", normalized)
        
        # Replace UUIDs
        normalized = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "<uuid>",
            normalized,
            flags=re.IGNORECASE
        )
        
        # Replace file paths
        normalized = re.sub(r"(/[a-z0-9_\-./]+)", "<path>", normalized)
        
        # Replace IP addresses
        normalized = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "<ip>", normalized)
        
        # Replace URLs
        normalized = re.sub(r"https?://[^\s]+", "<url>", normalized)
        
        # Replace email addresses
        normalized = re.sub(r"\b[\w.-]+@[\w.-]+\.\w+\b", "<email>", normalized)
        
        # Collapse whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()
        
        return normalized
    
    def _is_similar(self, msg1: str, msg2: str) -> bool:
        """Check if two normalized messages are similar."""
        if msg1 == msg2:
            return True
        
        # Use sequence matcher for fuzzy comparison
        ratio = SequenceMatcher(None, msg1, msg2).ratio()
        return ratio >= self.pattern_threshold
    
    def filter_by_level(
        self, 
        entries: list[LogEntry], 
        levels: list[LogLevel]
    ) -> list[LogEntry]:
        """Filter entries by log level."""
        return [e for e in entries if e.level in levels]
    
    def filter_by_time(
        self, 
        entries: list[LogEntry], 
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> list[LogEntry]:
        """Filter entries by time range."""
        result = []
        for entry in entries:
            if not entry.timestamp:
                continue
            if start and entry.timestamp < start:
                continue
            if end and entry.timestamp > end:
                continue
            result.append(entry)
        return result
    
    def filter_by_pattern(
        self, 
        entries: list[LogEntry], 
        pattern: str,
        case_sensitive: bool = False,
    ) -> list[LogEntry]:
        """Filter entries by regex pattern."""
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        return [e for e in entries if regex.search(e.message)]
    
    def get_errors(self, entries: list[LogEntry]) -> list[LogEntry]:
        """Get all error-level entries."""
        return self.filter_by_level(
            entries, 
            [LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.FATAL]
        )
    
    def get_warnings(self, entries: list[LogEntry]) -> list[LogEntry]:
        """Get all warning-level entries."""
        return self.filter_by_level(entries, [LogLevel.WARNING])
    
    def tail(self, entries: list[LogEntry], n: int = 10) -> list[LogEntry]:
        """Get the last N entries."""
        return entries[-n:]
    
    def head(self, entries: list[LogEntry], n: int = 10) -> list[LogEntry]:
        """Get the first N entries."""
        return entries[:n]
    
    def search(self, entries: list[LogEntry], query: str) -> list[LogEntry]:
        """Search entries by text query."""
        return self.filter_by_pattern(entries, query)
