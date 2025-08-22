#!/usr/bin/env python
import os
import sys
import glob
from datetime import datetime, timezone, timedelta
from collections import Counter
from dateutil import parser as dtparser

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scripts.utils import write_json, read_json, to_display_date


def date_dirs_in_range(start, end):
    paths = []
    for y in glob.glob("data/*"):
        for m in glob.glob(f"{y}/*"):
            for d in glob.glob(f"{m}/*"):
                sel = os.path.join(d, "selected.json")
                if os.path.exists(sel):
                    try:
                        folder = d.replace("data/", "")
                        dt = dtparser.parse(folder.replace("/", "-")).date()
                        if start.date() <= dt <= end.date():
                            paths.append((dt, sel))
                    except Exception:
                        pass
    paths.sort()
    return paths


def main():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    trend = []
    latest = []
    topics = Counter()
    for dt, sel in date_dirs_in_range(start, now):
        items = read_json(sel, default=[])
        trend.append({"date": dt.isoformat(), "count": len(items)})
        for it in items:
            latest.append(
                {
                    "title": it["title"],
                    "url": it["url"],
                    "source": it.get("source", ""),
                    "date": to_display_date(it["published_at"]),
                }
            )
            for token in (it["title"] or "").lower().replace("-", " ").split():
                if token.isalpha() and len(token) >= 3:
                    topics[token] += 1
    hot_topics = topics.most_common(50)
    # write weekly and docs/api.json
    iso_week = now.strftime("%G-%V")
    write_json(
        f"analysis/weekly/{iso_week}.json",
        {
            "generated_at": now.isoformat(),
            "range": [start.isoformat(), now.isoformat()],
            "hot_topics": hot_topics,
            "trend": trend,
            "latest": latest[-50:],
        },
    )
    write_json(
        "docs/api.json",
        {
            "hot_topics": hot_topics[:20],
            "trend": trend,
            "latest": list(reversed(latest))[:50],
        },
    )
    print("✅ 週度分析完成，已更新分析與 dashboard API")


if __name__ == "__main__":
    main()
