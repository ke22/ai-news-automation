# AI 新聞自動化系統（GitHub 雲端版）

## 功能特色
- 自動收集 AI 相關新聞（NewsAPI、RSS、Hacker News）
- 使用 Gemini AI 進行新聞評分與篩選
- 生成多種格式的內容輸出
- 支援發布到多個平台

## 環境設定

### 必要環境變數
```bash
# Gemini AI (主要 AI 處理引擎)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# News API (新聞收集)
NEWS_API_KEY=your_news_api_key_here
```

### 選擇性環境變數
```bash
# OpenAI (備用 AI 引擎)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# 發布平台
CONFLUENCE_TOKEN=your_confluence_token_here
CONFLUENCE_BASE=https://your-domain.atlassian.net
CONFLUENCE_SPACE=AI

FIGMA_TOKEN=your_figma_token_here
FIGMA_FILE_ID=your_figma_file_id_here

SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

## 安裝與執行

1. 安裝依賴：
```bash
./setup.sh
```

2. 設定環境變數（參考 `config/env.example`）

3. 執行工作流程：
```bash
# 方法一：使用 runner 腳本（推薦）
python run.py collect    # 收集新聞
python run.py process    # AI 處理與評分
python run.py publish    # 發布內容
python run.py analyze    # 週度分析

# 方法二：直接執行腳本
python scripts/collect.py    # 收集新聞
python scripts/process.py    # AI 處理與評分
python scripts/publish.py    # 發布內容
```

4. 查看結果：
```bash
# 查看統計資訊
python view_results.py stats

# 查看最新生成內容
python view_results.py latest

# 查看所有可用結果
python view_results.py all

# 或直接查看檔案
cat content/2025/08/22/format_a_social.md    # 社交媒體格式
cat content/2025/08/22/format_b_apa.md       # APA 引用格式
cat content/2025/08/22/format_c_design.txt   # 設計格式
```

詳見工作流程與 scripts/ 內容。
