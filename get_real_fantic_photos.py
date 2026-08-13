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

FANTIC_MODELS = [
    {
        "name": "Caballero 500 Scrambler",
        "filename": "fantic_caballero_500_scrambler.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/1/14/Fantic_Caballero_500.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Fantic_Caballero_500.jpg/1200px-Fantic_Caballero_500.jpg"
        ]
    },
    {
        "name": "Imola 500 Concept",
        "filename": "fantic_imola_500_concept.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/e/e0/Fantic_Imola.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Fantic_Imola.jpg/1200px-Fantic_Imola.jpg"
        ]
    },
    {
        "name": "XEF 450 Rally",
        "filename": "fantic_xef_450_rally.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/d/d4/Fantic_XEF_450_Rally.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Fantic_XEF_450_Rally.jpg/1200px-Fantic_XEF_450_Rally.jpg"
        ]
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

print("=== Step 1: Processing Fantic Model Images ===")
for item in FANTIC_MODELS:
    name = item["name"]
    filename = item["filename"]
    target_path = os.path.join(OUT_DIR, filename)
    
    downloaded = False
    for u in item["urls"]:
        if download_img(u, target_path):
            print(f"  [DIRECT OK]  {name:25} -> {filename:32} ({os.path.getsize(target_path)//1024} KB)")
            downloaded = True
            break

    if not downloaded:
        wm_u = search_wikimedia(f"Fantic {name} motorcycle")
        if wm_u and download_img(wm_u, target_path):
            print(f"  [WM SEARCH]  {name:25} -> {filename:32} ({os.path.getsize(target_path)//1024} KB)")
        else:
            # Generate fallback card using Pillow
            im = Image.new("RGB", (1000, 650), (6, 11, 24))
            im.save(target_path, "PNG")
            print(f"  [CARD GEN]   {name:25} -> {filename:32} ({os.path.getsize(target_path)//1024} KB)")

print("\n=== Step 2: Updating Database thumbnail_url for Fantic Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%fantic%'")
brand_id = cur.fetchone()[0]

for item in FANTIC_MODELS:
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

print("\n=== Step 3: Verifying Fantic Images on Disk ===")
for item in FANTIC_MODELS:
    name = item["name"]
    filename = item["filename"]
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  Fantic {name:25} | {filename:32} | {sz:5} KB | Exists: {os.path.exists(fp)}")
