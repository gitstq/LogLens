<p align="center">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">简体中文</a> | 
  <a href="README_TW.md">繁體中文</a>
</p>

# 🔍 LogLens

<p align="center">
  <strong>智能日志分析命令行工具</strong>
</p>

<p align="center">
  <em>多格式解析 • 错误模式识别 • 精美终端输出</em>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#安装">安装</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用指南">使用指南</a> •
  <a href="#贡献指南">贡献指南</a>
</p>

---

## 🎉 项目介绍

**LogLens** 是一款专为开发者和运维工程师设计的强大命令行日志分析工具。凭借智能模式检测、自动格式识别和精美的终端输出，LogLens 让繁琐的日志分析工作变得轻松愉快。

### 为什么选择 LogLens？

- 🚀 **快速分析**：秒级处理数千行日志
- 🎯 **智能检测**：自动识别错误模式和异常
- 🎨 **精美输出**：彩色编码、格式化的终端显示
- 📊 **丰富统计**：全面的指标和洞察
- 🔧 **灵活过滤**：按级别、模式、时间范围等多维度过滤

---

## ✨ 功能特性

### 📋 多格式支持
- **通用日志格式**：`[级别] 消息` 风格的日志
- **JSON 结构化日志**：解析 JSON 格式的日志条目
- **Apache/Nginx 访问日志**：Web 服务器日志分析
- **Syslog 格式**：系统日志解析
- **自动检测**：自动识别日志格式

### 🔍 智能分析
- **错误模式检测**：自动归类相似错误
- **级别分布统计**：可视化日志级别分布
- **时间范围分析**：追踪活动时间线
- **来源追踪**：识别日志来源

### 🎨 精美输出
- **彩色级别标识**：即时视觉识别严重程度
- **丰富表格**：格式化的统计展示
- **进度指示器**：实时分析反馈
- **JSON 导出**：机器可读的输出选项

### ⚡ 强大命令行
- **按级别过滤**：`--level error --level warning`
- **模式搜索**：`--pattern "connection.*failed"`
- **头部/尾部预览**：快速查看日志条目
- **实时追踪**：实时日志监控
- **管道支持**：与 Unix 管道无缝集成

---

## 🚀 快速开始

### 环境要求
- Python 3.9 或更高版本
- pip 包管理器

### 安装方式

```bash
# 从 PyPI 安装
pip install loglens

# 或从源码安装
git clone https://github.com/gitstq/LogLens.git
cd LogLens
pip install -e .
```

### 基本用法

```bash
# 分析日志文件
loglens analyze app.log

# 按错误级别过滤
loglens analyze app.log --level error

# 搜索特定模式
loglens search app.log "connection.*failed"

# 显示最后 20 行
loglens tail app.log -n 20

# 实时追踪日志更新
loglens tail app.log --follow

# 显示所有错误
loglens errors app.log
```

---

## 📖 使用指南

### analyze 命令

`analyze` 命令提供全面的日志分析：

```bash
# 基本分析
loglens analyze app.log

# 按多个级别过滤
loglens analyze app.log --level error --level warning

# 使用正则表达式搜索
loglens analyze app.log --pattern "database.*error"

# 指定日志格式
loglens analyze app.log --format json

# 输出为 JSON
loglens analyze app.log --json

# 显示前/后 N 条
loglens analyze app.log --head 50
loglens analyze app.log --tail 50
```

### stats 命令

获取日志的详细统计信息：

```bash
loglens stats app.log
```

输出包括：
- 总行数
- 级别分布
- 错误率百分比
- 检测到的错误模式
- 时间范围

### tail 命令

实时监控日志：

```bash
# 显示最后 10 行
loglens tail app.log

# 显示最后 50 行
loglens tail app.log -n 50

# 追踪文件更新
loglens tail app.log --follow

# 追踪时过滤
loglens tail app.log --follow --level error
```

### errors 命令

快速识别所有错误：

```bash
# 显示所有错误
loglens errors app.log

# 包含警告
loglens errors app.log --level warning
```

### search 命令

查找特定日志条目：

```bash
# 不区分大小写搜索
loglens search app.log "timeout"

# 区分大小写搜索
loglens search app.log "ERROR" --case-sensitive

# 正则表达式模式
loglens search app.log "connection.*refused"
```

### 管道支持

与 Unix 管道集成：

```bash
# 从标准输入分析
cat app.log | loglens analyze

# 与其他工具链式使用
grep "ERROR" app.log | loglens analyze
```

---

## 💡 设计理念

### 为什么开发 LogLens

日志分析是开发者和运维工程师的日常工作。现有工具往往：
- 配置复杂，不适合快速分析
- 仅支持特定日志格式
- 难以集成到工作流中

LogLens 解决了这些问题：
- **零配置**：开箱即用
- **通用格式支持**：处理任何日志格式
- **命令行优先**：完美适配自动化和脚本

### 技术选型

- **Python**：跨平台兼容性和丰富生态
- **Click**：业界标准的 CLI 框架
- **Rich**：无依赖的精美终端输出
- **Pydantic**：类型安全的数据模型

### 未来规划

- [ ] AI 驱动的异常检测
- [ ] Web 分析仪表盘
- [ ] 多格式导出（CSV、HTML）
- [ ] 自定义日志格式定义
- [ ] 监控系统集成

---

## 📦 构建与部署

### 从源码构建

```bash
# 克隆仓库
git clone https://github.com/gitstq/LogLens.git
cd LogLens

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 构建包
pip install build
python -m build
```

### 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率运行
pytest --cov=loglens
```

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！开始步骤：

1. **Fork 本仓库**
2. **创建功能分支**：`git checkout -b feature/amazing-feature`
3. **进行修改**
4. **运行测试**：`pytest`
5. **提交更改**：`git commit -m 'feat: 添加新功能'`
6. **推送到分支**：`git push origin feature/amazing-feature`
7. **提交 Pull Request**

### 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 为公共函数编写文档字符串
- 为新功能添加测试

---

## 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  由 LogLens 团队用 ❤️ 打造
</p>
