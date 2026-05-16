<p align="center">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">简体中文</a> | 
  <a href="README_TW.md">繁體中文</a>
</p>

# 🔍 LogLens

<p align="center">
  <strong>Intelligent Log Analysis CLI Tool</strong>
</p>

<p align="center">
  <em>Multi-format parsing • Error pattern detection • Beautiful terminal output</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## 🎉 Introduction

**LogLens** is a powerful command-line tool designed to help developers and DevOps engineers analyze log files efficiently. With intelligent pattern detection, automatic format recognition, and beautiful terminal output, LogLens transforms the tedious task of log analysis into a breeze.

### Why LogLens?

- 🚀 **Fast Analysis**: Process thousands of log lines in seconds
- 🎯 **Smart Detection**: Automatically identify error patterns and anomalies
- 🎨 **Beautiful Output**: Color-coded, formatted terminal display
- 📊 **Rich Statistics**: Comprehensive metrics and insights
- 🔧 **Flexible Filtering**: Filter by level, pattern, time range, and more

---

## ✨ Features

### 📋 Multi-Format Support
- **Common Log Format**: `[LEVEL] message` style logs
- **JSON Structured Logs**: Parse JSON-formatted log entries
- **Apache/Nginx Access Logs**: Web server log analysis
- **Syslog Format**: System log parsing
- **Auto-Detection**: Automatically detect log format

### 🔍 Intelligent Analysis
- **Error Pattern Detection**: Group similar errors automatically
- **Level Distribution**: Visualize log level breakdown
- **Time Range Analysis**: Track activity over time
- **Source Tracking**: Identify log sources

### 🎨 Beautiful Output
- **Color-Coded Levels**: Instant visual recognition of severity
- **Rich Tables**: Formatted statistics display
- **Progress Indicators**: Real-time analysis feedback
- **JSON Export**: Machine-readable output option

### ⚡ Powerful CLI
- **Filter by Level**: `--level error --level warning`
- **Pattern Search**: `--pattern "connection.*failed"`
- **Head/Tail**: Quick preview of log entries
- **Follow Mode**: Real-time log monitoring
- **Pipeline Support**: Integrate with Unix pipes

---

## 🚀 Quick Start

### Requirements
- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Install from PyPI
pip install loglens

# Or install from source
git clone https://github.com/gitstq/LogLens.git
cd LogLens
pip install -e .
```

### Basic Usage

```bash
# Analyze a log file
loglens analyze app.log

# Filter by error level
loglens analyze app.log --level error

# Search for specific patterns
loglens search app.log "connection.*failed"

# Show last 20 lines
loglens tail app.log -n 20

# Follow log updates in real-time
loglens tail app.log --follow

# Show all errors
loglens errors app.log
```

---

## 📖 Detailed Usage Guide

### Analyze Command

The `analyze` command provides comprehensive log analysis:

```bash
# Basic analysis
loglens analyze app.log

# Filter by multiple levels
loglens analyze app.log --level error --level warning

# Search with regex pattern
loglens analyze app.log --pattern "database.*error"

# Specify log format
loglens analyze app.log --format json

# Output to JSON
loglens analyze app.log --json

# Show first/last N entries
loglens analyze app.log --head 50
loglens analyze app.log --tail 50
```

### Statistics Command

Get detailed statistics about your logs:

```bash
loglens stats app.log
```

Output includes:
- Total line count
- Level distribution
- Error rate percentage
- Detected error patterns
- Time range

### Tail Command

Monitor logs in real-time:

```bash
# Show last 10 lines
loglens tail app.log

# Show last 50 lines
loglens tail app.log -n 50

# Follow file updates
loglens tail app.log --follow

# Filter while tailing
loglens tail app.log --follow --level error
```

### Errors Command

Quickly identify all errors:

```bash
# Show all errors
loglens errors app.log

# Include warnings
loglens errors app.log --level warning
```

### Search Command

Find specific log entries:

```bash
# Case-insensitive search
loglens search app.log "timeout"

# Case-sensitive search
loglens search app.log "ERROR" --case-sensitive

# Regex pattern
loglens search app.log "connection.*refused"
```

### Pipeline Support

Integrate with Unix pipes:

```bash
# Analyze from stdin
cat app.log | loglens analyze

# Chain with other tools
grep "ERROR" app.log | loglens analyze
```

---

## 💡 Design Philosophy

### Why We Built LogLens

Log analysis is a daily task for developers and DevOps engineers. Existing tools are often:
- Too complex for quick analysis
- Limited to specific log formats
- Difficult to integrate into workflows

LogLens solves these problems with:
- **Zero configuration**: Works out of the box
- **Universal format support**: Handles any log format
- **CLI-first design**: Perfect for automation and scripting

### Technical Choices

- **Python**: Cross-platform compatibility and rich ecosystem
- **Click**: Industry-standard CLI framework
- **Rich**: Beautiful terminal output without dependencies
- **Pydantic**: Type-safe data models

### Future Roadmap

- [ ] AI-powered anomaly detection
- [ ] Web dashboard for analysis
- [ ] Export to multiple formats (CSV, HTML)
- [ ] Custom log format definitions
- [ ] Integration with monitoring systems

---

## 📦 Building & Deployment

### Build from Source

```bash
# Clone the repository
git clone https://github.com/gitstq/LogLens.git
cd LogLens

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build package
pip install build
python -m build
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=loglens
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `pytest`
5. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for public functions
- Add tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by the LogLens Team
</p>
