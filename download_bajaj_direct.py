"""
Final targeted downloader — using confirmed direct Wikimedia URLs.
Runs after retry script. Downloads only models not yet successfully saved.
"""
import requests
import shutil
import os
import time

HEADERS = {
    'User-Agent': 'MotoVentra/1.0 (educational project)',
    'Referer': 'https://commons.wikimedia.org/'
}
OUT_DIR = 'motomod-ai/backend/app/static/images'

# Confirmed direct Wikimedia URLs (verified via API)
DIRECT_DOWNLOADS = [
    {
        'name': 'Pulsar 220F',
        'out_file': 'bajaj_pulsar_220f.png',
        'min_size_kb': 100,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/a/a9/Pulsar_220F-DTSi.jpg',
        ]
    },
    {
        'name': 'Dominar 400',
        'out_file': 'bajaj_dominar_400.png',
        'min_size_kb': 500,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg',
        ]
    },
    {
        'name': 'Pulsar NS200',
        'out_file': 'bajaj_pulsar_ns200.png',
        'min_size_kb': 500,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Pulsar_200_ns_grey_and_red.jpg',
        ]
    },
]

def download(url, out_path, min_kb=100, retries=3):
    for attempt in range(retries):
        try:
            print(f"  GET: {url[:80]}")
            r = requests.get(url, headers=HEADERS, stream=True, timeout=60)
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            with open(out_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            size_kb = os.path.getsize(out_path) // 1024
            if size_kb < min_kb:
                print(f"  File too small ({size_kb} KB), skipping")
                os.remove(out_path)
                return False
            print(f"  Saved: {os.path.basename(out_path)} ({size_kb} KB)")
            return True
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return False

print("=" * 60)
print("TARGETED DIRECT DOWNLOADER")
print("=" * 60)

for model in DIRECT_DOWNLOADS:
    out_path = os.path.join(OUT_DIR, model['out_file'])
    existing_size = os.path.getsize(out_path) // 1024 if os.path.exists(out_path) else 0
    
    # Skip if already a large real photo
    if existing_size > 1000:
        print(f"\n[{model['name']}] Already has real photo ({existing_size} KB) - skipping")
        continue
    
    print(f"\n[{model['name']}] Current size: {existing_size} KB")
    ok = False
    for url in model['urls']:
        ok = download(url, out_path, model['min_size_kb'])
        if ok:
            break
        time.sleep(5)
    
    if not ok:
        print(f"  FAILED to download {model['name']}")
    time.sleep(3)

print("\n=== Final Image Status ===")
for model in DIRECT_DOWNLOADS:
    p = os.path.join(OUT_DIR, model['out_file'])
    sz = os.path.getsize(p) // 1024 if os.path.exists(p) else 0
    print(f"  {model['name']:25} {model['out_file']:45} {sz} KB")
