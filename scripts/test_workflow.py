#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡化版兩階段工作流程測試
避免 API 配額限制
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils import write_json


def create_mock_candidates():
    """創建模擬候選新聞"""
    candidates = []

    mock_news = [
        {
            "title": "OpenAI 發布 GPT-5 預覽版",
            "category": "模型發布",
            "key_point": "GPT-5 性能大幅提升",
            "key_data": "準確率:95%, 速度:2x",
            "tech_score": 5,
            "impact_score": 5,
            "practical_score": 4,
            "timely_score": 5,
            "total_score": 4.75,
            "hours_ago": "2",
            "source": "OpenAI Blog",
            "url": "https://openai.com/blog/gpt-5",
            "cluster_id": "cluster_1",
        },
        {
            "title": "Google 推出 Gemini Ultra 2.0",
            "category": "模型發布",
            "key_point": "多模態能力增強",
            "key_data": "參數:2T, 多語言:100+",
            "tech_score": 4,
            "impact_score": 4,
            "practical_score": 3,
            "timely_score": 4,
            "total_score": 3.75,
            "hours_ago": "4",
            "source": "Google AI",
            "url": "https://ai.google/gemini",
            "cluster_id": "cluster_2",
        },
        {
            "title": "Microsoft 投資 Anthropic 100億美元",
            "category": "重大融資",
            "key_point": "AI 巨頭投資戰升溫",
            "key_data": "投資額:100億美元, 估值:300億",
            "tech_score": 3,
            "impact_score": 5,
            "practical_score": 4,
            "timely_score": 5,
            "total_score": 4.25,
            "hours_ago": "6",
            "source": "TechCrunch",
            "url": "https://techcrunch.com/microsoft-anthropic",
            "cluster_id": "cluster_3",
        },
        {
            "title": "Meta 開源 Llama 3 模型",
            "category": "模型發布",
            "key_point": "開源 AI 模型競爭加劇",
            "key_data": "參數:70B, 開源:MIT許可",
            "tech_score": 4,
            "impact_score": 4,
            "practical_score": 5,
            "timely_score": 4,
            "total_score": 4.25,
            "hours_ago": "8",
            "source": "Meta AI",
            "url": "https://ai.meta.com/llama3",
            "cluster_id": "cluster_4",
        },
        {
            "title": "AI 在醫療診斷準確率達98%",
            "category": "研究突破",
            "key_point": "AI 醫療應用重大進展",
            "key_data": "準確率:98%, 疾病:50+種",
            "tech_score": 5,
            "impact_score": 5,
            "practical_score": 5,
            "timely_score": 4,
            "total_score": 4.75,
            "hours_ago": "12",
            "source": "Nature",
            "url": "https://nature.com/ai-medical",
            "cluster_id": "cluster_5",
        },
    ]

    for i, news in enumerate(mock_news):
        news["id"] = i + 1
        candidates.append(news)

    return candidates


def generate_candidate_board(candidates, date_str):
    """生成候選看板"""
    board = []
    board.append("# 候選看板")
    board.append(f"日期: {date_str}")
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
    for candidate in candidates:
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

    return "\n".join(board)


def generate_format_a(selected_items, date_str):
    """生成格式 A: 社群傳播版"""
    content = f"""# {date_str} #AI動態（近 24–48 小時）

"""

    for item in selected_items:
        content += f"""🏷️【{item['category']}】{item['title']}

💡{item['key_point']}

摘要：{item['key_data']}。這項技術突破將對產業產生重大影響，值得關注其後續發展。

關鍵洞察：
技術突破：{item['tech_score']}/5 分
實務影響：{item['impact_score']}/5 分
行動建議：{item['practical_score']}/5 分

創新實踐者反思：
→ 跨界連結：AI + {item['category']} 領域
→ 實踐路徑：關注 {item['source']} 後續報導
→ 核心啟發：{item['key_point']}

---

"""

    content += """📊 最後總結
【今日三大趨勢】：
1. 模型發布競爭激烈
2. 企業投資 AI 加速
3. 開源 AI 生態發展

【金句洞察】：AI 競爭力不在模型，而在場景。

【立即行動】：企業應於本週內啟動 AI 投資回報審查，半年內過濾 30% 無效專案。"""

    return content


def generate_format_b(selected_items):
    """生成格式 B: APA 7 引用格式"""
    content = "## APA 7 引用格式\n\n"

    for item in selected_items:
        content += f"{item['source']}. ({datetime.now().strftime('%Y, %B %d')}). {item['title']}. {item['source']}. {item['url']}\n\n"

    return content


def generate_format_c(selected_items):
    """生成格式 C: 視覺設計版"""
    content = "## 視覺設計版\n\n"

    for item in selected_items:
        content += f"[{item['category']}]\n"
        content += f"[{item['key_point'][:15]}]\n\n"

    return content


def main():
    """主函數"""
    print("🚀 簡化版兩階段工作流程測試")

    # 設定時區
    tz = timezone(timedelta(hours=8))  # Asia/Taipei
    today = datetime.now(tz).strftime("%Y-%m-%d")

    # 建立輸出目錄
    output_dir = Path(f"content/{datetime.now(tz).strftime('%Y/%m/%d')}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📅 日期: {today}")
    print("=" * 50)

    # 階段 1: 生成候選看板
    print("🔄 階段 1: 生成候選看板...")
    candidates = create_mock_candidates()

    # 生成候選看板
    board_content = generate_candidate_board(candidates, today)
    board_file = output_dir / "candidate_board.md"
    with open(board_file, "w", encoding="utf-8") as f:
        f.write(board_content)

    print(f"📋 候選看板已儲存: {board_file}")

    # 儲存候選資料
    candidates_file = output_dir / "candidates.json"
    write_json(str(candidates_file), candidates)

    print("✅ 階段 1 完成！")

    # 模擬人工選擇
    print("🔄 處理人工選擇...")
    selected_ids = [1, 2, 3, 4, 5]  # 選擇前5則
    selected_items = [c for c in candidates if c["id"] in selected_ids]
    print(f"✅ 已選擇 {len(selected_items)} 則新聞")

    # 階段 2: 生成三種格式
    print("🔄 階段 2: 生成三種格式...")

    format_a = generate_format_a(selected_items, today)
    format_b = generate_format_b(selected_items)
    format_c = generate_format_c(selected_items)

    # 儲存結果
    format_a_file = output_dir / "format_a_social_tw.md"
    with open(format_a_file, "w", encoding="utf-8") as f:
        f.write(format_a)

    format_b_file = output_dir / "format_b_apa_tw.md"
    with open(format_b_file, "w", encoding="utf-8") as f:
        f.write(format_b)

    format_c_file = output_dir / "format_c_design_tw.txt"
    with open(format_c_file, "w", encoding="utf-8") as f:
        f.write(format_c)

    # 完整結果
    full_result = f"""# AI 新聞自動化結果
日期: {today}

## 格式 A: 社群傳播版
{format_a}

---

## 格式 B: APA 7 引用格式
{format_b}

---

## 格式 C: 視覺設計版
{format_c}
"""

    full_result_file = output_dir / "full_result.md"
    with open(full_result_file, "w", encoding="utf-8") as f:
        f.write(full_result)

    print(f"📁 結果已儲存到: {output_dir}")
    print("✅ 階段 2 完成！")
    print("🎉 完整工作流程完成！")


if __name__ == "__main__":
    main()
