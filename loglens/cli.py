"""
LogLens CLI Interface
=====================

Command-line interface for LogLens log analysis tool.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from loglens import __version__
from loglens.analyzer import LogAnalyzer
from loglens.models import LogFormat, LogLevel
from loglens.parser import LogParser

console = Console()


def print_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"[bold blue]LogLens[/bold blue] version [green]{__version__}[/green]")
    ctx.exit()


def print_banner() -> None:
    """Print LogLens banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🔍 LogLens - Intelligent Log Analysis CLI Tool          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, callback=print_version, 
              help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """
    🔍 LogLens - Intelligent Log Analysis CLI Tool
    
    Analyze log files with smart pattern detection, error identification,
    and beautiful terminal output.
    
    \b
    Examples:
        loglens analyze app.log
        loglens analyze app.log --level error
        loglens tail app.log --follow
        loglens stats app.log
    """
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print(ctx.get_help())


@main.command()
@click.argument("file", type=click.Path(exists=True), required=False)
@click.option("--level", "-l", "levels", multiple=True,
              type=click.Choice(["debug", "info", "warning", "error", "critical"]),
              help="Filter by log level (can be used multiple times)")
@click.option("--pattern", "-p", "search_pattern",
              help="Filter by regex pattern")
@click.option("--format", "-f", "log_format",
              type=click.Choice(["auto", "common", "json", "apache", "nginx"]),
              default="auto", help="Log format (default: auto-detect)")
@click.option("--output", "-o", "output_file",
              type=click.Path(), help="Output to file")
@click.option("--no-patterns", is_flag=True,
              help="Disable error pattern detection")
@click.option("--head", "-H", "head_count", type=int,
              help="Show first N entries")
@click.option("--tail", "-T", "tail_count", type=int,
              help="Show last N entries")
@click.option("--json", "output_json", is_flag=True,
              help="Output in JSON format")
def analyze(
    file: Optional[str],
    levels: tuple[str, ...],
    search_pattern: Optional[str],
    log_format: str,
    output_file: Optional[str],
    no_patterns: bool,
    head_count: Optional[int],
    tail_count: Optional[int],
    output_json: bool,
) -> None:
    """
    Analyze a log file and show statistics.
    
    \b
    Examples:
        loglens analyze app.log
        loglens analyze app.log --level error --level warning
        loglens analyze app.log --pattern "connection.*failed"
    """
    print_banner()
    
    # Read from stdin if no file provided
    if file is None:
        if sys.stdin.isatty():
            console.print("[red]Error: No file specified and no stdin input[/red]")
            sys.exit(1)
        lines = sys.stdin.readlines()
        parser = LogParser(LogFormat(log_format))
        analyzer = LogAnalyzer(parser, detect_patterns=not no_patterns)
        stats = analyzer.analyze_lines(lines)
        entries = list(parser.parse_lines(lines))
    else:
        parser = LogParser(LogFormat(log_format))
        analyzer = LogAnalyzer(parser, detect_patterns=not no_patterns)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing log file...", total=None)
            stats = analyzer.analyze_file(file)
            entries = list(parser.parse_file(file))
    
    # Apply filters
    if levels:
        level_objs = [LogLevel.from_string(l) for l in levels]
        entries = analyzer.filter_by_level(entries, level_objs)
    
    if search_pattern:
        entries = analyzer.filter_by_pattern(entries, search_pattern)
    
    if head_count:
        entries = entries[:head_count]
    elif tail_count:
        entries = entries[-tail_count:]
    
    # Output results
    if output_json:
        import json
        output = {
            "stats": stats.model_dump(),
            "entries": [e.model_dump() for e in entries[:100]],
        }
        output_str = json.dumps(output, indent=2, default=str)
        if output_file:
            Path(output_file).write_text(output_str)
        else:
            console.print(output_str)
    else:
        _print_stats(stats)
        if entries and not head_count and not tail_count:
            _print_entries(entries[:50])


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "-f", "log_format",
              type=click.Choice(["auto", "common", "json", "apache", "nginx"]),
              default="auto", help="Log format")
def stats(file: str, log_format: str) -> None:
    """
    Show statistics for a log file.
    
    \b
    Examples:
        loglens stats app.log
    """
    print_banner()
    
    parser = LogParser(LogFormat(log_format))
    analyzer = LogAnalyzer(parser)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Computing statistics...", total=None)
        result = analyzer.analyze_file(file)
    
    _print_stats(result)


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--lines", "-n", default=10, help="Number of lines to show")
@click.option("--follow", "-F", is_flag=True, help="Follow file updates")
@click.option("--level", "-l", "levels", multiple=True,
              type=click.Choice(["debug", "info", "warning", "error", "critical"]),
              help="Filter by log level")
def tail(file: str, lines: int, follow: bool, levels: tuple[str, ...]) -> None:
    """
    Show the last N lines of a log file.
    
    \b
    Examples:
        loglens tail app.log
        loglens tail app.log -n 50
        loglens tail app.log --follow
    """
    parser = LogParser()
    analyzer = LogAnalyzer(parser, detect_patterns=False)
    
    entries = list(parser.parse_file(file))
    
    if levels:
        level_objs = [LogLevel.from_string(l) for l in levels]
        entries = analyzer.filter_by_level(entries, level_objs)
    
    entries = entries[-lines:]
    _print_entries(entries)
    
    if follow:
        console.print("\n[dim]Following file updates... (Ctrl+C to stop)[/dim]")
        import time
        last_size = Path(file).stat().st_size
        try:
            while True:
                time.sleep(0.5)
                current_size = Path(file).stat().st_size
                if current_size > last_size:
                    with open(file, "r") as f:
                        f.seek(last_size)
                        new_content = f.read()
                        for line in new_content.strip().split("\n"):
                            if line:
                                entry = parser.parse_line(line)
                                _print_entry(entry)
                    last_size = current_size
        except KeyboardInterrupt:
            console.print("\n[dim]Stopped following file[/dim]")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--level", "-l", "level",
              type=click.Choice(["debug", "info", "warning", "error", "critical"]),
              default="error", help="Minimum level to show")
def errors(file: str, level: str) -> None:
    """
    Show all errors in a log file.
    
    \b
    Examples:
        loglens errors app.log
        loglens errors app.log --level warning
    """
    print_banner()
    
    parser = LogParser()
    analyzer = LogAnalyzer(parser, detect_patterns=False)
    
    entries = list(parser.parse_file(file))
    
    # Get entries at or above the specified level
    level_order = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.WARNING: 2,
        LogLevel.ERROR: 3,
        LogLevel.CRITICAL: 4,
        LogLevel.FATAL: 5,
    }
    min_level = LogLevel.from_string(level)
    min_priority = level_order.get(min_level, 3)
    
    error_entries = [
        e for e in entries 
        if level_order.get(e.level, 0) >= min_priority
    ]
    
    _print_entries(error_entries)
    
    console.print(f"\n[bold]Total:[/bold] {len(error_entries)} entries")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.argument("query")
@click.option("--case-sensitive", "-c", is_flag=True, help="Case sensitive search")
def search(file: str, query: str, case_sensitive: bool) -> None:
    """
    Search for entries matching a pattern.
    
    \b
    Examples:
        loglens search app.log "connection.*failed"
        loglens search app.log "ERROR" --case-sensitive
    """
    print_banner()
    
    parser = LogParser()
    analyzer = LogAnalyzer(parser, detect_patterns=False)
    
    entries = list(parser.parse_file(file))
    results = analyzer.filter_by_pattern(entries, query, case_sensitive)
    
    _print_entries(results)
    
    console.print(f"\n[bold]Found:[/bold] {len(results)} matching entries")


def _print_stats(stats: LogStats) -> None:
    """Print log statistics in a formatted table."""
    # Summary panel
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="green", justify="right")
    
    summary.add_row("Total Lines", str(stats.total_lines))
    summary.add_row("Parsed Entries", str(stats.parsed_entries))
    summary.add_row("Error Rate", f"{stats.error_rate:.1f}%")
    summary.add_row("Warning Rate", f"{stats.warning_rate:.1f}%")
    
    console.print(Panel(summary, title="📊 Summary", border_style="blue"))
    
    # Level distribution
    if stats.by_level:
        level_table = Table(title="📈 Level Distribution", show_lines=True)
        level_table.add_column("Level", style="bold")
        level_table.add_column("Count", justify="right")
        level_table.add_column("Percentage", justify="right")
        
        level_colors = {
            "DEBUG": "dim",
            "INFO": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold red",
            "FATAL": "bold red reverse",
        }
        
        for level, count in sorted(stats.by_level.items(), key=lambda x: -x[1]):
            percentage = (count / stats.parsed_entries * 100) if stats.parsed_entries > 0 else 0
            color = level_colors.get(level, "white")
            level_table.add_row(
                f"[{color}]{level}[/{color}]",
                str(count),
                f"{percentage:.1f}%"
            )
        
        console.print(level_table)
    
    # Error patterns
    if stats.error_patterns:
        pattern_table = Table(title="🔍 Detected Error Patterns", show_lines=True)
        pattern_table.add_column("Pattern", style="yellow", max_width=50)
        pattern_table.add_column("Count", justify="right")
        pattern_table.add_column("Level", style="bold")
        pattern_table.add_column("Lines", justify="right")
        
        for pattern in stats.error_patterns[:10]:  # Top 10 patterns
            pattern_table.add_row(
                pattern.pattern[:50] + ("..." if len(pattern.pattern) > 50 else ""),
                str(pattern.count),
                f"[red]{pattern.level.value}[/red]",
                f"{pattern.first_occurrence}-{pattern.last_occurrence}"
            )
        
        console.print(pattern_table)
    
    # Time range
    if stats.time_range:
        start, end = stats.time_range
        duration = end - start
        console.print(f"\n[bold]Time Range:[/bold] {start} to {end} (duration: {duration})")


def _print_entries(entries: list[LogEntry]) -> None:
    """Print log entries in a formatted way."""
    if not entries:
        console.print("[dim]No entries to display[/dim]")
        return
    
    for entry in entries:
        _print_entry(entry)


def _print_entry(entry: LogEntry) -> None:
    """Print a single log entry."""
    level_colors = {
        LogLevel.DEBUG: "dim",
        LogLevel.INFO: "blue",
        LogLevel.WARNING: "yellow",
        LogLevel.ERROR: "red",
        LogLevel.CRITICAL: "bold red",
        LogLevel.FATAL: "bold red reverse",
        LogLevel.UNKNOWN: "white",
    }
    
    color = level_colors.get(entry.level, "white")
    
    # Build the output line
    parts = []
    
    if entry.timestamp:
        parts.append(f"[dim]{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    
    parts.append(f"[{color}]{entry.level.value:8}[/{color}]")
    
    if entry.source:
        parts.append(f"[cyan][{entry.source}][/cyan]")
    
    parts.append(entry.message)
    
    console.print(" ".join(parts))


if __name__ == "__main__":
    main()
