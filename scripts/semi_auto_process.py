#!/usr/bin/env python
"""
半自動 AI 新聞處理系統
實現兩段式工作流：AI挑選 -> 人工篩選 -> AI產出
"""

import os
import sys
import json
from datetime import datetime, timezone
from dateutil import parser as dtparser

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scripts.utils import today_path, write_json, read_json, load_yaml, to_display_date


def load_articles():
    """載入原始新聞資料"""
    date_path = today_path()
    base = f"data/{date_path}"
    items = read_json(f"{base}/raw_news.json", default=[])
    return items


def ai_initial_scoring(items):
    """第一階段：AI 初步評分與分類"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未設定")
        return []

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        gen_model = genai.GenerativeModel(model)

        print("🤖 AI 正在進行初步評分與分類...")

        scored_items = []
        for i, item in enumerate(items[:20]):  # 限制前20篇
            prompt = f"""你是一位專業的 AI 產業內容策展人。

請對以下新聞進行評分與分類：

標題：{item['title']}
摘要：{item.get('summary', '')}
來源：{item.get('source', '')}
時間：{item.get('published_at', '')}

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

            response = gen_model.generate_content(
                prompt, generation_config=genai.types.GenerationConfig(temperature=0.2)
            )

            try:
                data = json.loads(response.text.strip())
                scored_item = {"id": i + 1, "original": item, "ai_analysis": data}
                scored_items.append(scored_item)
                print(f"✅ 已評分第 {i+1} 篇")
            except Exception as e:
                print(f"❌ 第 {i+1} 篇評分失敗: {e}")
                continue

        return scored_items

    except Exception as ex:
        print(f"❌ AI 評分失敗：{ex}")
        return []


def generate_candidate_board(scored_items):
    """生成候選看板"""
    print("\n📋 候選看板")
    print("=" * 80)
    print(
        f"{'#':<3} {'類別':<12} {'標題':<40} {'一句重點':<25} {'總分':<6} {'時效':<8} {'來源':<15}"
    )
    print("-" * 80)

    for item in scored_items:
        analysis = item["ai_analysis"]
        title = (
            item["original"]["title"][:35] + "..."
            if len(item["original"]["title"]) > 35
            else item["original"]["title"]
        )
        key_point = (
            analysis.get("key_point", "")[:20] + "..."
            if len(analysis.get("key_point", "")) > 20
            else analysis.get("key_point", "")
        )

        print(
            f"{item['id']:<3} {analysis.get('category', '')[:10]:<12} {title:<40} {key_point:<25} {analysis.get('total_score', 0):<6} {analysis.get('hours_ago', 0):<8} {item['original'].get('source', '')[:12]:<15}"
        )

    print("\n📝 操作指令：")
    print("#選擇 1 3 5 7 9（選擇指定編號的新聞）")
    print("#重搜 關鍵詞A,關鍵詞B（重新搜尋）")
    print("#過濾 類別=研究突破（按條件過濾）")
    print("#補證據 4（補充特定新聞的證據）")


def manual_selection_and_processing():
    """人工選擇與處理"""
    print("\n🎯 請輸入您的選擇指令：")
    print("範例：#選擇 1 3 5 7 9")

    # 這裡可以實現互動式選擇
    # 暫時返回預設選擇
    return [1, 3, 5, 7, 9]


def ai_final_analysis(selected_items):
    """第二階段：AI 最終分析與格式化"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未設定")
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        gen_model = genai.GenerativeModel(model)

        print("🤖 AI 正在進行最終分析與格式化...")

        # 準備選中的新聞資料
        selected_data = []
        for item in selected_items:
            selected_data.append(
                {
                    "title": item["original"]["title"],
                    "summary": item["original"].get("summary", ""),
                    "source": item["original"].get("source", ""),
                    "url": item["original"]["url"],
                    "published_at": item["original"]["published_at"],
                    "ai_analysis": item["ai_analysis"],
                }
            )

        # 生成格式A：社群傳播版
        format_a_prompt = f"""你是一位專業的 AI 產業內容策展人與創新實踐者。
請以繁體中文、時區 Asia/Taipei，為以下 {len(selected_data)} 則 AI 新聞產出【格式A：社群傳播版】。

新聞資料：
{json.dumps(selected_data, ensure_ascii=False, indent=2)}

請按照以下格式輸出：

🏷️【分類】新聞標題
💡一句話重點（≤20字）
摘要（120–150字）：核心事實 + 2–3關鍵訊息 + 影響範圍

關鍵洞察：
* 技術突破：X
* 實務影響：X
* 行動建議：X

創新實踐者反思：
→ 跨界連結：X
→ 實踐路徑：X
→ 核心啟發：X

---

📊 最後總結
【今日三大趨勢】：列3點（每點≤20字）
【金句洞察】：1句
【立即行動】：角色＋時間＋具體行動＋量化效果

使用 emoji 突出分類與亮點，語氣專業、簡潔，偏向產業觀點。"""

        response_a = gen_model.generate_content(
            format_a_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3),
        )

        # 生成格式B：APA引用格式
        format_b_prompt = f"""請為以下新聞生成【格式B：APA 7 引用格式】：

{json.dumps(selected_data, ensure_ascii=False, indent=2)}

格式：Author. (Year, Month Day). Title. Publisher/Source. URL"""

        response_b = gen_model.generate_content(
            format_b_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1),
        )

        # 生成格式C：視覺設計版
        format_c_prompt = f"""請為以下新聞生成【格式C：視覺設計版】：

{json.dumps(selected_data, ensure_ascii=False, indent=2)}

每則兩行：
第1行：[類別]
第2行：[精煉重點10–15字]"""

        response_c = gen_model.generate_content(
            format_c_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2),
        )

        return {
            "format_a": response_a.text.strip(),
            "format_b": response_b.text.strip(),
            "format_c": response_c.text.strip(),
        }

    except Exception as ex:
        print(f"❌ AI 最終分析失敗：{ex}")
        return None


def save_results(formats, selected_items):
    """儲存結果"""
    date_path = today_path()
    out_dir = f"content/{date_path}"
    os.makedirs(out_dir, exist_ok=True)

    # 儲存格式A：社群傳播版
    with open(f"{out_dir}/format_a_social_tw.md", "w", encoding="utf-8") as f:
        f.write(formats["format_a"])

    # 儲存格式B：APA引用格式
    with open(f"{out_dir}/format_b_apa_tw.md", "w", encoding="utf-8") as f:
        f.write(formats["format_b"])

    # 儲存格式C：視覺設計版
    with open(f"{out_dir}/format_c_design_tw.txt", "w", encoding="utf-8") as f:
        f.write(formats["format_c"])

    # 儲存選中的項目資料
    write_json(f"{out_dir}/selected_items.json", selected_items)

    print(f"✅ 結果已儲存至：{out_dir}/")


def main():
    print("🚀 半自動 AI 新聞處理系統")
    print("=" * 50)

    # 載入原始新聞
    items = load_articles()
    if not items:
        print("❌ 找不到原始資料，請先執行 collect.py")
        return

    print(f"📰 載入 {len(items)} 則新聞")

    # 第一階段：AI 初步評分
    scored_items = ai_initial_scoring(items)
    if not scored_items:
        print("❌ AI 評分失敗")
        return

    # 生成候選看板
    generate_candidate_board(scored_items)

    # 人工選擇（這裡可以實現互動式選擇）
    selected_ids = manual_selection_and_processing()
    selected_items = [item for item in scored_items if item["id"] in selected_ids]

    print(f"\n✅ 已選擇 {len(selected_items)} 則新聞")

    # 第二階段：AI 最終分析
    formats = ai_final_analysis(selected_items)
    if not formats:
        print("❌ AI 最終分析失敗")
        return

    # 儲存結果
    save_results(formats, selected_items)

    print("\n🎉 半自動處理完成！")
    print("📁 結果檔案：")
    print("   - format_a_social_tw.md（社群傳播版）")
    print("   - format_b_apa_tw.md（APA引用格式）")
    print("   - format_c_design_tw.txt（視覺設計版）")


if __name__ == "__main__":
    main()
