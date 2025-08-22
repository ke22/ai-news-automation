#!/bin/bash

# 完整兩階段工作流程啟動腳本
# AI挑選新聞 -> 人工選擇調整 -> AI產出格式 -> 資料庫儲存

echo "🚀 AI 新聞自動化系統 - 完整兩階段工作流程"
echo "=========================================="

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
echo "🎯 選擇工作模式："
echo "1. 互動式 Web 介面（推薦）"
echo "2. 命令行模式"
echo "3. 測試模式（模擬資料）"
echo "4. 退出"
echo ""

read -p "請選擇模式 (1-4): " choice

case $choice in
    1)
        echo "🌐 啟動互動式 Web 介面..."
        echo "📱 請在瀏覽器中開啟: http://localhost:8081"
        echo "💡 支援完整的兩階段工作流程"
        python scripts/interactive_web_interface.py
        ;;
    2)
        echo "🖥️ 啟動命令行模式..."
        echo "💡 使用以下命令："
        echo "  python run.py two-stage"
        echo "  python run.py two-stage '#選擇 1 2 3 4 5'"
        echo ""
        echo "🚀 開始執行..."
        python run.py two-stage
        ;;
    3)
        echo "🧪 啟動測試模式..."
        echo "💡 使用模擬資料，避免 API 配額限制"
        python scripts/test_workflow.py
        ;;
    4)
        echo "👋 再見！"
        exit 0
        ;;
    *)
        echo "❌ 無效選項，請重新選擇"
        exit 1
        ;;
esac

echo ""
echo "✅ 工作流程完成！"
echo "📁 結果檔案位置: content/$(date +%Y/%m/%d)/"
