#!/bin/bash

# 環境變數設定腳本
# 適合非技術團隊使用

echo "🔑 AI 新聞自動化系統 - API 金鑰設定"
echo "===================================="

# 檢查是否已有設定
if [ ! -z "$GEMINI_API_KEY" ] && [ "$GEMINI_API_KEY" != "your_actual_gemini_api_key_here" ]; then
    echo "✅ GEMINI_API_KEY 已設定"
else
    echo "❌ GEMINI_API_KEY 未設定"
fi

if [ ! -z "$NEWS_API_KEY" ] && [ "$NEWS_API_KEY" != "test_key_123" ]; then
    echo "✅ NEWS_API_KEY 已設定"
else
    echo "❌ NEWS_API_KEY 未設定或為測試值"
fi

echo ""
echo "📝 請輸入您的 API 金鑰："
echo ""

# 設定 Gemini API 金鑰
read -p "請輸入您的 GEMINI_API_KEY: " gemini_key
if [ ! -z "$gemini_key" ]; then
    export GEMINI_API_KEY="$gemini_key"
    echo "✅ GEMINI_API_KEY 已設定"
else
    echo "⚠️ 跳過 GEMINI_API_KEY 設定"
fi

echo ""

# 設定 News API 金鑰
read -p "請輸入您的 NEWS_API_KEY (可選): " news_key
if [ ! -z "$news_key" ]; then
    export NEWS_API_KEY="$news_key"
    echo "✅ NEWS_API_KEY 已設定"
else
    echo "⚠️ 跳過 NEWS_API_KEY 設定"
fi

echo ""
echo "🔧 將設定寫入 shell 配置檔案..."

# 檢測 shell 類型
if [ -n "$ZSH_VERSION" ]; then
    config_file="$HOME/.zshrc"
    echo "檢測到 Zsh，使用 $config_file"
elif [ -n "$BASH_VERSION" ]; then
    config_file="$HOME/.bashrc"
    echo "檢測到 Bash，使用 $config_file"
else
    config_file="$HOME/.profile"
    echo "使用 $config_file"
fi

# 寫入配置檔案
echo "" >> "$config_file"
echo "# AI 新聞自動化系統環境變數" >> "$config_file"
if [ ! -z "$gemini_key" ]; then
    echo "export GEMINI_API_KEY=\"$gemini_key\"" >> "$config_file"
fi
if [ ! -z "$news_key" ]; then
    echo "export NEWS_API_KEY=\"$news_key\"" >> "$config_file"
fi

echo ""
echo "✅ 設定完成！"
echo ""
echo "💡 提示："
echo "- 設定已保存到 $config_file"
echo "- 重新開啟終端機或執行 'source $config_file' 使設定生效"
echo "- 您現在可以啟動 Web 介面了"
echo ""
echo "🚀 啟動 Web 介面："
echo "./start_web.sh"
