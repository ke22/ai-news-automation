#!/bin/bash

# 簡化版 AI 新聞自動化腳本
# 適合非技術團隊使用

echo "🚀 AI 新聞自動化系統"
echo "===================="

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

echo ""
echo "請選擇您要執行的功能："
echo "1. 全自動流程（快速產出）"
echo "2. 半自動流程（高品質內容）"
echo "3. 查看最新結果"
echo "4. 查看統計資訊"
echo "5. 退出"
echo ""

read -p "請輸入選項 (1-5): " choice

case $choice in
    1)
        echo "🔄 執行全自動流程..."
        echo "步驟 1/2: 收集新聞"
        python run.py collect
        echo "步驟 2/2: AI 處理與評分"
        python run.py process
        echo "✅ 全自動流程完成！"
        echo "📁 結果檔案位置: content/$(date +%Y/%m/%d)/"
        ;;
    2)
        echo "🔄 執行半自動流程..."
        echo "步驟 1/3: 收集新聞"
        python run.py collect
        echo "步驟 2/3: AI 初步評分"
        python run.py semi-auto
        echo "✅ 半自動流程完成！"
        echo "📁 結果檔案位置: content/$(date +%Y/%m/%d)/"
        ;;
    3)
        echo "📰 查看最新結果..."
        python view_results.py latest
        ;;
    4)
        echo "📊 查看統計資訊..."
        python view_results.py stats
        ;;
    5)
        echo "👋 再見！"
        exit 0
        ;;
    *)
        echo "❌ 無效選項，請重新選擇"
        ;;
esac

echo ""
echo "💡 提示："
echo "- 結果檔案會自動儲存在 content/ 資料夾中"
echo "- 如需查看詳細結果，請選擇選項 3"
echo "- 如需技術支援，請聯繫開發團隊"
