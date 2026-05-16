<p align="center">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">简体中文</a> | 
  <a href="README_TW.md">繁體中文</a>
</p>

# 🔍 LogLens

<p align="center">
  <strong>智慧日誌分析命令列工具</strong>
</p>

<p align="center">
  <em>多格式解析 • 錯誤模式識別 • 精美終端輸出</em>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#安裝">安裝</a> •
  <a href="#快速開始">快速開始</a> •
  <a href="#使用指南">使用指南</a> •
  <a href="#貢獻指南">貢獻指南</a>
</p>

---

## 🎉 專案介紹

**LogLens** 是一款專為開發者和維運工程師設計的強大命令列日誌分析工具。憑藉智慧模式檢測、自動格式識別和精美的終端輸出，LogLens 讓繁瑣的日誌分析工作變得輕鬆愉快。

### 為什麼選擇 LogLens？

- 🚀 **快速分析**：秒級處理數千行日誌
- 🎯 **智慧檢測**：自動識別錯誤模式和異常
- 🎨 **精美輸出**：彩色編碼、格式化的終端顯示
- 📊 **豐富統計**：全面的指標和洞察
- 🔧 **靈活過濾**：按級別、模式、時間範圍等多維度過濾

---

## ✨ 功能特性

### 📋 多格式支援
- **通用日誌格式**：`[級別] 訊息` 風格的日誌
- **JSON 結構化日誌**：解析 JSON 格式的日誌項目
- **Apache/Nginx 存取日誌**：Web 伺服器日誌分析
- **Syslog 格式**：系統日誌解析
- **自動檢測**：自動識別日誌格式

### 🔍 智慧分析
- **錯誤模式檢測**：自動歸類相似錯誤
- **級別分佈統計**：視覺化日誌級別分佈
- **時間範圍分析**：追蹤活動時間線
- **來源追蹤**：識別日誌來源

### 🎨 精美輸出
- **彩色級別標識**：即時視覺識別嚴重程度
- **豐富表格**：格式化的統計展示
- **進度指示器**：即時分析回饋
- **JSON 匯出**：機器可讀的輸出選項

### ⚡ 強大命令列
- **按級別過濾**：`--level error --level warning`
- **模式搜尋**：`--pattern "connection.*failed"`
- **頭部/尾部預覽**：快速查看日誌項目
- **即時追蹤**：即時日誌監控
- **管線支援**：與 Unix 管線無縫整合

---

## 🚀 快速開始

### 環境需求
- Python 3.9 或更高版本
- pip 套件管理器

### 安裝方式

```bash
# 從 PyPI 安裝
pip install loglens

# 或從原始碼安裝
git clone https://github.com/gitstq/LogLens.git
cd LogLens
pip install -e .
```

### 基本用法

```bash
# 分析日誌檔案
loglens analyze app.log

# 按錯誤級別過濾
loglens analyze app.log --level error

# 搜尋特定模式
loglens search app.log "connection.*failed"

# 顯示最後 20 行
loglens tail app.log -n 20

# 即時追蹤日誌更新
loglens tail app.log --follow

# 顯示所有錯誤
loglens errors app.log
```

---

## 📖 使用指南

### analyze 命令

`analyze` 命令提供全面的日誌分析：

```bash
# 基本分析
loglens analyze app.log

# 按多個級別過濾
loglens analyze app.log --level error --level warning

# 使用正規表示式搜尋
loglens analyze app.log --pattern "database.*error"

# 指定日誌格式
loglens analyze app.log --format json

# 輸出為 JSON
loglens analyze app.log --json

# 顯示前/後 N 條
loglens analyze app.log --head 50
loglens analyze app.log --tail 50
```

### stats 命令

取得日誌的詳細統計資訊：

```bash
loglens stats app.log
```

輸出包括：
- 總行數
- 級別分佈
- 錯誤率百分比
- 偵測到的錯誤模式
- 時間範圍

### tail 命令

即時監控日誌：

```bash
# 顯示最後 10 行
loglens tail app.log

# 顯示最後 50 行
loglens tail app.log -n 50

# 追蹤檔案更新
loglens tail app.log --follow

# 追蹤時過濾
loglens tail app.log --follow --level error
```

### errors 命令

快速識別所有錯誤：

```bash
# 顯示所有錯誤
loglens errors app.log

# 包含警告
loglens errors app.log --level warning
```

### search 命令

尋找特定日誌項目：

```bash
# 不區分大小寫搜尋
loglens search app.log "timeout"

# 區分大小寫搜尋
loglens search app.log "ERROR" --case-sensitive

# 正規表示式模式
loglens search app.log "connection.*refused"
```

### 管線支援

與 Unix 管線整合：

```bash
# 從標準輸入分析
cat app.log | loglens analyze

# 與其他工具鏈式使用
grep "ERROR" app.log | loglens analyze
```

---

## 💡 設計理念

### 為什麼開發 LogLens

日誌分析是開發者和維運工程師的日常工作。現有工具往往：
- 設定複雜，不適合快速分析
- 僅支援特定日誌格式
- 難以整合到工作流程中

LogLens 解決了這些問題：
- **零設定**：開箱即用
- **通用格式支援**：處理任何日誌格式
- **命令列優先**：完美適配自動化和腳本

### 技術選型

- **Python**：跨平台相容性和豐富生態
- **Click**：業界標準的 CLI 框架
- **Rich**：無依賴的精美終端輸出
- **Pydantic**：型別安全的資料模型

### 未來規劃

- [ ] AI 驅動的異常檢測
- [ ] Web 分析儀表板
- [ ] 多格式匯出（CSV、HTML）
- [ ] 自訂日誌格式定義
- [ ] 監控系統整合

---

## 📦 建置與部署

### 從原始碼建置

```bash
# 複製儲存庫
git clone https://github.com/gitstq/LogLens.git
cd LogLens

# 安裝開發相依套件
pip install -e ".[dev]"

# 執行測試
pytest

# 建置套件
pip install build
python -m build
```

### 執行測試

```bash
# 執行所有測試
pytest

# 帶覆蓋率執行
pytest --cov=loglens
```

---

## 🤝 貢獻指南

我們歡迎各種形式的貢獻！開始步驟：

1. **Fork 本儲存庫**
2. **建立功能分支**：`git checkout -b feature/amazing-feature`
3. **進行修改**
4. **執行測試**：`pytest`
5. **提交變更**：`git commit -m 'feat: 新增功能'`
6. **推送到分支**：`git push origin feature/amazing-feature`
7. **提交 Pull Request**

### 程式碼規範

- 遵循 PEP 8 規範
- 使用型別註解
- 為公共函式編寫文件字串
- 為新功能新增測試

---

## 📄 開源授權

本專案採用 MIT 授權條款開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<p align="center">
  由 LogLens 團隊用 ❤️ 打造
</p>
