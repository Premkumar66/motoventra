"""
Fix: Update thumbnail_url in the motorcycles table for all brands
that have existing image files, so the frontend can display them correctly.
"""
import sqlite3
import os

DB_PATH = 'motomod-ai/backend/motomod_ai.db'
IMAGES_BASE = '/static/images/'

# Map: (brand_name, model_name) -> image filename
MODEL_IMAGE_MAP = {
    # ─── Benelli ───────────────────────────────────────────────────────────────
    ('Benelli', '502C Cruiser'):      'benelli_502c_cruiser.png',
    ('Benelli', 'Imperiale 400'):     'benelli_imperiale_400.png',
    ('Benelli', 'Leoncino 500'):      'benelli_leoncino_500.png',
    ('Benelli', 'TNT 600i Inline 4'): 'benelli_tnt_600i_inline_4.png',
    ('Benelli', 'TRK 502X'):          'benelli_trk_502x.png',

    # ─── Bajaj ─────────────────────────────────────────────────────────────────
    ('Bajaj', 'Avenger Cruise 220'): 'bajaj_avenger_cruise_220.png',
    ('Bajaj', 'CT 125X'):            'bajaj_ct_125x.png',
    ('Bajaj', 'Chetak Premium EV'):  'bajaj_chetak_premium_ev.png',
    ('Bajaj', 'Dominar 250'):        'bajaj_dominar_250.png',
    ('Bajaj', 'Dominar 400'):        'bajaj_dominar_400.png',
    ('Bajaj', 'Freedom 125 CNG'):    'bajaj_freedom_125_cng.png',
    ('Bajaj', 'Pulsar 220F'):        'bajaj_pulsar_220f.png',
    ('Bajaj', 'Pulsar N160'):        'bajaj_pulsar_n160.png',
    ('Bajaj', 'Pulsar N250'):        'bajaj_pulsar_n250.png',
    ('Bajaj', 'Pulsar NS125'):       'bajaj_pulsar_ns125.png',
    ('Bajaj', 'Pulsar NS160'):       'bajaj_pulsar_ns160.png',
    ('Bajaj', 'Pulsar NS200'):       'bajaj_pulsar_ns200.png',

    # ─── Ather ─────────────────────────────────────────────────────────────────
    ('Ather', '450S EV'):      'ather_450s_ev.png',
    ('Ather', '450X Apex EV'): 'ather_450x_apex_ev.png',
    ('Ather', 'Rizta Z EV'):   'ather_rizta_z_ev.png',
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

updated = 0
not_found = []

for (brand_name, model_name), img_file in MODEL_IMAGE_MAP.items():
    # Check if the image file actually exists
    local_path = os.path.join('motomod-ai/backend/app/static/images', img_file)
    if not os.path.exists(local_path):
        print(f"[MISSING FILE] {local_path}")
        not_found.append((brand_name, model_name, img_file))
        continue

    img_url = IMAGES_BASE + img_file

    # Get brand id
    cur.execute("SELECT id FROM brands WHERE name=?", (brand_name,))
    brand_row = cur.fetchone()
    if not brand_row:
        print(f"[BRAND NOT FOUND] {brand_name}")
        continue
    brand_id = brand_row[0]

    # Update motorcycle thumbnail_url
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )
    rows_affected = cur.rowcount
    if rows_affected > 0:
        print(f"[UPDATED] {brand_name} - {model_name} -> {img_url}")
        updated += rows_affected
    else:
        print(f"[NOT MATCHED IN DB] {brand_name} - {model_name}")

conn.commit()
conn.close()

print(f"\n✅ Done. Updated {updated} rows.")
if not_found:
    print(f"⚠️  Missing image files: {not_found}")
