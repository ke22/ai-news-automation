#!/usr/bin/env python
import os, requests, feedparser
from datetime import datetime, timezone
from urllib.parse import urlencode
from scripts.utils import today_path, write_json, normalize_article, load_yaml

def fetch_newsapi(cfg):
    if not cfg.get("enabled", False): return []
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("NEWS_API_KEY 未設定，跳過 NewsAPI。")
        return []
    params = {"q": cfg.get("query","artificial intelligence"), "language": cfg.get("language","en"), "pageSize": int(cfg.get("page_size", 50)), "sortBy":"publishedAt"}
    url = "https://newsapi.org/v2/everything?" + urlencode(params)
    headers = {"X-Api-Key": api_key}
    r = requests.get(url, headers=headers, timeout=30); r.raise_for_status()
    data = r.json()
    arts = []
    for a in data.get("articles", []):
        arts.append(normalize_article(a.get("title"), a.get("url"), a.get("publishedAt"), (a.get("source") or {}).get("name","NewsAPI"), a.get("description") or ""))
    print(f"NewsAPI 取得 {len(arts)} 則")
    return arts

def fetch_rss(cfg):
    if not cfg.get("enabled", False): return []
    out = []
    for url in cfg.get("feeds", []):
        try:
            d = feedparser.parse(url)
            for e in d.entries:
                out.append(normalize_article(getattr(e,"title",""), getattr(e,"link",""), getattr(e,"published", getattr(e,"updated","")), d.feed.get("title","RSS"), getattr(e,"summary","")))
        except Exception as ex:
            print("RSS 讀取錯誤:", url, ex)
    print(f"RSS 取得 {len(out)} 則")
    return out

def fetch_hn_algolia(cfg):
    if not cfg.get("enabled", False): return []
    import requests
    q = cfg.get("query","ai")
    url = "https://hn.algolia.com/api/v1/search_by_date?" + urlencode({"query":q,"tags":"story"})
    try:
        r = requests.get(url, timeout=20); r.raise_for_status(); data = r.json()
        out = []
        for h in data.get("hits", []):
            out.append(normalize_article(h.get("title"), h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}", h.get("created_at"), "HackerNews", ""))
        print(f"HN Algolia 取得 {len(out)} 則")
        return out
    except Exception as ex:
        print("HN Algolia 讀取錯誤:", ex); return []

def dedup(articles):
    seen=set(); out=[]
    for a in articles:
        key=(a["title"][:120], a["url"])
        if key in seen: continue
        seen.add(key); out.append(a)
    return out

def main():
    cfg = load_yaml("config/sources.yaml")
    all_ = []
    all_ += fetch_newsapi(cfg.get("newsapi",{}))
    all_ += fetch_rss(cfg.get("rss",{}))
    all_ += fetch_hn_algolia(cfg.get("fallback_hn_algolia",{}))
    all_ = dedup(all_)
    date_path = today_path()
    base = f"data/{date_path}"
    write_json(f"{base}/raw_news.json", all_)
    write_json(f"{base}/metadata.json", {"collected_at": datetime.now(timezone.utc).isoformat(), "count": len(all_), "sources": [k for k,v in cfg.items() if v.get('enabled')]})
    print("✅ 收集完成")

if __name__ == "__main__":
    main()