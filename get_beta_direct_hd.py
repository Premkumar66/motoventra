import requests
import json
import re
import os
import sqlite3
import shutil
import urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}

OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)
DB_PATH = 'motomod-ai/backend/motomod_ai.db'

MODELS = [
    {
        "name": "EVO 300 Trial",
        "file": "beta_evo_300_trial.png",
        "query": "Beta EVO 300 Trial motorcycle side view photo"
    },
    {
        "name": "RR 390 4T",
        "file": "beta_rr_390_4t.png",
        "query": "Beta RR 390 4T motorcycle side view photo"
    },
    {
        "name": "Xtrainer 300 Enduro",
        "file": "beta_xtrainer_300_enduro.png",
        "query": "Beta Xtrainer 300 Enduro motorcycle side view photo"
    }
]

def fetch_image_from_ddg(query):
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=8)
        # Find image URLs in HTML
        urls = re.findall(r'//external-content\.duckduckgo\.com/iu/\?u=([^&"]+)', r.text)
        for u in urls:
            clean = urllib.parse.unquote(u)
            if any(clean.lower().endswith(ext) or ext in clean.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return clean
    except Exception as e:
        print(f"Error DDG search: {e}")
    return None

def download_file(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            size_kb = os.path.getsize(filepath) // 1024
            if size_kb > 25:
                print(f"  [OK] Saved {os.path.basename(filepath)} ({size_kb} KB) from {url[:60]}...")
                return True
    except Exception as e:
        print(f"  Download error: {e}")
    return False

def run():
    print("=== Fetching Beta Motorcycle Models Exact Images ===")
    for m in MODELS:
        filepath = os.path.join(OUT_DIR, m["file"])
        print(f"\nSearching image for Beta {m['name']}...")
        url = fetch_image_from_ddg(m["query"])
        if url:
            print(f"Found URL: {url[:70]}")
            download_file(url, filepath)
        else:
            print("No URL found via DDG HTML")

    print("\n=== Updating Database thumbnail_url ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM brands WHERE name='Beta'")
    beta_id = cur.fetchone()[0]

    for m in MODELS:
        img_url = f"/static/images/{m['file']}"
        cur.execute(
            "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
            (img_url, beta_id, m['name'])
        )
        if cur.rowcount > 0:
            print(f"  [DB UPDATED] {m['name']:20} -> {img_url}")

    conn.commit()
    conn.close()

    print("\n=== Final Verification for Beta Models ===")
    for m in MODELS:
        filepath = os.path.join(OUT_DIR, m["file"])
        size_kb = (os.path.getsize(filepath) // 1024) if os.path.exists(filepath) else 0
        print(f"  Beta {m['name']:22} | {m['file']:28} | {size_kb:5} KB | Exists: {os.path.exists(filepath)}")

if __name__ == "__main__":
    run()
