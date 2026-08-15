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

HARLEY_10 = [
    ("Breakout 117", "harley_breakout_117.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Harley-Davidson_Breakout.jpg/1200px-Harley-Davidson_Breakout.jpg"),
    ("CVO Street Glide", "harley_cvo_street_glide.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Harley-Davidson_CVO.jpg/1200px-Harley-Davidson_CVO.jpg"),
    ("Fat Boy 114", "harley_fat_boy_114.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Harley-Davidson_Fat_Boy.jpg/1200px-Harley-Davidson_Fat_Boy.jpg"),
    ("Heritage Classic 114", "harley_heritage_classic_114.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Harley_Davidson_Heritage_Softail.jpg/1200px-Harley_Davidson_Heritage_Softail.jpg"),
    ("Nightster Special", "harley_nightster_special.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Harley-Davidson_Nightster.jpg/1200px-Harley-Davidson_Nightster.jpg"),
    ("Pan America 1250 Special", "harley_pan_america_1250_special.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Harley-Davidson_Pan_America_1250.jpg/1200px-Harley-Davidson_Pan_America_1250.jpg"),
    ("Road Glide Limited", "harley_road_glide_limited.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Harley-Davidson_Road_Glide.jpg/1200px-Harley-Davidson_Road_Glide.jpg"),
    ("Sportster S", "harley_sportster_s.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Harley-Davidson_Sportster_S.jpg/1200px-Harley-Davidson_Sportster_S.jpg"),
    ("Street Glide Special", "harley_street_glide_special.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Harley-Davidson_Street_Glide.jpg/1200px-Harley-Davidson_Street_Glide.jpg"),
    ("X440 Roadster", "harley_x440_roadster.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Harley-Davidson_X440.jpg/1200px-Harley-Davidson_X440.jpg")
]

def download_img(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 30000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        pass
    return False

fallback_base = os.path.join(OUT_DIR, "harley_davidson_bike.png")

print("=== Step 1: Downloading missing images & optimizing ===")
for model_name, filename, url in HARLEY_10:
    fp = os.path.join(OUT_DIR, filename)
    if not os.path.exists(fp) or os.path.getsize(fp) == 0:
        if download_img(url, fp):
            print(f"  [HD OK] {model_name:25} -> {os.path.getsize(fp)//1024} KB")
        elif os.path.exists(fallback_base):
            shutil.copy2(fallback_base, fp)
            print(f"  [FALLBACK OK] {model_name:25} -> {os.path.getsize(fp)//1024} KB")

# Optimize heavy files (>1.5MB)
for model_name, filename, _ in HARLEY_10:
    fp = os.path.join(OUT_DIR, filename)
    if os.path.exists(fp) and os.path.getsize(fp) > 1500000:
        try:
            im = Image.open(fp)
            im.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            im.save(fp, "PNG", optimize=True)
            print(f"  [RESIZED] {filename:32} -> {os.path.getsize(fp)//1024} KB")
        except Exception as e:
            pass

print("\n=== Step 2: Updating Database thumbnail_url for All 10 Harley Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%harley%'")
brand_id = cur.fetchone()[0]

for model_name, filename, _ in HARLEY_10:
    img_url = f"/static/images/{filename}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )
    print(f"  [DB OK] {model_name:25} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Final Verification of Harley Models ===")
for model_name, filename, _ in HARLEY_10:
    fp = os.path.join(OUT_DIR, filename)
    sz = (os.path.getsize(fp) // 1024) if os.path.exists(fp) else 0
    print(f"  Harley {model_name:25} | {filename:32} | {sz:5} KB | Exists: {os.path.exists(fp)}")
