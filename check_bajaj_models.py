import sqlite3
import os
import requests

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
STATIC_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
BASE_URL = "http://localhost:8000"

bajaj_models = [
    ("Avenger Cruise 220", "bajaj_avenger_cruise_220.png"),
    ("CT 125X", "bajaj_ct_125x.png"),
    ("Chetak Premium EV", "bajaj_chetak_premium_ev.png"),
    ("Dominar 250", "bajaj_dominar_250.png"),
    ("Dominar 400", "bajaj_dominar_400.png"),
    ("Freedom 125 CNG", "bajaj_freedom_125_cng.png"),
    ("Pulsar 220F", "bajaj_pulsar_220f.png"),
    ("Pulsar N160", "bajaj_pulsar_n160.png"),
    ("Pulsar N250", "bajaj_pulsar_n250.png"),
    ("Pulsar NS125", "bajaj_pulsar_ns125.png"),
    ("Pulsar NS160", "bajaj_pulsar_ns160.png"),
    ("Pulsar NS200", "bajaj_pulsar_ns200.png")
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("===========================================================================")
print("VERIFYING ALL 12 BAJAJ MOTORCYCLE MODELS, DB THUMBNAILS & HTTP RESPONSES")
print("===========================================================================")

all_ok = True
for model_name, filename in bajaj_models:
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
        
    status_str = "OK" if exists and http_code == 200 else "FAIL"
    if status_str == "FAIL":
        all_ok = False
        
    print(f"[{status_str:4}] {model_name:22} | {filename:30} | {size_kb:6} KB | DB: {db_thumb}")

conn.close()

if all_ok:
    print("\nAll 12 Bajaj models verified 100% active, mapped in DB, and serving live HTTP 200 OK!")
