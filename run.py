#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 新聞自動化系統 - 主執行器
支援多種工作流程
"""

import sys
import subprocess
from pathlib import Path

# 腳本映射
SCRIPTS = {
    "collect": "scripts/collect.py",
    "process": "scripts/process.py",
    "semi-auto": "scripts/semi_auto_process.py",
    "two-stage": "scripts/two_stage_workflow.py",
    "interactive": "scripts/interactive_web_interface.py",
    "publish": "scripts/publish.py",
    "analyze": "scripts/analyze.py",
    "database": "scripts/database_integration.py",
}


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("🚀 AI 新聞自動化系統")
        print("=" * 30)
        print("可用命令：")
        print("  collect      - 收集新聞")
        print("  process      - AI 處理與評分")
        print("  semi-auto    - 半自動流程")
        print("  two-stage    - 兩階段工作流程")
        print("  interactive  - 互動式 Web 介面")
        print("  publish      - 發布內容")
        print("  analyze      - 分析統計")
        print("  database     - 資料庫整合測試")
        print("")
        print("範例：")
        print("  python run.py collect")
        print("  python run.py two-stage")
        print("  python run.py interactive")
        return 1

    command = sys.argv[1]

    if command not in SCRIPTS:
        print(f"❌ 未知命令: {command}")
        print("💡 使用 'python run.py' 查看可用命令")
        return 1

    script_path = SCRIPTS[command]

    if not Path(script_path).exists():
        print(f"❌ 腳本不存在: {script_path}")
        return 1

    print(f"🚀 執行: {command}")
    print(f"📁 腳本: {script_path}")
    print("=" * 30)

    try:
        # 執行腳本
        result = subprocess.run([sys.executable, script_path] + sys.argv[2:])
        return result.returncode
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
