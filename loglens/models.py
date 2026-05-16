"""
LogLens Data Models
===================

Pydantic models for structured log data representation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log level enumeration with common log levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    TRACE = "TRACE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, level_str: str) -> "LogLevel":
        """Convert string to LogLevel, case-insensitive."""
        level_upper = level_str.upper().strip()
        for level in cls:
            if level.value == level_upper:
                return level
        return cls.UNKNOWN


class LogEntry(BaseModel):
    """Represents a single parsed log entry."""
    
    timestamp: Optional[datetime] = None
    level: LogLevel = LogLevel.UNKNOWN
    message: str
    source: Optional[str] = None
    raw_line: str
    line_number: int
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "use_enum_values": False,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class ErrorPattern(BaseModel):
    """Represents a detected error pattern in logs."""
    
    pattern: str
    count: int = 1
    level: LogLevel
    first_occurrence: int  # Line number
    last_occurrence: int   # Line number
    sample_messages: list[str] = Field(default_factory=list, max_length=5)

    def add_occurrence(self, line_number: int, message: str) -> None:
        """Add a new occurrence of this error pattern."""
        self.count += 1
        self.last_occurrence = line_number
        if len(self.sample_messages) < 5:
            self.sample_messages.append(message)


class LogStats(BaseModel):
    """Statistics summary for analyzed logs."""
    
    total_lines: int = 0
    parsed_entries: int = 0
    by_level: dict[str, int] = Field(default_factory=dict)
    error_patterns: list[ErrorPattern] = Field(default_factory=list)
    time_range: Optional[tuple[datetime, datetime]] = None
    sources: dict[str, int] = Field(default_factory=dict)
    error_rate: float = 0.0
    warning_rate: float = 0.0

    def calculate_rates(self) -> None:
        """Calculate error and warning rates."""
        if self.parsed_entries > 0:
            error_count = self.by_level.get(LogLevel.ERROR.value, 0)
            error_count += self.by_level.get(LogLevel.CRITICAL.value, 0)
            error_count += self.by_level.get(LogLevel.FATAL.value, 0)
            warning_count = self.by_level.get(LogLevel.WARNING.value, 0)
            
            self.error_rate = (error_count / self.parsed_entries) * 100
            self.warning_rate = (warning_count / self.parsed_entries) * 100


class LogFormat(str, Enum):
    """Supported log format types."""
    
    AUTO = "auto"
    COMMON = "common"          # Common log format: [LEVEL] message
    APACHE = "apache"          # Apache access log format
    NGINX = "nginx"            # Nginx log format
    JSON = "json"              # JSON structured logs
    SYSLOG = "syslog"          # Syslog format
    TIMESTAMP = "timestamp"    # Timestamp prefixed logs
    CUSTOM = "custom"          # Custom regex pattern
