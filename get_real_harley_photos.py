import requests
import os
import sqlite3
import shutil
from PIL import Image

OUT_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://commons.wikimedia.org/'
}

HARLEY_MODELS = [
    {
        "name": "Breakout 117",
        "filename": "harley_breakout_117.png",
        "query": "Harley Davidson Breakout motorcycle"
    },
    {
        "name": "CVO Street Glide",
        "filename": "harley_cvo_street_glide.png",
        "query": "Harley Davidson CVO Street Glide motorcycle"
    },
    {
        "name": "Fat Boy 114",
        "filename": "harley_fat_boy_114.png",
        "query": "Harley Davidson Fat Boy motorcycle"
    },
    {
        "name": "Heritage Classic 114",
        "filename": "harley_heritage_classic_114.png",
        "query": "Harley Davidson Heritage Classic motorcycle"
    },
    {
        "name": "Nightster Special",
        "filename": "harley_nightster_special.png",
        "query": "Harley Davidson Nightster motorcycle"
    },
    {
        "name": "Pan America 1250 Special",
        "filename": "harley_pan_america_1250_special.png",
        "query": "Harley Davidson Pan America motorcycle"
    },
    {
        "name": "Road Glide Limited",
        "filename": "harley_road_glide_limited.png",
        "query": "Harley Davidson Road Glide motorcycle"
    },
    {
        "name": "Sportster S",
        "filename": "harley_sportster_s.png",
        "query": "Harley Davidson Sportster S motorcycle"
    },
    {
        "name": "Street Glide Special",
        "filename": "harley_street_glide_special.png",
        "query": "Harley Davidson Street Glide motorcycle"
    },
    {
        "name": "X440 Roadster",
        "filename": "harley_x440_roadster.png",
        "query": "Harley Davidson X440 motorcycle"
    }
]

def search_wikimedia(query):
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
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        results = r.json().get('query', {}).get('search', [])
        for res in results:
            title = res['title']
            info_params = {
                'action': 'query',
                'titles': title,
                'prop': 'imageinfo',
                'iiprop': 'url|size',
                'format': 'json'
            }
            ir = requests.get(url, params=info_params, headers=HEADERS, timeout=10)
            pages = ir.json().get('query', {}).get('pages', {})
            for page in pages.values():
                ii = page.get('imageinfo', [{}])[0]
                u = ii.get('url', '')
                sz = ii.get('size', 0)
                if u and sz > 30000:
                    return u
    except Exception as e:
        print(f"Wikimedia search error for {query}: {e}")
    return None

def download_img(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 20000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        pass
    return False

print("=== Step 1: Processing Harley-Davidson Model Images ===")
fallback_base = os.path.join(OUT_DIR, "harley_davidson_bike.png")

for item in HARLEY_MODELS:
    name = item["name"]
    filename = item["filename"]
    query = item["query"]
    target_path = os.path.join(OUT_DIR, filename)
    
    wm_u = search_wikimedia(query)
    if wm_u and download_img(wm_u, target_path):
        print(f"  [WM SEARCH OK] {name:25} -> {filename:32} ({os.path.getsize(target_path)//1024} KB)")
    else:
        wm_u2 = search_wikimedia("Harley Davidson motorcycle")
        if wm_u2 and download_img(wm_u2, target_path):
            print(f"  [WM BROADER OK] {name:25} -> {filename:32} ({os.path.getsize(target_path)//1024} KB)")
        elif os.path.exists(fallback_base):
            shutil.copy2(fallback_base, target_path)
            print(f"  [FALLBACK OK]   {name:25} -> {filename:32} ({os.path.getsize(target_path)//1024} KB)")

# Optimize large PNGs (>1.5MB)
for item in HARLEY_MODELS:
    filename = item["filename"]
    fp = os.path.join(OUT_DIR, filename)
    if os.path.exists(fp) and os.path.getsize(fp) > 1500000:
        try:
            im = Image.open(fp)
            im.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            im.save(fp, "PNG", optimize=True)
            print(f"  [RESIZED] {filename:32} -> {os.path.getsize(fp)//1024} KB")
        except Exception as e:
            pass

print("\n=== Step 2: Updating Database thumbnail_url for Harley Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%harley%'")
brand_id = cur.fetchone()[0]

for item in HARLEY_MODELS:
    name = item["name"]
    filename = item["filename"]
    img_url = f"/static/images/{filename}"
    
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, name)
    )
    print(f"  [DB OK] {name:25} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Step 3: Verifying Harley Images on Disk ===")
for item in HARLEY_MODELS:
    name = item["name"]
    filename = item["filename"]
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  Harley {name:25} | {filename:32} | {sz:5} KB | Exists: {os.path.exists(fp)}")
