"""
LogLens Log Parser
==================

Intelligent log file parser with automatic format detection.
"""

import json
import re
from datetime import datetime
from typing import Iterator, Optional

from loglens.models import LogEntry, LogFormat, LogLevel


class LogParser:
    """
    Intelligent log parser with automatic format detection.
    
    Supports multiple log formats:
    - Common: [LEVEL] message
    - Apache/Nginx access logs
    - JSON structured logs
    - Syslog format
    - Timestamp prefixed logs
    """
    
    # Common timestamp patterns
    TIMESTAMP_PATTERNS = [
        # ISO 8601
        r"(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)",
        # Common log format date
        r"(?P<ts>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}[+-]\d{4})",
        # Syslog format
        r"(?P<ts>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",
        # Simple date time
        r"(?P<ts>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
        # Date only
        r"(?P<ts>\d{4}-\d{2}-\d{2})",
    ]
    
    # Log level patterns
    LEVEL_PATTERNS = [
        # [LEVEL] or [LEVEL]: format
        r"\[(?P<level>DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL|TRACE)\]",
        # LEVEL: format
        r"^(?P<level>DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL|TRACE)\s*[:\-]",
        # - LEVEL - format
        r"[\-\s](?P<level>DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL|TRACE)[\-\s]",
    ]
    
    # Apache/Nginx combined log format
    APACHE_PATTERN = re.compile(
        r'^(?P<ip>[\d.]+)\s+'
        r'(?P<ident>\S+)\s+'
        r'(?P<user>\S+)\s+'
        r'\[(?P<ts>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>\S+)\s*(?P<protocol>[^"]*)"\s+'
        r'(?P<status>\d+)\s+'
        r'(?P<size>\S+)'
        r'(?:\s+"(?P<referer>[^"]*)")?'
        r'(?:\s+"(?P<ua>[^"]*)")?'
    )
    
    def __init__(self, log_format: LogFormat = LogFormat.AUTO):
        """Initialize parser with specified format."""
        self.log_format = log_format
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> list[tuple[re.Pattern, str]]:
        """Compile timestamp regex patterns."""
        patterns = []
        for pattern in self.TIMESTAMP_PATTERNS:
            patterns.append((re.compile(pattern), pattern))
        return patterns
    
    def detect_format(self, sample_lines: list[str]) -> LogFormat:
        """Detect log format from sample lines."""
        if not sample_lines:
            return LogFormat.COMMON
        
        # Check for JSON format
        json_count = 0
        for line in sample_lines[:10]:
            try:
                json.loads(line.strip())
                json_count += 1
            except json.JSONDecodeError:
                pass
        if json_count >= len(sample_lines[:10]) * 0.5:
            return LogFormat.JSON
        
        # Check for Apache/Nginx format
        for line in sample_lines[:5]:
            if self.APACHE_PATTERN.match(line.strip()):
                return LogFormat.APACHE
        
        return LogFormat.COMMON
    
    def parse_line(self, line: str, line_number: int = 0) -> LogEntry:
        """Parse a single log line into a LogEntry."""
        raw_line = line
        line = line.strip()
        
        if not line:
            return LogEntry(
                message="",
                raw_line=raw_line,
                line_number=line_number,
            )
        
        # Try JSON format first
        if line.startswith("{"):
            entry = self._parse_json(line, raw_line, line_number)
            if entry:
                return entry
        
        # Try Apache/Nginx format
        match = self.APACHE_PATTERN.match(line)
        if match:
            return self._parse_apache(match, raw_line, line_number)
        
        # Parse common log format
        return self._parse_common(line, raw_line, line_number)
    
    def _parse_json(self, line: str, raw_line: str, line_number: int) -> Optional[LogEntry]:
        """Parse JSON formatted log line."""
        try:
            data = json.loads(line)
            
            # Extract timestamp
            timestamp = None
            for ts_field in ["timestamp", "time", "@timestamp", "date", "datetime"]:
                if ts_field in data:
                    timestamp = self._parse_timestamp(str(data[ts_field]))
                    break
            
            # Extract level
            level = LogLevel.UNKNOWN
            for level_field in ["level", "severity", "log_level"]:
                if level_field in data:
                    level = LogLevel.from_string(str(data[level_field]))
                    break
            
            # Extract message
            message = ""
            for msg_field in ["message", "msg", "log", "content"]:
                if msg_field in data:
                    message = str(data[msg_field])
                    break
            
            if not message:
                message = line
            
            # Extract source
            source = data.get("source") or data.get("logger") or data.get("name")
            
            # Collect extra fields
            extra = {k: v for k, v in data.items() 
                    if k not in ["timestamp", "time", "@timestamp", "date", "datetime",
                                "level", "severity", "log_level", "message", "msg", 
                                "log", "content", "source", "logger", "name"]}
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=message,
                source=str(source) if source else None,
                raw_line=raw_line,
                line_number=line_number,
                extra=extra,
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def _parse_apache(self, match: re.Match, raw_line: str, line_number: int) -> LogEntry:
        """Parse Apache/Nginx log format."""
        data = match.groupdict()
        
        # Parse timestamp
        timestamp = self._parse_apache_timestamp(data.get("ts", ""))
        
        # Determine level from status code
        status = int(data.get("status", 200))
        if status >= 500:
            level = LogLevel.ERROR
        elif status >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        # Build message
        method = data.get("method", "")
        path = data.get("path", "")
        size = data.get("size", "0")
        message = f"{method} {path} - {status} ({size} bytes)"
        
        extra = {
            "ip": data.get("ip"),
            "user": data.get("user"),
            "protocol": data.get("protocol"),
            "referer": data.get("referer"),
            "user_agent": data.get("ua"),
        }
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=data.get("ip"),
            raw_line=raw_line,
            line_number=line_number,
            extra=extra,
        )
    
    def _parse_common(self, line: str, raw_line: str, line_number: int) -> LogEntry:
        """Parse common log format."""
        timestamp = None
        level = LogLevel.INFO
        message = line
        
        # Try to extract timestamp
        for pattern, _ in self._compiled_patterns:
            match = pattern.search(line)
            if match:
                ts_str = match.group("ts")
                timestamp = self._parse_timestamp(ts_str)
                # Remove timestamp from message
                message = pattern.sub("", line).strip()
                break
        
        # Try to extract log level
        for pattern_str in self.LEVEL_PATTERNS:
            match = re.search(pattern_str, line, re.IGNORECASE)
            if match:
                level_str = match.group("level")
                level = LogLevel.from_string(level_str)
                # Remove level from message
                message = re.sub(re.escape(match.group(0)), "", message, count=1).strip()
                break
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            raw_line=raw_line,
            line_number=line_number,
        )
    
    def _parse_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime."""
        ts_str = ts_str.strip()
        
        # Try ISO format
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%d/%b/%Y:%H:%M:%S%z",
            "%b %d %H:%M:%S",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_apache_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Parse Apache log timestamp format."""
        try:
            # Format: 10/Oct/2000:13:55:36 -0700
            return datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S %z")
        except ValueError:
            return self._parse_timestamp(ts_str)
    
    def parse_file(self, file_path: str) -> Iterator[LogEntry]:
        """Parse log file line by line."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                yield self.parse_line(line, line_number)
    
    def parse_lines(self, lines: list[str]) -> Iterator[LogEntry]:
        """Parse multiple log lines."""
        for line_number, line in enumerate(lines, start=1):
            yield self.parse_line(line, line_number)
