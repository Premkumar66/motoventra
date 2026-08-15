import requests
import os
import sqlite3
import shutil

OUT_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://commons.wikimedia.org/'
}

GASGAS_MODELS = [
    {
        "name": "EC 300 2-Stroke",
        "filename": "gasgas_ec_300_2stroke.png",
        "query": "GasGas EC 300 motorcycle"
    },
    {
        "name": "ES 700 Enduro",
        "filename": "gasgas_es_700_enduro.png",
        "query": "GasGas ES 700 motorcycle"
    },
    {
        "name": "SM 700 Supermoto",
        "filename": "gasgas_sm_700_supermoto.png",
        "query": "GasGas SM 700 motorcycle"
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

print("=== Step 1: Processing GASGAS Model Images ===")
for item in GASGAS_MODELS:
    name = item["name"]
    filename = item["filename"]
    query = item["query"]
    target_path = os.path.join(OUT_DIR, filename)
    
    wm_u = search_wikimedia(query)
    if wm_u and download_img(wm_u, target_path):
        print(f"  [WM SEARCH OK] {name:20} -> {filename:30} ({os.path.getsize(target_path)//1024} KB)")
    else:
        # Try broader search "GasGas motorcycle"
        wm_u2 = search_wikimedia("GasGas motorcycle")
        if wm_u2 and download_img(wm_u2, target_path):
            print(f"  [WM BROADER OK] {name:20} -> {filename:30} ({os.path.getsize(target_path)//1024} KB)")
        else:
            print(f"  [NEED FALLBACK] {name:20} -> {filename:30}")

print("\n=== Step 2: Updating Database thumbnail_url for GASGAS Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%gasgas%' OR LOWER(name) LIKE '%gas gas%'")
brand_id = cur.fetchone()[0]

for item in GASGAS_MODELS:
    name = item["name"]
    filename = item["filename"]
    img_url = f"/static/images/{filename}"
    
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, name)
    )
    print(f"  [DB OK] {name:20} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Step 3: Verifying GASGAS Images on Disk ===")
for item in GASGAS_MODELS:
    name = item["name"]
    filename = item["filename"]
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  GASGAS {name:20} | {filename:30} | {sz:5} KB | Exists: {os.path.exists(fp)}")
