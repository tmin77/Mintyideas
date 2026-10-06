"""Converts TikTok short links (tiktok.com/t/...) in content.py into full video links so videos play
right on the page. Run on your own computer: python3 resolve_links.py  then  python3 build.py"""
import re, urllib.request
path = "content.py"
src = open(path).read()
for short in sorted(set(re.findall(r"https://(?:www|vm|vt)\.tiktok\.com/(?:t/)?[A-Za-z0-9]+/?", src))):
    if "/video/" in short: continue
    try:
        req = urllib.request.Request(short, headers={"User-Agent": "Mozilla/5.0"})
        full = urllib.request.urlopen(req, timeout=15).geturl().split("?")[0]
        if "/video/" in full:
            src = src.replace(f'"{short}"', f'"{full}"'); print("ok ", short, "->", full)
        else: print("skip", short, "->", full)
    except Exception as ex:
        print("fail", short, ex)
open(path, "w").write(src)
