#!/usr/bin/env python
"""
Web 介面版本 - 適合非技術團隊使用
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import threading
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

app = Flask(__name__)

# 全域變數儲存執行狀態
execution_status = {
    "running": False,
    "current_step": "",
    "progress": 0,
    "logs": [],
    "results": None,
}


def run_command(command, step_name):
    """執行命令並更新狀態"""
    global execution_status

    execution_status["running"] = True
    execution_status["current_step"] = step_name
    execution_status["progress"] = 0
    execution_status["logs"] = []

    try:
        # 檢查 API 金鑰
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key or gemini_key == "your_actual_gemini_api_key_here":
            execution_status["logs"].append("❌ GEMINI_API_KEY 未設定或為預設值")
            execution_status["logs"].append("💡 請執行 ./setup_env.sh 設定 API 金鑰")
            execution_status["current_step"] = "API 金鑰未設定"
            execution_status["results"] = "請先設定 API 金鑰"
            execution_status["running"] = False
            return

        # 啟動虛擬環境並執行命令
        if os.name == "nt":  # Windows
            cmd = f"source .venv/Scripts/activate && python {command}"
        else:  # macOS/Linux
            cmd = f"source .venv/bin/activate && python {command}"

        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        # 即時讀取輸出
        for line in process.stdout:
            execution_status["logs"].append(line.strip())
            if len(execution_status["logs"]) > 50:  # 限制日誌數量
                execution_status["logs"] = execution_status["logs"][-50:]

        process.wait()

        if process.returncode == 0:
            execution_status["progress"] = 100
            execution_status["current_step"] = "完成"
            execution_status["results"] = "成功"
        else:
            execution_status["current_step"] = "失敗"
            execution_status["results"] = "執行失敗"

    except Exception as e:
        execution_status["current_step"] = "錯誤"
        execution_status["results"] = str(e)
    finally:
        execution_status["running"] = False


@app.route("/")
def index():
    """主頁面"""
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    """獲取執行狀態"""
    return jsonify(execution_status)


@app.route("/api/run", methods=["POST"])
def run_workflow():
    """執行工作流程"""
    data = request.get_json()
    workflow_type = data.get("type", "auto")

    if execution_status["running"]:
        return jsonify({"error": "已有任務正在執行"}), 400

    # 在新線程中執行命令
    if workflow_type == "auto":
        thread = threading.Thread(
            target=run_command, args=("run.py collect", "收集新聞")
        )
    elif workflow_type == "semi":
        thread = threading.Thread(
            target=run_command, args=("run.py semi-auto", "半自動處理")
        )
    else:
        return jsonify({"error": "無效的工作流程類型"}), 400

    thread.start()

    return jsonify({"message": "開始執行"})


@app.route("/api/results")
def get_results():
    """獲取最新結果"""
    try:
        # 找到最新的結果目錄
        content_dirs = []
        for root, dirs, files in os.walk("content"):
            for dir in dirs:
                if os.path.exists(os.path.join(root, dir, "format_a_social.md")):
                    content_dirs.append(os.path.join(root, dir))

        if not content_dirs:
            return jsonify({"error": "沒有找到結果"}), 404

        latest_dir = max(content_dirs, key=os.path.getctime)

        # 讀取結果檔案
        results = {}
        for filename in [
            "format_a_social.md",
            "format_b_apa.md",
            "format_c_design.txt",
        ]:
            filepath = os.path.join(latest_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    results[filename] = f.read()

        return jsonify({"directory": latest_dir, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<filename>")
def download_file(filename):
    """下載結果檔案"""
    try:
        # 找到最新的結果目錄
        content_dirs = []
        for root, dirs, files in os.walk("content"):
            for dir in dirs:
                if os.path.exists(os.path.join(root, dir, filename)):
                    content_dirs.append(os.path.join(root, dir))

        if not content_dirs:
            return jsonify({"error": "檔案不存在"}), 404

        latest_dir = max(content_dirs, key=os.path.getctime)
        filepath = os.path.join(latest_dir, filename)

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🌐 啟動 Web 介面...")
    print("📱 請在瀏覽器中開啟: http://localhost:8080")
    print("💡 適合非技術團隊使用")

    app.run(debug=True, host="0.0.0.0", port=8080)
