"""
Retry downloader for failed Bajaj models.
Uses: direct known Wikimedia file URLs + Wikipedia article image API + delays to avoid rate limits.
"""
import requests
import shutil
import os
import time

HEADERS = {'User-Agent': 'MotoVentra/1.0 (educational project; contact: premkumar66@github)'}
OUT_DIR = 'motomod-ai/backend/app/static/images'

def get_direct_url(filename):
    """Get direct image URL by known filename from Wikimedia."""
    url = 'https://commons.wikimedia.org/w/api.php'
    params = {
        'action': 'query',
        'titles': f'File:{filename}',
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'format': 'json'
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        pages = r.json().get('query', {}).get('pages', {})
        for page in pages.values():
            ii = page.get('imageinfo', [{}])[0]
            img_url = ii.get('url', '')
            size = ii.get('size', 0)
            if img_url and size > 50000:
                print(f"  Direct URL: {img_url[:70]}... ({size//1024} KB)")
                return img_url
    except Exception as e:
        print(f"  Error: {e}")
    return None

def search_wikimedia(term, min_size=80000):
    """Search Wikimedia for an image."""
    url = 'https://commons.wikimedia.org/w/api.php'
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': f'filetype:bitmap {term}',
        'srnamespace': 6,
        'srlimit': 8,
        'format': 'json'
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        results = r.json().get('query', {}).get('search', [])
        for result in results:
            title = result['title']
            info_params = {
                'action': 'query',
                'titles': title,
                'prop': 'imageinfo',
                'iiprop': 'url|size|mime',
                'format': 'json'
            }
            ir = requests.get(url, params=info_params, headers=HEADERS, timeout=20)
            pages = ir.json().get('query', {}).get('pages', {})
            for page in pages.values():
                ii = page.get('imageinfo', [{}])[0]
                img_url = ii.get('url', '')
                size = ii.get('size', 0)
                mime = ii.get('mime', '')
                if img_url and size > min_size and mime in ('image/jpeg', 'image/png'):
                    print(f"  Found: {title} ({size//1024} KB)")
                    return img_url
        time.sleep(1)
    except Exception as e:
        print(f"  Search error: {e}")
    return None

def download(url, out_path, retries=3):
    """Download with retry on 429."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, stream=True, timeout=60)
            if r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            with open(out_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            size = os.path.getsize(out_path)
            print(f"  Saved: {os.path.basename(out_path)} ({size//1024} KB)")
            return True
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(3)
    return False

# ─── Retry list with known direct filenames and fallback search terms ─────────
RETRY_MODELS = [
    {
        'name': 'CT 125X',
        'out_file': 'bajaj_ct_125x.png',
        'direct_files': [
            'Bajaj CT 125X.jpg',
            'Bajaj CT125X.jpg',
            'Bajaj CT 100.jpg',
        ],
        'search_terms': ['Bajaj CT commuter motorcycle', 'Bajaj CT 100 motorcycle India']
    },
    {
        'name': 'Dominar 250',
        'out_file': 'bajaj_dominar_250.png',
        'direct_files': [
            'Bajaj Dominar 250.jpg',
            'Bajaj Dominar250.jpg',
        ],
        'search_terms': ['Bajaj Dominar 400 motorcycle', 'Bajaj Dominar touring bike']
    },
    {
        'name': 'Dominar 400',
        'out_file': 'bajaj_dominar_400.png',
        'direct_files': [
            'Bajaj Dominar 400.jpg',
            'Bajaj dominar 400.jpg',
        ],
        'search_terms': ['Bajaj Dominar 400 bike', 'Dominar 400 motorcycle India']
    },
    {
        'name': 'Freedom 125 CNG',
        'out_file': 'bajaj_freedom_125_cng.png',
        'direct_files': [
            'Bajaj Freedom 125.jpg',
            'Bajaj Freedom 125 CNG.jpg',
        ],
        'search_terms': ['Bajaj Freedom CNG motorcycle', 'Bajaj 125 CNG bike India']
    },
    {
        'name': 'Pulsar 220F',
        'out_file': 'bajaj_pulsar_220f.png',
        'direct_files': [
            'Bajaj Pulsar 220F.jpg',
            'Bajaj Pulsar 220 F.jpg',
            'Bajaj Pulsar220F.jpg',
            'Bajaj Pulsar 220.jpg',
        ],
        'search_terms': ['Bajaj Pulsar 220 motorcycle', 'Pulsar 220F India bike']
    },
    {
        'name': 'Pulsar N160',
        'out_file': 'bajaj_pulsar_n160.png',
        'direct_files': [
            'Bajaj Pulsar N160.jpg',
            'Bajaj Pulsar N 160.jpg',
        ],
        'search_terms': ['Bajaj Pulsar 160 motorcycle', 'Bajaj Pulsar NS160 bike']
    },
    {
        'name': 'Pulsar N250',
        'out_file': 'bajaj_pulsar_n250.png',
        'direct_files': [
            'Bajaj Pulsar N250.jpg',
            'Bajaj Pulsar 250.jpg',
        ],
        'search_terms': ['Bajaj Pulsar 250 motorcycle', 'Bajaj Pulsar NS200 naked']
    },
    {
        'name': 'Pulsar NS160',
        'out_file': 'bajaj_pulsar_ns160.png',
        'direct_files': [
            'Bajaj Pulsar NS160.jpg',
            'Bajaj Pulsar NS 160.jpg',
        ],
        'search_terms': ['Bajaj Pulsar NS 160 motorcycle', 'Bajaj Pulsar naked sport 160']
    },
    {
        'name': 'Pulsar NS200',
        'out_file': 'bajaj_pulsar_ns200.png',
        'direct_files': [
            'Bajaj Pulsar 200 ns grey and red.jpg',
            'Bajaj Pulsar NS200.jpg',
            'Bajaj Pulsar 200 NS.jpg',
        ],
        'search_terms': ['Bajaj Pulsar 200 NS motorcycle', 'Bajaj Pulsar NS 200']
    },
]

print("=" * 60)
print("BAJAJ RETRY DOWNLOADER - Working Process")
print("=" * 60)

success = []
failed = []

for model in RETRY_MODELS:
    out_path = os.path.join(OUT_DIR, model['out_file'])
    print(f"\n[{model['name']}]")
    
    img_url = None

    # Try direct known filenames first
    for fname in model.get('direct_files', []):
        print(f"  Trying direct: {fname}")
        img_url = get_direct_url(fname)
        if img_url:
            break
        time.sleep(1)

    # Fallback to search
    if not img_url:
        for term in model.get('search_terms', []):
            print(f"  Searching: {term}")
            img_url = search_wikimedia(term)
            if img_url:
                break
            time.sleep(2)

    if img_url:
        ok = download(img_url, out_path)
        if ok:
            success.append(model['name'])
        else:
            failed.append(model['name'])
    else:
        print(f"  No photo found for {model['name']}")
        failed.append(model['name'])

    time.sleep(2)  # Pause between models

print("\n" + "=" * 60)
print(f"SUCCESS ({len(success)}): {success}")
print(f"FAILED  ({len(failed)}): {failed}")
print("=" * 60)
