"""
LogLens - Intelligent Log Analysis CLI Tool
============================================

A powerful command-line tool for analyzing log files with smart pattern detection,
error identification, and beautiful terminal output.

Author: LogLens Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "LogLens Team"

from loglens.analyzer import LogAnalyzer
from loglens.parser import LogParser
from loglens.models import LogEntry, LogStats, ErrorPattern

__all__ = [
    "LogAnalyzer",
    "LogParser",
    "LogEntry",
    "LogStats",
    "ErrorPattern",
    "__version__",
]
