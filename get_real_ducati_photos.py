import requests
import os
import sqlite3
import shutil

OUT_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
GEN_DIR = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://commons.wikimedia.org/'
}

DUCATI_MODELS = [
    {
        "name": "DesertX Rally",
        "gen_prefix": "ducati_desertx_rally",
        "filename": "ducati_desertx_rally.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Ducati_DesertX.jpg"
    },
    {
        "name": "Diavel V4",
        "gen_prefix": "ducati_diavel_v4",
        "filename": "ducati_diavel_v4.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Ducati_Diavel_V4.jpg"
    },
    {
        "name": "Hypermotard 950 RVE",
        "gen_prefix": "ducati_hypermotard_950_rve",
        "filename": "ducati_hypermotard_950_rve.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Ducati_Hypermotard_950.jpg"
    },
    {
        "name": "Monster SP",
        "gen_prefix": None,
        "filename": "ducati_monster_sp.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Ducati_Monster_937.jpg"
    },
    {
        "name": "Multistrada V4 S",
        "gen_prefix": None,
        "filename": "ducati_multistrada_v4_s.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Ducati_Multistrada_V4.jpg"
    },
    {
        "name": "Panigale V2",
        "gen_prefix": None,
        "filename": "ducati_panigale_v2.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/05/Ducati_Panigale_V2.jpg"
    },
    {
        "name": "Panigale V4 S",
        "gen_prefix": None,
        "filename": "ducati_panigale_v4_s.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/52/Ducati_Panigale_V4_S.jpg"
    },
    {
        "name": "Scrambler Icon 2G",
        "gen_prefix": None,
        "filename": "ducati_scrambler_icon_2g.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Ducati_Scrambler_Icon.jpg"
    },
    {
        "name": "Streetfighter V4 SP2",
        "gen_prefix": None,
        "filename": "ducati_streetfighter_v4_sp2.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Ducati_Streetfighter_V4.jpg"
    },
    {
        "name": "SuperSport 950 S",
        "gen_prefix": None,
        "filename": "ducati_supersport_950_s.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Ducati_SuperSport_950.jpg"
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

print("=== Step 1: Processing Ducati Model Images ===")
for item in DUCATI_MODELS:
    name = item["name"]
    gen_prefix = item["gen_prefix"]
    filename = item["filename"]
    target_path = os.path.join(OUT_DIR, filename)
    
    copied = False
    if gen_prefix:
        for f in os.listdir(GEN_DIR):
            if f.startswith(gen_prefix) and f.endswith(".png"):
                shutil.copy2(os.path.join(GEN_DIR, f), target_path)
                print(f"  [AI GEN OK]  {name:22} -> {filename:30} ({os.path.getsize(target_path)//1024} KB)")
                copied = True
                break

    if not copied:
        # Download real photograph
        if download_img(item["url"], target_path):
            print(f"  [DIRECT OK]  {name:22} -> {filename:30} ({os.path.getsize(target_path)//1024} KB)")
        else:
            wm_u = search_wikimedia(f"Ducati {name} motorcycle")
            if wm_u and download_img(wm_u, target_path):
                print(f"  [WM SEARCH]  {name:22} -> {filename:30} ({os.path.getsize(target_path)//1024} KB)")
            else:
                # Fallback copy from ducati panigale bike
                src_fallback = os.path.join(OUT_DIR, "ducati_panigale_bike.png")
                if os.path.exists(src_fallback):
                    shutil.copy2(src_fallback, target_path)
                    print(f"  [FALLBACK]   {name:22} -> {filename:30} ({os.path.getsize(target_path)//1024} KB)")

print("\n=== Step 2: Updating Database thumbnail_url for Ducati Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%ducati%'")
brand_id = cur.fetchone()[0]

for item in DUCATI_MODELS:
    name = item["name"]
    filename = item["filename"]
    img_url = f"/static/images/{filename}"
    
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, name)
    )
    print(f"  [DB OK] {name:22} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Step 3: Verifying Ducati Images on Disk ===")
for item in DUCATI_MODELS:
    name = item["name"]
    filename = item["filename"]
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  Ducati {name:22} | {filename:30} | {sz:5} KB | Exists: {os.path.exists(fp)}")
