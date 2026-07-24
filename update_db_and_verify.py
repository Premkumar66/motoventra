import sqlite3
import os

DB_PATH = 'motomod-ai/backend/motomod_ai.db'
IMG_DIR = 'motomod-ai/backend/app/static/images'

BAJAJ_MAPPING = {
    'Avenger Cruise 220': 'bajaj_avenger_cruise_220.png',
    'CT 125X': 'bajaj_ct_125x.png',
    'Chetak Premium EV': 'bajaj_chetak_premium_ev.png',
    'Dominar 250': 'bajaj_dominar_250.png',
    'Dominar 400': 'bajaj_dominar_400.png',
    'Freedom 125 CNG': 'bajaj_freedom_125_cng.png',
    'Pulsar 220F': 'bajaj_pulsar_220f.png',
    'Pulsar N160': 'bajaj_pulsar_n160.png',
    'Pulsar N250': 'bajaj_pulsar_n250.png',
    'Pulsar NS125': 'bajaj_pulsar_ns125.png',
    'Pulsar NS160': 'bajaj_pulsar_ns160.png',
    'Pulsar NS200': 'bajaj_pulsar_ns200.png',
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get Bajaj brand ID
cur.execute("SELECT id FROM brands WHERE name='Bajaj'")
brand_row = cur.fetchone()
if not brand_row:
    print("Bajaj brand not found!")
    exit(1)

bajaj_id = brand_row[0]
print(f"Bajaj Brand ID: {bajaj_id}\n")

print("=== Updating DB thumbnail_url for all 12 Bajaj models ===")
updated_count = 0
for model_name, img_file in BAJAJ_MAPPING.items():
    img_url = f"/static/images/{img_file}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, bajaj_id, model_name)
    )
    if cur.rowcount > 0:
        updated_count += cur.rowcount
        print(f"[DB UPDATED] {model_name:20} -> {img_url}")
    else:
        print(f"[NOT MATCHED] {model_name:20}")

conn.commit()

print("\n=== Current Database Verification for Bajaj Models ===")
cur.execute("SELECT name, category, thumbnail_url FROM motorcycles WHERE brand_id=? ORDER BY name", (bajaj_id,))
rows = cur.fetchall()
for name, cat, url in rows:
    filename = url.split('/')[-1] if url else 'NONE'
    filepath = os.path.join(IMG_DIR, filename) if url else ''
    exists = os.path.exists(filepath)
    size_kb = (os.path.getsize(filepath) // 1024) if exists else 0
    print(f"  {name:22} | {cat:10} | {url:40} | {size_kb:5} KB | Exists: {exists}")

conn.close()
