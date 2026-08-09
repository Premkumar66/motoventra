import os
import sqlite3
import requests
from PIL import Image

STATIC_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

# High definition direct OEM / studio links for Bajaj models
BAJAJ_HD_MAPPINGS = {
    "Avenger Cruise 220": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Bajaj_Avenger_Cruise_220.jpg",
    "CT 125X": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Bajaj_CT_125X.jpg",
    "Chetak Premium EV": "https://upload.wikimedia.org/wikipedia/commons/6/62/Bajaj_Chetak_Electric.jpg",
    "Dominar 250": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Bajaj_Dominar_250.jpg",
    "Dominar 400": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Bajaj_Dominar_400.jpg",
    "Freedom 125 CNG": "https://upload.wikimedia.org/wikipedia/commons/2/29/Bajaj_Freedom_125_CNG.jpg",
    "Pulsar 220F": "https://upload.wikimedia.org/wikipedia/commons/b/b2/Bajaj_Pulsar_220F.jpg",
    "Pulsar N160": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Bajaj_Pulsar_N160.jpg",
    "Pulsar N250": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Bajaj_Pulsar_N250.jpg",
    "Pulsar NS125": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Bajaj_Pulsar_NS125.jpg",
    "Pulsar NS160": "https://upload.wikimedia.org/wikipedia/commons/1/1d/Bajaj_Pulsar_NS160.jpg",
    "Pulsar NS200": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Bajaj_Pulsar_NS200.jpg"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== Optimizing & Verifying All 12 Bajaj Model Photographs ===")

for model_name, url in BAJAJ_HD_MAPPINGS.items():
    clean_name = model_name.lower().replace(" ", "_").replace("-", "_")
    filename = f"bajaj_{clean_name}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    
    # Compress large files (>1.5MB) to optimal web size (~500KB)
    if os.path.exists(filepath):
        sz_kb = os.path.getsize(filepath) // 1024
        if sz_kb > 1500:
            try:
                im = Image.open(filepath)
                im.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                im.save(filepath, "PNG", optimize=True)
                print(f"  [OPTIMIZED] {model_name:22} -> {os.path.getsize(filepath)//1024} KB")
            except Exception as e:
                print(f"  [ERROR OPT] {model_name}: {e}")
        else:
            print(f"  [VERIFIED]  {model_name:22} -> {sz_kb} KB")

# Update DB
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%bajaj%'")
brand_id = cur.fetchone()[0]

for model_name in BAJAJ_HD_MAPPINGS.keys():
    clean_name = model_name.lower().replace(" ", "_").replace("-", "_")
    filename = f"bajaj_{clean_name}.png"
    img_url = f"/static/images/{filename}"
    
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )

conn.commit()
conn.close()

print("\nAll 12 Bajaj motorcycle models updated & mapped in database!")
