#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
互動式 Web 介面
支援兩階段工作流程的人工操作
"""

import os
import sys
import json
import threading
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.two_stage_workflow import TwoStageWorkflow
from scripts.database_integration import DatabaseManager

app = Flask(__name__)

# 全域變數
workflow_status = {
    "stage": 1,
    "running": False,
    "candidates": [],
    "selected_items": [],
    "current_step": "",
    "progress": 0,
    "logs": [],
    "results": "",
}

workflow_instance = None
database_manager = None


@app.route("/")
def index():
    """主頁面"""
    return render_template("interactive_interface.html")


@app.route("/api/start_stage1", methods=["POST"])
def start_stage1():
    """開始階段 1"""
    global workflow_instance, workflow_status

    try:
        workflow_status["running"] = True
        workflow_status["stage"] = 1
        workflow_status["current_step"] = "階段 1: AI 挑選新聞"
        workflow_status["progress"] = 0
        workflow_status["logs"] = []

        # 在背景執行階段 1
        def run_stage1():
            try:
                workflow_instance = TwoStageWorkflow()
                success = workflow_instance.stage1_ai_selection()

                if success:
                    workflow_status["candidates"] = workflow_instance.candidates
                    workflow_status["stage"] = 1
                    workflow_status["current_step"] = "等待人工選擇"
                    workflow_status["progress"] = 100
                    workflow_status["logs"].append("✅ 階段 1 完成！請進行人工選擇")
                else:
                    workflow_status["current_step"] = "階段 1 失敗"
                    workflow_status["logs"].append("❌ 階段 1 執行失敗")

                workflow_status["running"] = False

            except Exception as e:
                workflow_status["current_step"] = "執行錯誤"
                workflow_status["logs"].append(f"❌ 錯誤: {e}")
                workflow_status["running"] = False

        thread = threading.Thread(target=run_stage1)
        thread.start()

        return jsonify({"status": "started", "message": "階段 1 已開始"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/process_commands", methods=["POST"])
def process_commands():
    """處理人工指令"""
    global workflow_instance, workflow_status

    try:
        data = request.get_json()
        commands = data.get("commands", [])

        if not workflow_instance:
            return jsonify({"status": "error", "message": "請先執行階段 1"})

        # 處理指令
        workflow_instance.process_manual_commands(commands)

        # 更新狀態
        workflow_status["selected_items"] = workflow_instance.selected_items

        return jsonify(
            {
                "status": "success",
                "message": f"已處理 {len(commands)} 個指令",
                "selected_count": len(workflow_instance.selected_items),
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/start_stage2", methods=["POST"])
def start_stage2():
    """開始階段 2"""
    global workflow_instance, workflow_status, database_manager

    try:
        if not workflow_instance or not workflow_instance.selected_items:
            return jsonify({"status": "error", "message": "請先選擇新聞項目"})

        workflow_status["running"] = True
        workflow_status["stage"] = 2
        workflow_status["current_step"] = "階段 2: AI 產出分析與格式"
        workflow_status["progress"] = 0
        workflow_status["logs"] = []

        # 在背景執行階段 2
        def run_stage2():
            try:
                # 生成三種格式
                format_a = workflow_instance._generate_format_a()
                format_b = workflow_instance._generate_format_b()
                format_c = workflow_instance._generate_format_c()

                # 儲存結果
                workflow_instance._save_results(format_a, format_b, format_c)

                # 儲存到資料庫
                database_manager = DatabaseManager()
                date_str = workflow_instance.today
                news_data = workflow_instance.selected_items

                database_manager.save_results(format_a, format_c, news_data, date_str)

                # 更新狀態
                workflow_status["stage"] = 2
                workflow_status["current_step"] = "完成"
                workflow_status["progress"] = 100
                workflow_status["logs"].append("✅ 階段 2 完成！")
                workflow_status["results"] = {
                    "format_a": format_a,
                    "format_b": format_b,
                    "format_c": format_c,
                }

                workflow_status["running"] = False

            except Exception as e:
                workflow_status["current_step"] = "階段 2 失敗"
                workflow_status["logs"].append(f"❌ 錯誤: {e}")
                workflow_status["running"] = False

        thread = threading.Thread(target=run_stage2)
        thread.start()

        return jsonify({"status": "started", "message": "階段 2 已開始"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/status")
def get_status():
    """取得狀態"""
    return jsonify(workflow_status)


@app.route("/api/candidates")
def get_candidates():
    """取得候選清單"""
    return jsonify(workflow_status["candidates"])


@app.route("/api/selected")
def get_selected():
    """取得已選擇項目"""
    return jsonify(workflow_status["selected_items"])


@app.route("/api/results")
def get_results():
    """取得結果"""
    return jsonify(workflow_status["results"])


@app.route("/api/download/<format_type>")
def download_result(format_type):
    """下載結果檔案"""
    try:
        if not workflow_instance:
            return jsonify({"status": "error", "message": "沒有可下載的結果"})

        output_dir = workflow_instance.output_dir

        if format_type == "format_a":
            file_path = output_dir / "format_a_social_tw.md"
        elif format_type == "format_b":
            file_path = output_dir / "format_b_apa_tw.md"
        elif format_type == "format_c":
            file_path = output_dir / "format_c_design_tw.txt"
        elif format_type == "full":
            file_path = output_dir / "full_result.md"
        else:
            return jsonify({"status": "error", "message": "無效的格式類型"})

        if not file_path.exists():
            return jsonify({"status": "error", "message": "檔案不存在"})

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def main():
    """主函數"""
    print("🌐 啟動互動式 Web 介面...")
    print("📱 請在瀏覽器中開啟: http://localhost:8081")
    print("💡 支援兩階段工作流程")

    app.run(host="0.0.0.0", port=8081, debug=True)


if __name__ == "__main__":
    main()
