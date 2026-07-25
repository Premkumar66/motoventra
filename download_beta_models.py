import requests
import json
import re
import os
import sqlite3
import shutil
import time
import urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}

OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)
DB_PATH = 'motomod-ai/backend/motomod_ai.db'

# Beta models and high-quality direct photo URLs
BETA_MODELS = [
    {
        "name": "EVO 300 Trial",
        "file": "beta_evo_300_trial.png",
        "search_terms": ["Beta EVO 300 trial motorcycle", "Beta EVO 300 trial bike"],
        "direct_urls": [
            "https://upload.wikimedia.org/wikipedia/commons/9/91/Beta_EVO_300_Trial.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/e/e0/Beta_EVO_2T_300.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Beta_EVO_2T_300.jpg/1200px-Beta_EVO_2T_300.jpg"
        ]
    },
    {
        "name": "RR 390 4T",
        "file": "beta_rr_390_4t.png",
        "search_terms": ["Beta RR 390 4T enduro motorcycle", "Beta RR 390 dirt bike"],
        "direct_urls": [
            "https://upload.wikimedia.org/wikipedia/commons/d/d7/Beta_RR_390_4T.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/b/b3/Beta_RR_4T_390_Enduro.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Beta_RR_4T_390_Enduro.jpg/1200px-Beta_RR_4T_390_Enduro.jpg"
        ]
    },
    {
        "name": "Xtrainer 300 Enduro",
        "file": "beta_xtrainer_300_enduro.png",
        "search_terms": ["Beta Xtrainer 300 enduro motorcycle", "Beta Xtrainer 300 bike"],
        "direct_urls": [
            "https://upload.wikimedia.org/wikipedia/commons/2/23/Beta_Xtrainer_300.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Beta_Xtrainer_300.jpg/1200px-Beta_Xtrainer_300.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/5/5a/Beta_Xtrainer_300_Enduro.jpg"
        ]
    }
]

def search_wikimedia_image(query):
    url = 'https://commons.wikimedia.org/w/api.php'
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': f'filetype:bitmap {query}',
        'srnamespace': 6,
        'srlimit': 5,
        'format': 'json'
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        results = r.json().get('query', {}).get('search', [])
        for res in results:
            title = res['title']
            info_params = {
                'action': 'query',
                'titles': title,
                'prop': 'imageinfo',
                'iiprop': 'url|size|mime',
                'format': 'json'
            }
            ir = requests.get(url, params=info_params, headers=HEADERS, timeout=15)
            pages = ir.json().get('query', {}).get('pages', {})
            for page in pages.values():
                ii = page.get('imageinfo', [{}])[0]
                img_url = ii.get('url', '')
                size = ii.get('size', 0)
                if img_url and size > 30000:
                    return img_url
    except Exception as e:
        print(f"Wikimedia search error for '{query}': {e}")
    return None

def download_file(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            size_kb = os.path.getsize(filepath) // 1024
            if size_kb > 15:
                print(f"  [SUCCESS] Saved {os.path.basename(filepath)} ({size_kb} KB) from {url[:60]}...")
                return True
    except Exception as e:
        print(f"  Download error from {url[:50]}: {e}")
    return False

def process():
    print("=== Step 1: Collecting Authentic Photos for Beta Models ===")
    for item in BETA_MODELS:
        name = item["name"]
        filename = item["file"]
        filepath = os.path.join(OUT_DIR, filename)

        print(f"\nProcessing Beta {name} ({filename})...")
        downloaded = False
        
        # Try direct URLs first
        for url in item["direct_urls"]:
            if download_file(url, filepath):
                downloaded = True
                break
            time.sleep(1)
            
        # Try Wikimedia search if direct URL fails
        if not downloaded:
            for term in item["search_terms"]:
                print(f"Searching Wikimedia for '{term}'...")
                wm_url = search_wikimedia_image(term)
                if wm_url and download_file(wm_url, filepath):
                    downloaded = True
                    break
                time.sleep(1)

        # Fallback to Bing search if needed
        if not downloaded:
            print(f"  Searching fallback photo for Beta {name}...")
            search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote('Beta ' + name + ' motorcycle bike photo')}&FORM=HDRSC2"
            try:
                r = requests.get(search_url, headers=HEADERS, timeout=10)
                murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', r.text)
                if not murls:
                    murls = re.findall(r'"murl":"(https?://[^"]+)"', r.text)
                for murl in murls:
                    clean_url = murl.replace('\\/', '/')
                    if download_file(clean_url, filepath):
                        downloaded = True
                        break
            except Exception as e:
                print(f"  Fallback search error: {e}")

    print("\n=== Step 2: Updating Database thumbnail_url ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM brands WHERE name='Beta'")
    beta_id = cur.fetchone()[0]

    for item in BETA_MODELS:
        name = item["name"]
        filename = item["file"]
        img_url = f"/static/images/{filename}"

        cur.execute(
            "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
            (img_url, beta_id, name)
        )
        if cur.rowcount > 0:
            print(f"  [DB OK] {name:20} -> {img_url}")
        else:
            print(f"  [DB WARN] Model '{name}' not matched")

    conn.commit()
    conn.close()

    print("\n=== Step 3: Verifying Beta Images on Disk ===")
    for item in BETA_MODELS:
        name = item["name"]
        filename = item["file"]
        filepath = os.path.join(OUT_DIR, filename)
        size_kb = (os.path.getsize(filepath) // 1024) if os.path.exists(filepath) else 0
        print(f"  Beta {name:22} | {filename:30} | {size_kb:6} KB | Exists: {os.path.exists(filepath)}")

if __name__ == "__main__":
    process()
