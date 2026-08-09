import requests
import os
import sqlite3
import shutil
from PIL import Image

OUT_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

DUCATI_HD_URLS = {
    "Monster SP": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Ducati_Monster_937.jpg/1200px-Ducati_Monster_937.jpg",
    "Panigale V2": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ducati_Panigale_V2.jpg/1200px-Ducati_Panigale_V2.jpg",
    "Scrambler Icon 2G": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Ducati_Scrambler_Icon.jpg/1200px-Ducati_Scrambler_Icon.jpg",
    "Streetfighter V4 SP2": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Ducati_Streetfighter_V4.jpg/1200px-Ducati_Streetfighter_V4.jpg",
    "SuperSport 950 S": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Ducati_SuperSport_950.jpg/1200px-Ducati_SuperSport_950.jpg"
}

def download_and_save(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 30000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print("Download error:", e)
    return False

print("=== Step 1: Downloading & Optimizing Ducati HD Images ===")
for model_name, url in DUCATI_HD_URLS.items():
    clean_name = model_name.lower().replace(" ", "_").replace("-", "_")
    filename = f"ducati_{clean_name}.png"
    filepath = os.path.join(OUT_DIR, filename)
    
    if download_and_save(url, filepath):
        print(f"  [HD OK] {model_name:22} -> {os.path.getsize(filepath)//1024} KB")

# Optimize heavy files (>1.5MB)
for f in os.listdir(OUT_DIR):
    if f.startswith("ducati_") and f.endswith(".png"):
        fp = os.path.join(OUT_DIR, f)
        if os.path.getsize(fp) > 1500000:
            try:
                im = Image.open(fp)
                im.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                im.save(fp, "PNG", optimize=True)
                print(f"  [RESIZED] {f:30} -> {os.path.getsize(fp)//1024} KB")
            except Exception as e:
                pass

print("\n=== Step 2: Updating Database thumbnail_url for All 10 Ducati Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%ducati%'")
brand_id = cur.fetchone()[0]

ducati_10_models = [
    ("DesertX Rally", "ducati_desertx_rally.png"),
    ("Diavel V4", "ducati_diavel_v4.png"),
    ("Hypermotard 950 RVE", "ducati_hypermotard_950_rve.png"),
    ("Monster SP", "ducati_monster_sp.png"),
    ("Multistrada V4 S", "ducati_multistrada_v4_s.png"),
    ("Panigale V2", "ducati_panigale_v2.png"),
    ("Panigale V4 S", "ducati_panigale_v4_s.png"),
    ("Scrambler Icon 2G", "ducati_scrambler_icon_2g.png"),
    ("Streetfighter V4 SP2", "ducati_streetfighter_v4_sp2.png"),
    ("SuperSport 950 S", "ducati_supersport_950_s.png")
]

for model_name, filename in ducati_10_models:
    img_url = f"/static/images/{filename}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )
    print(f"  [DB OK] {model_name:22} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Final Verification of Ducati Images ===")
for model_name, filename in ducati_10_models:
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  Ducati {model_name:22} | {filename:30} | {sz:5} KB | Exists: {os.path.exists(fp)}")
