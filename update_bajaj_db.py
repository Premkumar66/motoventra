"""
Step 3: After downloading real photos, update the DB thumbnail_url
for all Bajaj models so the frontend shows correct real photos.
"""
import sqlite3
import os

DB_PATH = 'motomod-ai/backend/motomod_ai.db'
IMG_BASE = '/static/images/'
IMG_DIR  = 'motomod-ai/backend/app/static/images'

BAJAJ_MAP = {
    'Avenger Cruise 220': 'bajaj_avenger_cruise_220.png',
    'CT 125X':            'bajaj_ct_125x.png',
    'Chetak Premium EV':  'bajaj_chetak_premium_ev.png',
    'Dominar 250':        'bajaj_dominar_250.png',
    'Dominar 400':        'bajaj_dominar_400.png',
    'Freedom 125 CNG':    'bajaj_freedom_125_cng.png',
    'Pulsar 220F':        'bajaj_pulsar_220f.png',
    'Pulsar N160':        'bajaj_pulsar_n160.png',
    'Pulsar N250':        'bajaj_pulsar_n250.png',
    'Pulsar NS125':       'bajaj_pulsar_ns125.png',
    'Pulsar NS160':       'bajaj_pulsar_ns160.png',
    'Pulsar NS200':       'bajaj_pulsar_ns200.png',
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get Bajaj brand id
cur.execute("SELECT id FROM brands WHERE name='Bajaj'")
bajaj_id = cur.fetchone()[0]
print(f"Bajaj brand_id: {bajaj_id}")

updated = 0
print("\n[MODEL IMAGE MAPPING]")
for model_name, img_file in BAJAJ_MAP.items():
    img_path = os.path.join(IMG_DIR, img_file)
    if not os.path.exists(img_path):
        print(f"  [MISSING] {model_name} -> {img_file}")
        continue

    size_kb = os.path.getsize(img_path) // 1024
    img_url = IMG_BASE + img_file
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, bajaj_id, model_name)
    )
    if cur.rowcount > 0:
        print(f"  [OK] {model_name} -> {img_url} ({size_kb} KB)")
        updated += 1
    else:
        print(f"  [NOT FOUND IN DB] {model_name}")

conn.commit()
conn.close()
print(f"\nTotal updated: {updated} models")
