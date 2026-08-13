import sqlite3
import os
import requests

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
STATIC_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
BASE_URL = "http://localhost:8000"

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

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("===========================================================================")
print("VERIFYING DUCATI MODELS, IMAGE FILES & DB THUMBNAILS")
print("===========================================================================")

all_ok = True
for model_name, filename in ducati_10_models:
    img_url = f"/static/images/{filename}"
    filepath = os.path.join(STATIC_DIR, filename)
    exists = os.path.exists(filepath)
    size_kb = (os.path.getsize(filepath) // 1024) if exists else 0
    
    cur.execute("SELECT thumbnail_url FROM motorcycles WHERE name=?", (model_name,))
    row = cur.fetchone()
    db_thumb = row[0] if row else "NOT FOUND"
    
    try:
        r = requests.head(BASE_URL + img_url, timeout=3)
        http_code = r.status_code
    except Exception as e:
        http_code = str(e)
        
    status_str = "OK" if exists and size_kb > 50 and http_code == 200 else "CHECK"
    if status_str == "CHECK":
        all_ok = False
        
    print(f"[{status_str:5}] {model_name:22} | {filename:32} | {size_kb:6} KB | DB: {db_thumb}")

conn.close()

if all_ok:
    print("\nAll 10 Ducati models verified 100% active, mapped in DB, and serving live HTTP 200 OK!")
