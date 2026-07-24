"""
Download REAL authentic camera photos for all 12 Bajaj models
from Wikimedia Commons using MediaWiki API.
Working process: Search API -> Get direct URL -> Download full-res image -> Save
"""
import requests
import shutil
import os
import time

HEADERS = {'User-Agent': 'MotoVentra/1.0 (educational project)'}
OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)

def get_wikimedia_image_url(search_terms):
    """Try multiple search terms and return the best direct image URL from Wikimedia."""
    for term in search_terms:
        try:
            # Search for files
            search_url = 'https://commons.wikimedia.org/w/api.php'
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': f'filetype:bitmap {term}',
                'srnamespace': 6,  # File namespace
                'srlimit': 5,
                'format': 'json'
            }
            r = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
            results = r.json().get('query', {}).get('search', [])
            
            for result in results:
                title = result['title']  # e.g. "File:Bajaj_Pulsar_NS200.jpg"
                # Get direct URL
                info_params = {
                    'action': 'query',
                    'titles': title,
                    'prop': 'imageinfo',
                    'iiprop': 'url|size|mime',
                    'format': 'json'
                }
                ir = requests.get(search_url, params=info_params, headers=HEADERS, timeout=15)
                pages = ir.json().get('query', {}).get('pages', {})
                for page in pages.values():
                    ii = page.get('imageinfo', [{}])[0]
                    url = ii.get('url', '')
                    size = ii.get('size', 0)
                    mime = ii.get('mime', '')
                    # Only accept real photos (JPEG/PNG), not SVG/tiny files
                    if url and size > 100000 and mime in ('image/jpeg', 'image/png', 'image/webp'):
                        print(f"  Found: {title} ({size//1024} KB) via term '{term}'")
                        return url, title
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error searching '{term}': {e}")
            continue
    return None, None

def download_image(url, out_path):
    """Download image from URL to out_path."""
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        size = os.path.getsize(out_path)
        print(f"  Saved: {out_path} ({size//1024} KB)")
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        return False

# ─── All 12 Bajaj Models with multiple search terms ──────────────────────────
BAJAJ_MODELS = [
    {
        'name': 'Avenger Cruise 220',
        'out_file': 'bajaj_avenger_cruise_220.png',
        'search_terms': [
            'Bajaj Avenger Cruise 220',
            'Bajaj Avenger 220 cruise motorcycle',
            'Bajaj Avenger 220',
        ]
    },
    {
        'name': 'CT 125X',
        'out_file': 'bajaj_ct_125x.png',
        'search_terms': [
            'Bajaj CT 125X motorcycle',
            'Bajaj CT125X',
            'Bajaj CT 125',
        ]
    },
    {
        'name': 'Chetak Premium EV',
        'out_file': 'bajaj_chetak_premium_ev.png',
        'search_terms': [
            'Bajaj Chetak electric scooter',
            'Bajaj Chetak EV',
            'Chetak electric 2021',
        ]
    },
    {
        'name': 'Dominar 250',
        'out_file': 'bajaj_dominar_250.png',
        'search_terms': [
            'Bajaj Dominar 250 motorcycle',
            'Bajaj Dominar 250',
        ]
    },
    {
        'name': 'Dominar 400',
        'out_file': 'bajaj_dominar_400.png',
        'search_terms': [
            'Bajaj Dominar 400 motorcycle',
            'Bajaj Dominar 400',
        ]
    },
    {
        'name': 'Freedom 125 CNG',
        'out_file': 'bajaj_freedom_125_cng.png',
        'search_terms': [
            'Bajaj Freedom 125 CNG motorcycle',
            'Bajaj Freedom CNG bike',
        ]
    },
    {
        'name': 'Pulsar 220F',
        'out_file': 'bajaj_pulsar_220f.png',
        'search_terms': [
            'Bajaj Pulsar 220F motorcycle',
            'Bajaj Pulsar 220 F bike',
            'Bajaj Pulsar 220',
        ]
    },
    {
        'name': 'Pulsar N160',
        'out_file': 'bajaj_pulsar_n160.png',
        'search_terms': [
            'Bajaj Pulsar N160 motorcycle',
            'Bajaj Pulsar N160',
        ]
    },
    {
        'name': 'Pulsar N250',
        'out_file': 'bajaj_pulsar_n250.png',
        'search_terms': [
            'Bajaj Pulsar N250 motorcycle',
            'Bajaj Pulsar N250',
        ]
    },
    {
        'name': 'Pulsar NS125',
        'out_file': 'bajaj_pulsar_ns125.png',
        'search_terms': [
            'Bajaj Pulsar NS125 motorcycle',
            'Bajaj Pulsar NS 125',
        ]
    },
    {
        'name': 'Pulsar NS160',
        'out_file': 'bajaj_pulsar_ns160.png',
        'search_terms': [
            'Bajaj Pulsar NS160 motorcycle',
            'Bajaj Pulsar NS 160',
        ]
    },
    {
        'name': 'Pulsar NS200',
        'out_file': 'bajaj_pulsar_ns200.png',
        'search_terms': [
            'Bajaj Pulsar NS200 motorcycle',
            'Bajaj Pulsar NS 200',
            'Bajaj Pulsar 200 NS',
        ]
    },
]

print("=" * 60)
print("BAJAJ MODEL REAL PHOTO DOWNLOADER - Working Process")
print("=" * 60)

success = []
failed = []

for model in BAJAJ_MODELS:
    out_path = os.path.join(OUT_DIR, model['out_file'])
    print(f"\n[{model['name']}]")
    print(f"  Target: {out_path}")
    
    url, title = get_wikimedia_image_url(model['search_terms'])
    
    if url:
        ok = download_image(url, out_path)
        if ok:
            success.append(model['name'])
        else:
            failed.append(model['name'])
    else:
        print(f"  No Wikimedia photo found for {model['name']}")
        failed.append(model['name'])
    
    time.sleep(0.5)

print("\n" + "=" * 60)
print(f"SUCCESS ({len(success)}): {success}")
print(f"FAILED  ({len(failed)}): {failed}")
print("=" * 60)
