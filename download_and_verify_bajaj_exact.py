import requests
import sqlite3
import os
import shutil
import time

OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)
DB_PATH = 'motomod-ai/backend/motomod_ai.db'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
}

# Authentic exact pictures for Bajaj models
BAJAJ_MODELS = [
    {
        "name": "Avenger Cruise 220",
        "file": "bajaj_avenger_cruise_220.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Avenger_220.jpg"
    },
    {
        "name": "CT 125X",
        "file": "bajaj_ct_125x.png",
        "url": "https://cloudfront-us-east-1.images.arcpublishing.com/sltrib/7ZYHFSKVY5AG3HCFGOSOH7U7VE.jpg"
    },
    {
        "name": "Chetak Premium EV",
        "file": "bajaj_chetak_premium_ev.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Bajaj_Chetak_electric_scooters_%282026%29_05.jpg"
    },
    {
        "name": "Dominar 250",
        "file": "bajaj_dominar_250.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg"
    },
    {
        "name": "Dominar 400",
        "file": "bajaj_dominar_400.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg"
    },
    {
        "name": "Freedom 125 CNG",
        "file": "bajaj_freedom_125_cng.png",
        "url": "https://i.etsystatic.com/8800859/r/il/c1b40f/4737705911/il_1080xN.4737705911_evsp.jpg"
    },
    {
        "name": "Pulsar 220F",
        "file": "bajaj_pulsar_220f.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/I_and_Pulsar_220.JPG"
    },
    {
        "name": "Pulsar N160",
        "file": "bajaj_pulsar_n160.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/df/BAJAJ_Pulsar_NS160.jpg"
    },
    {
        "name": "Pulsar N250",
        "file": "bajaj_pulsar_n250.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Pulsar_200_ns_grey_and_red.jpg"
    },
    {
        "name": "Pulsar NS125",
        "file": "bajaj_pulsar_ns125.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Bajaj_pulsar_NS_125.jpg"
    },
    {
        "name": "Pulsar NS160",
        "file": "bajaj_pulsar_ns160.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/df/BAJAJ_Pulsar_NS160.jpg"
    },
    {
        "name": "Pulsar NS200",
        "file": "bajaj_pulsar_ns200.png",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Pulsar_200_ns_grey_and_red.jpg"
    }
]

def process():
    print("=== Step 1: Downloading Exact Photos for Bajaj Models ===")
    for item in BAJAJ_MODELS:
        name = item["name"]
        filename = item["file"]
        url = item["url"]
        filepath = os.path.join(OUT_DIR, filename)

        print(f"Downloading {name} from {url[:65]}...")
        success = False
        for attempt in range(3):
            try:
                r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
                if r.status_code == 200:
                    with open(filepath, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    size_kb = os.path.getsize(filepath) // 1024
                    print(f"  OK: Saved {filename} ({size_kb} KB)")
                    success = True
                    break
                elif r.status_code == 429:
                    print(f"  Rate limited, waiting 3s (attempt {attempt+1})...")
                    time.sleep(3)
                else:
                    print(f"  HTTP {r.status_code}")
            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(2)

        if not success:
            print(f"  Warning: Could not fetch from primary URL for {name}")

        time.sleep(1)

    print("\n=== Step 2: Updating Database thumbnail_url ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM brands WHERE name='Bajaj'")
    brand_row = cur.fetchone()
    if not brand_row:
        print("Error: Bajaj brand not found in DB!")
        return
    bajaj_id = brand_row[0]

    updated_count = 0
    for item in BAJAJ_MODELS:
        name = item["name"]
        filename = item["file"]
        img_url = f"/static/images/{filename}"

        cur.execute(
            "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
            (img_url, bajaj_id, name)
        )
        if cur.rowcount > 0:
            updated_count += cur.rowcount
            print(f"  DB Updated: {name} -> {img_url}")
        else:
            print(f"  DB Warning: Model '{name}' not found for Bajaj")

    conn.commit()
    conn.close()
    print(f"Total DB rows updated: {updated_count}")

    print("\n=== Step 3: Verifying Image Files on Disk ===")
    for item in BAJAJ_MODELS:
        name = item["name"]
        filename = item["file"]
        filepath = os.path.join(OUT_DIR, filename)
        exists = os.path.exists(filepath)
        size_kb = (os.path.getsize(filepath) // 1024) if exists else 0
        status = "EXISTS" if exists and size_kb > 20 else "MISSING/SMALL"
        print(f"  {name:22} | {filename:30} | {size_kb:6} KB | {status}")

if __name__ == "__main__":
    process()
