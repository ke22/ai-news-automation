#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
兩階段 AI 新聞工作流程
階段 1: AI 挑選新聞 → 候選清單
階段 2: 人工選擇 → AI 產出分析與格式
"""

import os
import sys
import json
import yaml
import pandas as pd
from datetime import datetime, timezone, timedelta
import google.generativeai as genai
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# 直接實現收集新聞功能
def collect_news():
    """收集新聞的簡化版本"""
    import os
    import requests
    import feedparser
    from datetime import datetime, timezone
    from urllib.parse import urlencode

    articles = []

    # NewsAPI
    api_key = os.getenv("NEWS_API_KEY")
    if api_key:
        try:
            params = {
                "q": "artificial intelligence",
                "language": "en",
                "pageSize": 50,
                "sortBy": "publishedAt",
            }
            url = "https://newsapi.org/v2/everything?" + urlencode(params)
            headers = {"X-Api-Key": api_key}
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()

            for a in data.get("articles", []):
                articles.append(
                    {
                        "title": a.get("title", ""),
                        "url": a.get("url", ""),
                        "published_at": a.get("publishedAt", ""),
                        "source": (a.get("source") or {}).get("name", "NewsAPI"),
                        "summary": a.get("description") or "",
                    }
                )
            print(f"NewsAPI 取得 {len(articles)} 則")
        except Exception as e:
            print(f"NewsAPI 錯誤: {e}")

    # RSS 來源
    rss_feeds = [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://rss.cnn.com/rss/edition_technology.rss",
    ]

    for url in rss_feeds:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:10]:  # 限制每個來源10則
                articles.append(
                    {
                        "title": getattr(e, "title", ""),
                        "url": getattr(e, "link", ""),
                        "published_at": getattr(
                            e, "published", getattr(e, "updated", "")
                        ),
                        "source": d.feed.get("title", "RSS"),
                        "summary": getattr(e, "summary", ""),
                    }
                )
        except Exception as e:
            print(f"RSS 錯誤 {url}: {e}")

    print(f"總共收集 {len(articles)} 則新聞")
    return articles


from scripts.utils import load_yaml, write_json, read_json


class TwoStageWorkflow:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未設定")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        )

        # 載入配置
        self.config = load_yaml("config/sources.yaml")
        self.prompts = load_yaml("config/prompts.yaml")

        # 設定時區
        self.tz = timezone(timedelta(hours=8))  # Asia/Taipei
        self.today = datetime.now(self.tz).strftime("%Y-%m-%d")

        # 建立輸出目錄
        self.output_dir = Path(f"content/{datetime.now(self.tz).strftime('%Y/%m/%d')}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 工作狀態
        self.stage = 1
        self.candidates = []
        self.selected_items = []

    def stage1_ai_selection(self):
        """階段 1: AI 挑選新聞 → 候選清單"""
        print("🔄 階段 1: AI 挑選新聞...")

        # 收集新聞
        print("📰 收集新聞中...")
        articles = collect_news()

        if not articles:
            print("❌ 沒有收集到新聞")
            return False

        print(f"✅ 收集到 {len(articles)} 則新聞")

        # AI 初步評分與分類
        print("🤖 AI 評分與分類中...")
        self.candidates = self._ai_initial_scoring(articles)

        # 生成候選看板
        print("📊 生成候選看板...")
        self._generate_candidate_board()

        print("✅ 階段 1 完成！")
        print("📋 候選看板已生成，請進行人工選擇")
        return True

    def _ai_initial_scoring(self, articles):
        """AI 初步評分與分類"""
        candidates = []

        for i, article in enumerate(articles[:20]):  # 限制前20則
            try:
                prompt = f"""你是一位專業的 AI 產業內容策展人與創新實踐者。

請以 繁體中文、時區 Asia/Taipei，依 [今天日期：{self.today}] 對以下新聞進行評分與分類：

標題：{article['title']}
摘要：{article.get('summary', '')}
來源：{article.get('source', '')}
時間：{article.get('published_at', '')}
URL：{article.get('url', '')}

請輸出 JSON 格式：
{{
    "category": "模型發布/AI開發工具/企業應用/重大融資/研究突破",
    "key_point": "一句重點（≤30字）",
    "key_data": "關鍵數據（最多3個「指標:數值」；缺則寫「—」）",
    "tech_score": 0-5,
    "impact_score": 0-5,
    "practical_score": 0-5,
    "timely_score": 0-5,
    "total_score": "四項加權求和，保留1位小數",
    "hours_ago": "距今幾小時",
    "cluster_id": "同題相同ID（如果與其他新聞相同）"
}}"""

                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=0.2),
                )

                data = json.loads(response.text.strip())

                candidate = {
                    "id": i + 1,
                    "title": article["title"],
                    "summary": article.get("summary", ""),
                    "source": article.get("source", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("published_at", ""),
                    "category": data.get("category", "其他"),
                    "key_point": data.get("key_point", ""),
                    "key_data": data.get("key_data", "—"),
                    "tech_score": data.get("tech_score", 0),
                    "impact_score": data.get("impact_score", 0),
                    "practical_score": data.get("practical_score", 0),
                    "timely_score": data.get("timely_score", 0),
                    "total_score": float(data.get("total_score", 0)),
                    "hours_ago": data.get("hours_ago", ""),
                    "cluster_id": data.get("cluster_id", f"cluster_{i}"),
                }

                candidates.append(candidate)

            except Exception as e:
                print(f"⚠️ 處理新聞 {i+1} 時出錯: {e}")
                continue

        # 按總分排序
        candidates.sort(key=lambda x: x["total_score"], reverse=True)

        # 重新分配 ID
        for i, candidate in enumerate(candidates):
            candidate["id"] = i + 1

        return candidates

    def _generate_candidate_board(self):
        """生成候選看板"""
        if not self.candidates:
            return

        # 建立 DataFrame
        df = pd.DataFrame(self.candidates)

        # 生成表格格式
        board = []
        board.append("# 候選看板")
        board.append(f"日期: {self.today}")
        board.append("")

        # 表頭
        headers = [
            "#",
            "類別",
            "標題",
            "一句重點",
            "關鍵數據",
            "技術",
            "影響",
            "實戰",
            "時效",
            "總分",
            "時效",
            "來源",
            "URL",
            "ClusterID",
        ]
        board.append("| " + " | ".join(headers) + " |")
        board.append("|" + "|".join(["---"] * len(headers)) + "|")

        # 資料行
        for candidate in self.candidates:
            row = [
                str(candidate["id"]),
                candidate["category"],
                (
                    candidate["title"][:70] + "..."
                    if len(candidate["title"]) > 70
                    else candidate["title"]
                ),
                (
                    candidate["key_point"][:30] + "..."
                    if len(candidate["key_point"]) > 30
                    else candidate["key_point"]
                ),
                candidate["key_data"],
                str(candidate["tech_score"]),
                str(candidate["impact_score"]),
                str(candidate["practical_score"]),
                str(candidate["timely_score"]),
                f"{candidate['total_score']:.1f}",
                candidate["hours_ago"],
                candidate["source"],
                candidate["url"],
                candidate["cluster_id"],
            ]
            board.append("| " + " | ".join(row) + " |")

        # 去重說明
        board.append("")
        board.append("## 去重說明")
        clusters = {}
        for candidate in self.candidates:
            cluster_id = candidate["cluster_id"]
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(f"{candidate['id']}: {candidate['source']}")

        for cluster_id, sources in clusters.items():
            if len(sources) > 1:
                board.append(f"- **{cluster_id}**: {', '.join(sources)}")

        # 缺料建議
        if len(self.candidates) < 12:
            board.append("")
            board.append("## 缺料建議")
            board.append("建議擴充以下關鍵詞或來源：")
            board.append("- 模型發布：OpenAI、Anthropic、Google、Meta 官方")
            board.append("- 開發工具：GitHub、Cursor、VS Code")
            board.append("- 企業應用：Microsoft、Google Cloud、AWS")
            board.append("- 研究：Nature、Science、arXiv")

        # 儲存候選看板
        board_content = "\n".join(board)
        board_file = self.output_dir / "candidate_board.md"
        with open(board_file, "w", encoding="utf-8") as f:
            f.write(board_content)

        print(f"📋 候選看板已儲存: {board_file}")

        # 儲存 JSON 資料
        candidates_file = self.output_dir / "candidates.json"
        write_json(str(candidates_file), self.candidates)

        return board_content

    def process_manual_commands(self, commands):
        """處理人工指令"""
        print("🔄 處理人工指令...")

        for command in commands:
            if command.startswith("#選擇"):
                self._process_selection(command)
            elif command.startswith("#重搜"):
                self._process_research(command)
            elif command.startswith("#過濾"):
                self._process_filter(command)
            elif command.startswith("#合併"):
                self._process_merge(command)
            elif command.startswith("#補證據"):
                self._process_evidence(command)
            elif command.startswith("#改分類"):
                self._process_category_change(command)

        print("✅ 人工指令處理完成")

    def _process_selection(self, command):
        """處理選擇指令 #選擇 2 5 7 9 12"""
        try:
            ids = [int(x) for x in command.split()[1:]]
            self.selected_items = [c for c in self.candidates if c["id"] in ids]
            print(f"✅ 已選擇 {len(self.selected_items)} 則新聞")
        except Exception as e:
            print(f"❌ 選擇指令處理失敗: {e}")

    def _process_research(self, command):
        """處理重搜指令 #重搜 關鍵詞A, 關鍵詞B"""
        # 這裡可以實現重新搜尋邏輯
        print("🔄 重新搜尋功能待實現")

    def _process_filter(self, command):
        """處理過濾指令 #過濾 類別=研究突破, 來源≠路邊媒體"""
        # 這裡可以實現過濾邏輯
        print("🔄 過濾功能待實現")

    def _process_merge(self, command):
        """處理合併指令 #合併 3 8"""
        # 這裡可以實現合併邏輯
        print("🔄 合併功能待實現")

    def _process_evidence(self, command):
        """處理補證據指令 #補證據 4"""
        # 這裡可以實現補充證據邏輯
        print("🔄 補證據功能待實現")

    def _process_category_change(self, command):
        """處理改分類指令 #改分類 6=企業應用"""
        # 這裡可以實現分類修改邏輯
        print("🔄 改分類功能待實現")

    def stage2_ai_analysis(self):
        """階段 2: AI 產出分析與格式"""
        if not self.selected_items:
            print("❌ 沒有選擇的新聞項目")
            return False

        print("🔄 階段 2: AI 產出分析與格式...")

        # 生成三種格式
        format_a = self._generate_format_a()
        format_b = self._generate_format_b()
        format_c = self._generate_format_c()

        # 儲存結果
        self._save_results(format_a, format_b, format_c)

        print("✅ 階段 2 完成！")
        return True

    def _generate_format_a(self):
        """生成格式 A: 社群傳播版"""
        prompt = f"""你是一位專業的 AI 產業內容策展人與創新實踐者。

請以 繁體中文、時區 Asia/Taipei，依 [今天日期：{self.today}] 為以下選中的新聞生成【格式A：社群傳播版】：

{json.dumps(self.selected_items, ensure_ascii=False, indent=2)}

請按照以下結構輸出：

【格式A：社群傳播版】

{self._get_format_a_structure()}

格式要求：
- 使用 emoji 突出分類與亮點
- 語氣專業、簡潔，偏向產業觀點
- 不要贅述背景故事，聚焦「新 → 有數據 → 有行動」
- 每篇新聞都要有完整的結構"""

        response = self.model.generate_content(
            prompt, generation_config=genai.types.GenerationConfig(temperature=0.3)
        )

        return response.text.strip()

    def _get_format_a_structure(self):
        """取得格式 A 的結構模板"""
        return """🏷️【分類】新聞標題

💡一句話重點（≤20 字）

摘要（120–150 字）：核心事實 + 2–3 關鍵訊息 + 影響範圍

關鍵洞察：
技術突破：X
實務影響：X
行動建議：X

創新實踐者反思：
→ 跨界連結：X
→ 實踐路徑：X
→ 核心啟發：X

---

📊 最後總結
【今日三大趨勢】：列 3 點（每點 ≤20 字）
【金句洞察】：1 句
【立即行動】：角色＋時間＋具體行動＋量化效果"""

    def _generate_format_b(self):
        """生成格式 B: APA 7 引用格式"""
        prompt = f"""請為以下新聞生成【格式B：APA 7 引用格式】：

{json.dumps(self.selected_items, ensure_ascii=False, indent=2)}

請輸出 5 條 APA 7 格式的引用，格式如下：
Author. (Year, Month Day). Title. Publisher/Source. URL

每條都必須包含 URL。"""

        response = self.model.generate_content(
            prompt, generation_config=genai.types.GenerationConfig(temperature=0.1)
        )

        return response.text.strip()

    def _generate_format_c(self):
        """生成格式 C: 視覺設計版"""
        prompt = f"""請為以下新聞生成【格式C：視覺設計版】：

{json.dumps(self.selected_items, ensure_ascii=False, indent=2)}

每則兩行：
第 1 行：[類別]
第 2 行：[精煉重點 10–15 字]

請輸出 5 則，每則用換行分隔。"""

        response = self.model.generate_content(
            prompt, generation_config=genai.types.GenerationConfig(temperature=0.2)
        )

        return response.text.strip()

    def _save_results(self, format_a, format_b, format_c):
        """儲存結果"""
        # 儲存格式 A
        format_a_file = self.output_dir / "format_a_social_tw.md"
        with open(format_a_file, "w", encoding="utf-8") as f:
            f.write(format_a)

        # 儲存格式 B
        format_b_file = self.output_dir / "format_b_apa_tw.md"
        with open(format_b_file, "w", encoding="utf-8") as f:
            f.write(format_b)

        # 儲存格式 C
        format_c_file = self.output_dir / "format_c_design_tw.txt"
        with open(format_c_file, "w", encoding="utf-8") as f:
            f.write(format_c)

        # 儲存完整結果
        full_result = f"""# AI 新聞自動化結果
日期: {self.today}

## 格式 A: 社群傳播版
{format_a}

---

## 格式 B: APA 7 引用格式
{format_b}

---

## 格式 C: 視覺設計版
{format_c}
"""

        full_result_file = self.output_dir / "full_result.md"
        with open(full_result_file, "w", encoding="utf-8") as f:
            f.write(full_result)

        print(f"📁 結果已儲存到: {self.output_dir}")

    def run_full_workflow(self, manual_commands=None):
        """執行完整工作流程"""
        print("🚀 開始兩階段 AI 新聞工作流程")
        print(f"📅 日期: {self.today}")
        print("=" * 50)

        # 階段 1
        if not self.stage1_ai_selection():
            return False

        # 等待人工指令
        if manual_commands:
            self.process_manual_commands(manual_commands)
        else:
            print("⏳ 等待人工指令...")
            print("💡 您可以輸入以下指令：")
            print("  #選擇 2 5 7 9 12")
            print("  #重搜 關鍵詞A, 關鍵詞B")
            print("  #過濾 類別=研究突破")
            print("  #合併 3 8")
            print("  #補證據 4")
            print("  #改分類 6=企業應用")
            return True  # 等待人工輸入

        # 階段 2
        if self.stage2_ai_analysis():
            print("🎉 完整工作流程完成！")
            return True

        return False


def main():
    """主函數"""
    try:
        workflow = TwoStageWorkflow()

        # 檢查是否有命令行參數（人工指令）
        if len(sys.argv) > 1:
            commands = sys.argv[1:]
            workflow.run_full_workflow(commands)
        else:
            # 互動模式
            workflow.run_full_workflow()

    except Exception as e:
        print(f"❌ 工作流程執行失敗: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
