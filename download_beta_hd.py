import requests
import shutil
import os
import sqlite3

OUT_DIR = 'motomod-ai/backend/app/static/images'
DB_PATH = 'motomod-ai/backend/motomod_ai.db'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://commons.wikimedia.org/'
}

DIRECT_MAP = {
    "beta_evo_300_trial.png": [
        "https://upload.wikimedia.org/wikipedia/commons/e/e0/Beta_EVO_2T_300.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Beta_EVO_2T_300.jpg/1200px-Beta_EVO_2T_300.jpg"
    ],
    "beta_rr_390_4t.png": [
        "https://upload.wikimedia.org/wikipedia/commons/b/b3/Beta_RR_4T_390_Enduro.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Beta_RR_4T_390_Enduro.jpg/1200px-Beta_RR_4T_390_Enduro.jpg"
    ],
    "beta_xtrainer_300_enduro.png": [
        "https://upload.wikimedia.org/wikipedia/commons/2/23/Beta_Xtrainer_300.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Beta_Xtrainer_300.jpg/1200px-Beta_Xtrainer_300.jpg"
    ]
}

def fetch_hd():
    print("=== Downloading HD Photos for Beta Motorcycle Models ===")
    for filename, urls in DIRECT_MAP.items():
        filepath = os.path.join(OUT_DIR, filename)
        print(f"\nDownloading {filename}...")
        for url in urls:
            try:
                r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
                if r.status_code == 200:
                    with open(filepath, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    size_kb = os.path.getsize(filepath) // 1024
                    if size_kb > 40:
                        print(f"  [OK] Saved {filename} ({size_kb} KB) from {url[:60]}")
                        break
                else:
                    print(f"  HTTP {r.status_code} for {url[:60]}")
            except Exception as e:
                print(f"  Error: {e}")

    print("\n=== Verifying DB Links for Beta ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM brands WHERE name='Beta'")
    beta_id = cur.fetchone()[0]

    model_map = {
        "EVO 300 Trial": "beta_evo_300_trial.png",
        "RR 390 4T": "beta_rr_390_4t.png",
        "Xtrainer 300 Enduro": "beta_xtrainer_300_enduro.png"
    }

    for name, fn in model_map.items():
        img_url = f"/static/images/{fn}"
        cur.execute("UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?", (img_url, beta_id, name))
        print(f"  DB: {name:20} -> {img_url}")
    conn.commit()
    conn.close()

    print("\n=== Final Files Verification ===")
    for fn in DIRECT_MAP.keys():
        fp = os.path.join(OUT_DIR, fn)
        sz = os.path.getsize(fp) // 1024 if os.path.exists(fp) else 0
        print(f"  {fn:30} : {sz:5} KB | Exists: {os.path.exists(fp)}")

if __name__ == "__main__":
    fetch_hd()
