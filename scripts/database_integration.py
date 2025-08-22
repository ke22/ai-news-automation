#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
資料庫整合模組
- Google Sheets 整合（格式 C → Figma）
- GitHub 資料庫整合（格式 A）
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from github import Github
from pathlib import Path
import sys

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import load_json


class GoogleSheetsIntegration:
    """Google Sheets 整合"""

    def __init__(self):
        self.credentials_file = "config/google_credentials.json"
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.worksheet_name = "AI_News_Format_C"

        if not self.spreadsheet_id:
            print("⚠️ GOOGLE_SHEETS_ID 未設定，跳過 Google Sheets 整合")
            return

        try:
            self._setup_credentials()
            self.client = gspread.authorize(self.credentials)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
            print("✅ Google Sheets 連接成功")
        except Exception as e:
            print(f"❌ Google Sheets 連接失敗: {e}")
            self.worksheet = None

    def _setup_credentials(self):
        """設定 Google API 憑證"""
        if not os.path.exists(self.credentials_file):
            print(f"⚠️ 憑證檔案不存在: {self.credentials_file}")
            print("💡 請從 Google Cloud Console 下載服務帳戶憑證")
            return

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        self.credentials = Credentials.from_service_account_file(
            self.credentials_file, scopes=scope
        )

    def update_format_c(self, format_c_content, date_str):
        """更新格式 C 到 Google Sheets"""
        if not self.worksheet:
            print("❌ Google Sheets 未連接")
            return False

        try:
            # 解析格式 C 內容
            lines = format_c_content.strip().split("\n")
            data = []

            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    category = lines[i].strip()
                    key_point = lines[i + 1].strip()
                    data.append([date_str, category, key_point])

            # 清除舊資料（保留標題行）
            self.worksheet.clear()

            # 寫入標題
            headers = ["日期", "類別", "精煉重點"]
            self.worksheet.append_row(headers)

            # 寫入資料
            for row in data:
                self.worksheet.append_row(row)

            print(f"✅ 格式 C 已更新到 Google Sheets")
            return True

        except Exception as e:
            print(f"❌ 更新 Google Sheets 失敗: {e}")
            return False


class GitHubIntegration:
    """GitHub 資料庫整合"""

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("GITHUB_REPO", "ai-news-database")
        self.branch = os.getenv("GITHUB_BRANCH", "main")

        if not self.github_token:
            print("⚠️ GITHUB_TOKEN 未設定，跳過 GitHub 整合")
            return

        try:
            self.github = Github(self.github_token)
            self.repo = self.github.get_repo(self.repo_name)
            print("✅ GitHub 連接成功")
        except Exception as e:
            print(f"❌ GitHub 連接失敗: {e}")
            self.repo = None

    def save_format_a(self, format_a_content, date_str):
        """儲存格式 A 到 GitHub"""
        if not self.repo:
            print("❌ GitHub 未連接")
            return False

        try:
            # 建立檔案路徑
            file_path = f"content/{date_str}/format_a_social_tw.md"

            # 建立提交訊息
            commit_message = f"Add AI news format A - {date_str}"

            # 檢查檔案是否已存在
            try:
                existing_file = self.repo.get_contents(file_path)
                # 更新現有檔案
                self.repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=format_a_content,
                    sha=existing_file.sha,
                    branch=self.branch,
                )
            except:
                # 建立新檔案
                self.repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=format_a_content,
                    branch=self.branch,
                )

            print(f"✅ 格式 A 已儲存到 GitHub: {file_path}")
            return True

        except Exception as e:
            print(f"❌ 儲存到 GitHub 失敗: {e}")
            return False

    def create_database_entry(self, news_data, date_str):
        """建立資料庫條目"""
        if not self.repo:
            return False

        try:
            # 建立 JSON 資料庫條目
            database_entry = {
                "date": date_str,
                "timestamp": date_str,
                "news_count": len(news_data),
                "news_items": news_data,
                "format": "social_media",
                "language": "zh-TW",
            }

            # 儲存到資料庫
            file_path = f"database/{date_str}/news_data.json"
            commit_message = f"Add news database entry - {date_str}"

            try:
                existing_file = self.repo.get_contents(file_path)
                self.repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=json.dumps(database_entry, ensure_ascii=False, indent=2),
                    sha=existing_file.sha,
                    branch=self.branch,
                )
            except:
                self.repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=json.dumps(database_entry, ensure_ascii=False, indent=2),
                    branch=self.branch,
                )

            print(f"✅ 資料庫條目已建立: {file_path}")
            return True

        except Exception as e:
            print(f"❌ 建立資料庫條目失敗: {e}")
            return False


class DatabaseManager:
    """資料庫管理器"""

    def __init__(self):
        self.sheets = GoogleSheetsIntegration()
        self.github = GitHubIntegration()

    def save_results(self, format_a, format_c, news_data, date_str):
        """儲存所有結果到資料庫"""
        print("🔄 儲存結果到資料庫...")

        # 儲存格式 A 到 GitHub
        if format_a:
            self.github.save_format_a(format_a, date_str)

        # 更新格式 C 到 Google Sheets
        if format_c:
            self.sheets.update_format_c(format_c, date_str)

        # 建立資料庫條目
        if news_data:
            self.github.create_database_entry(news_data, date_str)

        print("✅ 資料庫儲存完成")


def main():
    """測試函數"""
    manager = DatabaseManager()

    # 測試資料
    test_format_a = """# 測試格式 A
這是測試內容
"""

    test_format_c = """[模型發布]
[精煉重點測試]"""

    test_news_data = [{"title": "測試新聞", "category": "模型發布", "score": 4.5}]

    manager.save_results(test_format_a, test_format_c, test_news_data, "2025-08-22")


if __name__ == "__main__":
    main()
