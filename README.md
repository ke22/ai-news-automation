# 🤖 AI 新聞自動化系統

專業的 AI 產業新聞自動化系統，支援兩階段工作流程：AI 挑選新聞 → 人工選擇調整 → AI 產出格式 → 資料庫儲存。

## 🚀 功能特色

### 兩階段工作流程
1. **階段 1: AI 挑選新聞**
   - 自動收集 AI 相關新聞
   - AI 評分與分類（技術/影響/實戰/時效）
   - 生成候選看板供人工選擇

2. **階段 2: 人工選擇與 AI 產出**
   - 支援多種人工指令（#選擇、#重搜、#過濾等）
   - AI 生成三種格式輸出
   - 自動儲存到資料庫

### 三種輸出格式
- **格式 A: 社群傳播版** - 繁體中文，適合社群媒體
- **格式 B: APA 7 引用格式** - 學術引用標準
- **格式 C: 視覺設計版** - 簡潔設計用

### 資料庫整合
- **格式 C → Google Sheets → Figma** - 自動同步
- **格式 A → GitHub 資料庫** - 版本控制

## 📋 系統需求

- Python 3.8+
- macOS/Linux/Windows
- 網路連接

## 🔧 快速安裝

### 1. 克隆專案
```bash
git clone https://github.com/your-username/ai-news-automation.git
cd ai-news-automation
```

### 2. 設定環境
```bash
# 方法一：使用設定腳本（推薦）
./setup_env.sh

# 方法二：手動設定
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
export NEWS_API_KEY="your_actual_news_api_key_here"
```

### 3. 安裝依賴
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 🎯 使用方式

### 方法一：完整工作流程（推薦）
```bash
./start_complete_workflow.sh
```

### 方法二：互動式 Web 介面
```bash
./start_interactive.sh
# 然後在瀏覽器中開啟 http://localhost:8081
```

### 方法三：命令行模式
```bash
# 基本命令
python run.py collect      # 收集新聞
python run.py process      # AI 處理
python run.py two-stage    # 兩階段工作流程

# 帶參數執行
python run.py two-stage "#選擇 1 2 3 4 5"
```

### 方法四：測試模式
```bash
python scripts/test_workflow.py
```

## 🔑 API 金鑰設定

### 必需的 API 金鑰
- **GEMINI_API_KEY**: Google AI Studio 的 API 金鑰
- **NEWS_API_KEY**: NewsAPI 的 API 金鑰（可選）

### 可選的 API 金鑰
- **GOOGLE_SHEETS_ID**: Google Sheets 整合
- **GITHUB_TOKEN**: GitHub 資料庫整合
- **FIGMA_TOKEN**: Figma 自動化整合

### 獲取 API 金鑰
- **Gemini AI**: 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
- **News API**: 訪問 [NewsAPI](https://newsapi.org/register) 註冊免費帳戶

## 📁 專案結構

```
ai-news-automation/
├── config/                 # 配置檔案
│   ├── sources.yaml       # 新聞來源配置
│   ├── prompts.yaml       # AI 提示詞配置
│   └── env.example        # 環境變數範例
├── scripts/               # 核心腳本
│   ├── collect.py         # 新聞收集
│   ├── process.py         # AI 處理
│   ├── two_stage_workflow.py  # 兩階段工作流程
│   ├── interactive_web_interface.py  # Web 介面
│   ├── database_integration.py  # 資料庫整合
│   └── test_workflow.py   # 測試模式
├── templates/             # Web 介面模板
├── content/               # 輸出結果
├── data/                  # 原始資料
├── requirements.txt       # Python 依賴
├── run.py                # 主執行器
├── setup_env.sh          # 環境設定腳本
├── start_complete_workflow.sh  # 完整工作流程啟動
└── start_interactive.sh   # Web 介面啟動
```

## 🎮 人工指令說明

### 基本指令
- `#選擇 2 5 7 9 12` - 選擇指定 ID 的新聞
- `#重搜 關鍵詞A, 關鍵詞B` - 重新搜尋特定關鍵詞
- `#過濾 類別=研究突破` - 按類別過濾
- `#合併 3 8` - 合併相同主題的新聞
- `#補證據 4` - 為指定新聞補充證據
- `#改分類 6=企業應用` - 修改新聞分類

### 使用範例
```bash
# 選擇前 5 則新聞
python run.py two-stage "#選擇 1 2 3 4 5"

# 選擇特定類別
python run.py two-stage "#過濾 類別=模型發布" "#選擇 1 2 3"
```

## 📊 輸出格式範例

### 格式 A: 社群傳播版
```
🏷️【模型發布】OpenAI 發布 GPT-5 預覽版

💡GPT-5 性能大幅提升

摘要：準確率:95%, 速度:2x。這項技術突破將對產業產生重大影響。

關鍵洞察：
技術突破：5/5 分
實務影響：5/5 分
行動建議：4/5 分

創新實踐者反思：
→ 跨界連結：AI + 模型發布 領域
→ 實踐路徑：關注 OpenAI Blog 後續報導
→ 核心啟發：GPT-5 性能大幅提升
```

### 格式 B: APA 7 引用格式
```
OpenAI Blog. (2025, August 23). OpenAI 發布 GPT-5 預覽版. OpenAI Blog. https://openai.com/blog/gpt-5
```

### 格式 C: 視覺設計版
```
[模型發布]
[GPT-5 性能大幅提升]
```

## 🔧 進階配置

### 自定義新聞來源
編輯 `config/sources.yaml`：
```yaml
newsapi:
  enabled: true
  query: "artificial intelligence"
  language: "en"
  page_size: 50

rss:
  enabled: true
  feeds:
    - "https://feeds.feedburner.com/TechCrunch/"
    - "https://rss.cnn.com/rss/edition_technology.rss"
```

### 自定義 AI 提示詞
編輯 `config/prompts.yaml`：
```yaml
scoring_prompt: |
  你是一位專業的 AI 產業內容策展人。
  請對以下新聞進行評分...
```

## 🚨 故障排除

### 常見問題

**Q: API 配額限制錯誤**
```
A: 免費版 Gemini API 每分鐘限制 15 次請求
   解決方案：
   1. 等待 17 秒後重試
   2. 使用測試模式：python scripts/test_workflow.py
   3. 升級到付費版
```

**Q: 模組導入錯誤**
```
A: 確保已安裝所有依賴：
   pip install -r requirements.txt
```

**Q: 環境變數未設定**
```
A: 執行設定腳本：
   ./setup_env.sh
```

## 📈 效能優化

### API 配額管理
- 使用測試模式進行開發
- 分批處理大量新聞
- 設定適當的請求間隔

### 記憶體優化
- 限制同時處理的新聞數量
- 定期清理暫存檔案
- 使用串流處理大量資料

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 發起 Pull Request

## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援

- 問題回報：GitHub Issues
- 功能建議：GitHub Discussions
- 技術支援：建立 Issue 並標籤為 "support"

---

**🎉 開始使用 AI 新聞自動化系統，提升您的內容策展效率！**
