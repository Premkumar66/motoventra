"""
Final pass: Download all remaining Bajaj model photos using confirmed direct URLs.
For models with no Wikimedia photo, search Wikimedia API with proper delays.
"""
import requests, shutil, os, time, json

HEADERS = {'User-Agent': 'MotoVentra/1.0 (educational; https://github.com/Premkumar66/motoventra)'}
OUT_DIR = 'motomod-ai/backend/app/static/images'

def wikimedia_api(params, retries=3):
    """Call Wikimedia API with retry and delay."""
    url = 'https://commons.wikimedia.org/w/api.php'
    for i in range(retries):
        try:
            r = requests.get(url, params={**params, 'format': 'json'}, headers=HEADERS, timeout=20)
            if r.status_code == 429:
                time.sleep(15 * (i+1))
                continue
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"  API error: {e}")
            time.sleep(5)
    return {}

def get_imageinfo(title):
    data = wikimedia_api({'action': 'query', 'titles': title, 'prop': 'imageinfo', 'iiprop': 'url|size|mime'})
    pages = data.get('query', {}).get('pages', {})
    for page in pages.values():
        ii = page.get('imageinfo', [{}])[0]
        url = ii.get('url', '')
        size = ii.get('size', 0)
        mime = ii.get('mime', '')
        if url and size > 50000 and mime in ('image/jpeg', 'image/png'):
            return url, size
    return None, 0

def search_and_get(term, min_size=200000):
    """Search Wikimedia and return first valid image URL."""
    data = wikimedia_api({'action': 'query', 'list': 'search', 'srsearch': f'filetype:bitmap {term}', 'srnamespace': 6, 'srlimit': 8})
    results = data.get('query', {}).get('search', [])
    time.sleep(1)
    for result in results:
        title = result['title']
        url, size = get_imageinfo(title)
        if url and size >= min_size:
            print(f"  Found via search: {title} ({size//1024} KB)")
            return url
        time.sleep(0.5)
    return None

def download(url, out_path, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, stream=True, timeout=60)
            if r.status_code == 429:
                time.sleep(15*(i+1))
                continue
            r.raise_for_status()
            with open(out_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            sz = os.path.getsize(out_path)
            print(f"  Saved: {os.path.basename(out_path)} ({sz//1024} KB)")
            return sz
        except Exception as e:
            print(f"  Attempt {i+1} failed: {e}")
            time.sleep(5)
    return 0

# ─── Confirmed direct URLs (verified by Wikimedia API) ──────────────────────
CONFIRMED = [
    {
        'name': 'Pulsar NS160',
        'out': 'bajaj_pulsar_ns160.png',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/d/df/BAJAJ_Pulsar_NS160.jpg',
    },
]

# ─── Models to search for ────────────────────────────────────────────────────
TO_SEARCH = [
    {
        'name': 'CT 125X',
        'out': 'bajaj_ct_125x.png',
        'terms': ['Bajaj CT 125X', 'Bajaj CT125', 'Bajaj CT motorcycle India commuter']
    },
    {
        'name': 'Freedom 125 CNG',
        'out': 'bajaj_freedom_125_cng.png',
        'terms': ['Bajaj Freedom 125 CNG', 'Bajaj Freedom motorcycle', 'Bajaj CNG motorcycle 125cc']
    },
    {
        'name': 'Pulsar N160',
        'out': 'bajaj_pulsar_n160.png',
        'terms': ['Bajaj Pulsar N160', 'Bajaj N160 naked motorcycle', 'Bajaj Pulsar 160 neon']
    },
    {
        'name': 'Pulsar N250',
        'out': 'bajaj_pulsar_n250.png',
        'terms': ['Bajaj Pulsar N250', 'Bajaj N250 naked motorcycle', 'Bajaj Pulsar 250 naked']
    },
]

print("=" * 60)
print("FINAL PASS DOWNLOADER")
print("=" * 60)

success = []
failed = []

# Download confirmed URLs first
for m in CONFIRMED:
    out = os.path.join(OUT_DIR, m['out'])
    existing = os.path.getsize(out)//1024 if os.path.exists(out) else 0
    print(f"\n[{m['name']}] Existing: {existing} KB")
    sz = download(m['url'], out)
    if sz > 50000:
        success.append(m['name'])
    else:
        failed.append(m['name'])
    time.sleep(3)

# Search for remaining
for m in TO_SEARCH:
    out = os.path.join(OUT_DIR, m['out'])
    existing = os.path.getsize(out)//1024 if os.path.exists(out) else 0
    
    # Skip if already has large real photo (>1MB)
    if existing > 1000:
        print(f"\n[{m['name']}] Already has real photo ({existing} KB)")
        success.append(m['name'])
        continue

    print(f"\n[{m['name']}] Existing: {existing} KB — searching...")
    img_url = None
    for term in m['terms']:
        print(f"  Searching: {term}")
        img_url = search_and_get(term, min_size=100000)
        if img_url:
            break
        time.sleep(3)

    if img_url:
        sz = download(img_url, out)
        if sz > 50000:
            success.append(m['name'])
        else:
            failed.append(m['name'])
    else:
        print(f"  No Wikimedia photo found — will use existing generated image")
        failed.append(m['name'])
    time.sleep(4)

print("\n" + "=" * 60)
print(f"SUCCESS ({len(success)}): {success}")
print(f"FAILED  ({len(failed)}): {failed}")

# Show final status of all 12 bajaj images
print("\n=== ALL 12 BAJAJ MODEL IMAGES FINAL STATUS ===")
all_bajaj = [
    ('Avenger Cruise 220', 'bajaj_avenger_cruise_220.png'),
    ('CT 125X',            'bajaj_ct_125x.png'),
    ('Chetak Premium EV',  'bajaj_chetak_premium_ev.png'),
    ('Dominar 250',        'bajaj_dominar_250.png'),
    ('Dominar 400',        'bajaj_dominar_400.png'),
    ('Freedom 125 CNG',    'bajaj_freedom_125_cng.png'),
    ('Pulsar 220F',        'bajaj_pulsar_220f.png'),
    ('Pulsar N160',        'bajaj_pulsar_n160.png'),
    ('Pulsar N250',        'bajaj_pulsar_n250.png'),
    ('Pulsar NS125',       'bajaj_pulsar_ns125.png'),
    ('Pulsar NS160',       'bajaj_pulsar_ns160.png'),
    ('Pulsar NS200',       'bajaj_pulsar_ns200.png'),
]
for name, f in all_bajaj:
    p = os.path.join(OUT_DIR, f)
    sz = os.path.getsize(p)//1024 if os.path.exists(p) else 0
    status = 'REAL PHOTO' if sz > 500 else ('SMALL' if sz > 0 else 'MISSING')
    print(f"  {name:25} {sz:6} KB  [{status}]")
print("=" * 60)
