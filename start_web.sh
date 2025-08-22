#!/bin/bash

# Web 介面啟動腳本
# 適合非技術團隊使用

echo "🌐 AI 新聞自動化系統 - Web 介面"
echo "================================"

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

# 檢查 Flask 是否已安裝
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 安裝 Flask..."
    pip install flask
fi

echo ""
echo "🚀 啟動 Web 介面..."
echo "📱 請在瀏覽器中開啟: http://localhost:8080"
echo "💡 按 Ctrl+C 停止服務"
echo ""

# 啟動 Web 介面
python web_interface.py
