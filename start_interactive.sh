#!/bin/bash

# 互動式 Web 介面啟動腳本
# 支援兩階段工作流程

echo "🌐 AI 新聞自動化系統 - 互動式介面"
echo "=================================="

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "📦 正在設置環境..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    echo "✅ 環境設置完成"
else
    echo "✅ 環境已就緒"
fi

# 啟動虛擬環境
source .venv/bin/activate

# 檢查 API 金鑰
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_actual_gemini_api_key_here" ]; then
    echo "❌ GEMINI_API_KEY 未設定"
    echo "💡 請執行 ./setup_env.sh 設定 API 金鑰"
    exit 1
fi

echo ""
echo "🚀 啟動互動式 Web 介面..."
echo "📱 請在瀏覽器中開啟: http://localhost:8081"
echo "💡 支援兩階段工作流程"
echo "💡 按 Ctrl+C 停止服務"
echo ""

# 啟動互動式 Web 介面
python scripts/interactive_web_interface.py
