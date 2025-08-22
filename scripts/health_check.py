#!/usr/bin/env python
import os, glob, sys
from datetime import datetime, timezone, timedelta
from dateutil import parser as dtparser

def newest_data_time():
    dirs = sorted(glob.glob("data/*/*/*"))
    if not dirs: return None
    latest = dirs[-1].replace("data/","").replace("/","-")
    try:
        return dtparser.parse(latest).replace(tzinfo=timezone.utc)
    except Exception:
        return None

def main():
    t = newest_data_time()
    if not t:
        print("❌ 無資料資料夾"); sys.exit(1)
    delta = datetime.now(timezone.utc) - t
    if delta > timedelta(hours=36):
        print(f"❌ 資料已過期：{delta}"); sys.exit(1)
    print(f"✅ 健康：最新資料 {delta} 前")

if __name__ == "__main__":
    main()