#!/usr/bin/env python
import os, json
from datetime import datetime, timezone, timedelta
from dateutil import parser as dtparser
from scripts.utils import today_path, write_json, read_json, load_yaml, to_display_date

def rule_score(item):
    kw = load_yaml("config/keywords.yaml")
    title = (item.get("title") or "").lower()
    summary = (item.get("summary") or "").lower()
    text = f"{title} {summary}"
    score = 0
    for k in kw["weights"]["technical_breakthrough"]:
        if k.lower() in text: score += 10
    for k in kw["weights"]["industry_impact"]:
        if k.lower() in text: score += 8
    for k in kw["weights"]["practical_value"]:
        if k.lower() in text: score += 7
    try:
        pub = dtparser.parse(item["published_at"]).replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - pub).days
        score += max(0, 5 - age)
    except Exception:
        score += 1
    boosts = [b.lower() for b in kw.get("boost_publishers",[])]
    if any(b in (item.get("source","").lower()) for b in boosts): score += 2
    return score

def ai_refine(items):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: return [None]*len(items)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL","gpt-4o-mini")
        refined = []
        for it in items:
            sys = "你將只輸出 JSON，且內容極簡。"
            user = f'''請針對下列 AI 新聞依規則給出 1~5 分四項評分（tech/impact/practical/timely）：
標題：{it['title']}
摘要：{it.get('summary','')}
來源：{it.get('source','')}
時間：{it.get('published_at','')}
輸出 JSON：{{"tech":x,"impact":x,"practical":x,"timely":x}}'''
            res = client.chat.completions.create(model=model, messages=[{"role":"system","content":sys},{"role":"user","content":user}], temperature=0.2)
            content = res.choices[0].message.content.strip()
            try:
                data = json.loads(content)
                s = int(data.get("tech",0))+int(data.get("impact",0))+int(data.get("practical",0))+int(data.get("timely",0))
                refined.append(s)
            except Exception:
                refined.append(None)
        return refined
    except Exception as ex:
        print("OpenAI 失敗：", ex)
        return [None]*len(items)

def generate_formats(selected):
    lines = ["# 🔥 今日精選 AI 新聞（Top 20）"]
    for i, it in enumerate(selected, 1):
        date = to_display_date(it["published_at"])
        lines.append(f"- **{i}. {it['title']}**  \n  {it.get('summary','')[:160]}...  \n  {date}｜{it.get('source','')}｜[連結]({it['url']}) #AI #Tech")
    fmt_a = "\n".join(lines)
    lines = ["# 📚 APA 近似引用彙整（Top 20）"]
    for it in selected:
        date = to_display_date(it["published_at"])
        lines.append(f"- {it.get('source','未知機構')}（{date[:4]}）。{it['title']}。取自 {it['url']}")
    fmt_b = "\n".join(lines)
    lines = []
    for it in selected:
        date = to_display_date(it["published_at"])
        lines.append(f"{it['title']}｜AI, Tech｜{it.get('source','')}｜{date}｜{it['url']}")
    fmt_c = "\n".join(lines)
    return fmt_a, fmt_b, fmt_c

def main():
    date_path = today_path()
    base = f"data/{date_path}"
    items = read_json(f"{base}/raw_news.json", default=[])
    if not items:
        print("❗找不到原始資料，請先執行 collect.py"); return
    scored = [(rule_score(it), it) for it in items]
    refined = ai_refine([it for _, it in scored])
    for idx, (s, it) in enumerate(scored):
        if refined[idx] is not None:
            s = int(round(0.6*s + 0.8*refined[idx]))
        scored[idx] = (s, it)
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [it for _, it in scored[:20]]
    write_json(f"{base}/selected.json", top)
    fmt_a, fmt_b, fmt_c = generate_formats(top)
    out_dir = f"content/{date_path}"; os.makedirs(out_dir, exist_ok=True)
    open(f"{out_dir}/format_a_social.md","w",encoding="utf-8").write(fmt_a)
    open(f"{out_dir}/format_b_apa.md","w",encoding="utf-8").write(fmt_b)
    open(f"{out_dir}/format_c_design.txt","w",encoding="utf-8").write(fmt_c)
    print(f"✅ 已輸出 Top20 與三種格式：content/{date_path}")

if __name__ == "__main__":
    main()