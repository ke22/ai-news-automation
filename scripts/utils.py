import os, json, hashlib
from datetime import datetime, timezone
from dateutil import parser as dtparser

TZ = timezone.utc

def today_path():
    return datetime.now(TZ).strftime("%Y/%m/%d")

def iso_now():
    return datetime.now(TZ).isoformat()

def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def normalize_article(title, url, published_at, source, summary=""):
    try:
        ts = dtparser.parse(published_at).astimezone(TZ).isoformat()
    except Exception:
        ts = iso_now()
    return {"id": sha1(url or title or ts), "title": title or "", "url": url, "published_at": ts, "source": source, "summary": summary or ""}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(os.path.join(path), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_yaml(path):
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_json(path, default=None):
    if not os.path.exists(path): return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def to_display_date(iso_ts):
    try:
        d = dtparser.parse(iso_ts).date().isoformat()
        return d
    except Exception:
        return iso_ts[:10]