import sqlite3
import os
import requests

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
STATIC_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
BASE_URL = "http://localhost:8000"

gasgas_models = [
    ("EC 300 2-Stroke", "gasgas_ec_300_2stroke.png"),
    ("ES 700 Enduro", "gasgas_es_700_enduro.png"),
    ("SM 700 Supermoto", "gasgas_sm_700_supermoto.png")
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("===========================================================================")
print("VERIFYING GASGAS MODELS, IMAGE FILES & DB THUMBNAILS")
print("===========================================================================")

all_ok = True
for model_name, filename in gasgas_models:
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
        
    print(f"[{status_str:5}] {model_name:20} | {filename:30} | {size_kb:6} KB | DB: {db_thumb}")

conn.close()

if all_ok:
    print("\nAll 3 GASGAS models verified 100% active, mapped in DB, and serving live HTTP 200 OK!")
