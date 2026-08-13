import requests
import os
import sqlite3

OUT_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

FANTIC_SEARCHES = [
    ("Caballero 500 Scrambler", "fantic_caballero_500_scrambler.png", "Fantic Caballero 500"),
    ("Imola 500 Concept", "fantic_imola_500_concept.png", "Fantic Imola"),
    ("XEF 450 Rally", "fantic_xef_450_rally.png", "Fantic XEF 450")
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
        print(f"Search error: {e}")
    return None

print("=== Fetching High-Res Photos for Fantic Models ===")
for model_name, filename, query in FANTIC_SEARCHES:
    target_path = os.path.join(OUT_DIR, filename)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 50000:
        print(f"  [ALREADY HD] {model_name:25} -> {os.path.getsize(target_path)//1024} KB")
        continue

    wm_url = search_wikimedia(query)
    if wm_url:
        try:
            r = requests.get(wm_url, headers=HEADERS, timeout=15)
            if r.status_code == 200 and len(r.content) > 30000:
                with open(target_path, 'wb') as f:
                    f.write(r.content)
                print(f"  [FETCHED HD] {model_name:25} -> {len(r.content)//1024} KB ({wm_url[:50]}...)")
        except Exception as e:
            print("Download error:", e)

# Update DB
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%fantic%'")
brand_id = cur.fetchone()[0]

for model_name, filename, _ in FANTIC_SEARCHES:
    img_url = f"/static/images/{filename}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )

conn.commit()
conn.close()

print("\n=== Final Verification of Fantic Models ===")
for model_name, filename, _ in FANTIC_SEARCHES:
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  Fantic {model_name:25} | {filename:32} | {sz:5} KB | Exists: {os.path.exists(fp)}")
