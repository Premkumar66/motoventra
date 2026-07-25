import requests
import os
import sqlite3
import shutil
import time

OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)
DB_PATH = 'motomod-ai/backend/motomod_ai.db'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://commons.wikimedia.org/'
}

# Verified high quality Wikimedia photographs for the 4 BMW models
BMW_4_PHOTOS = [
    {
        "name": "F900R",
        "filename": "bmw_f900r.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/d/d3/BMW_F_900_R_2020_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/BMW_F_900_R_2020_1.jpg/1200px-BMW_F_900_R_2020_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/7/7d/BMW_F900R.jpg"
        ]
    },
    {
        "name": "F900XR",
        "filename": "bmw_f900xr.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/a/a2/BMW_F_900_XR_2020_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/BMW_F_900_XR_2020_1.jpg/1200px-BMW_F_900_XR_2020_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/3/36/BMW_F900XR.jpg"
        ]
    },
    {
        "name": "G310GS",
        "filename": "bmw_g310gs.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/8/87/BMW_G_310_GS_2018_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/BMW_G_310_GS_2018_1.jpg/1200px-BMW_G_310_GS_2018_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/6/6f/BMW_G310GS.jpg"
        ]
    },
    {
        "name": "G310R",
        "filename": "bmw_g310r.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/5/52/BMW_G_310_R_2017_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/BMW_G_310_R_2017_1.jpg/1200px-BMW_G_310_R_2017_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/1/1b/BMW_G310R.jpg"
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
                if img_url and size > 40000:
                    return img_url
    except Exception as e:
        print(f"Wikimedia search error: {e}")
    return None

def download_file(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            size_kb = os.path.getsize(filepath) // 1024
            if size_kb > 20:
                print(f"  [SUCCESS] Saved {os.path.basename(filepath)} ({size_kb} KB) from {url[:60]}...")
                return True
    except Exception as e:
        print(f"  Download error: {e}")
    return False

def process():
    print("=== Step 1: Downloading Real Authentic Photos for F900R, F900XR, G310GS, G310R ===")
    for item in BMW_4_PHOTOS:
        name = item["name"]
        filename = item["filename"]
        filepath = os.path.join(OUT_DIR, filename)

        print(f"\nProcessing BMW {name} ({filename})...")
        downloaded = False
        
        # Try direct URLs first
        for url in item["urls"]:
            if download_file(url, filepath):
                downloaded = True
                break
            time.sleep(1)
            
        # Try Wikimedia search if direct URL fails
        if not downloaded:
            search_query = f"BMW {name} motorcycle"
            print(f"Searching Wikimedia for '{search_query}'...")
            wm_url = search_wikimedia_image(search_query)
            if wm_url and download_file(wm_url, filepath):
                downloaded = True

    print("\n=== Step 2: Updating Database thumbnail_url ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%bmw%'")
    bmw_brand_id = cur.fetchone()[0]

    for item in BMW_4_PHOTOS:
        name = item["name"]
        filename = item["filename"]
        img_url = f"/static/images/{filename}"

        cur.execute(
            "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
            (img_url, bmw_brand_id, name)
        )
        if cur.rowcount > 0:
            print(f"  [DB OK] BMW {name:15} -> {img_url}")

    conn.commit()
    conn.close()

    print("\n=== Step 3: Verifying BMW 4 Images on Disk ===")
    for item in BMW_4_PHOTOS:
        name = item["name"]
        filename = item["filename"]
        filepath = os.path.join(OUT_DIR, filename)
        size_kb = (os.path.getsize(filepath) // 1024) if os.path.exists(filepath) else 0
        print(f"  BMW {name:15} | {filename:25} | {size_kb:6} KB | Exists: {os.path.exists(filepath)}")

if __name__ == "__main__":
    process()
