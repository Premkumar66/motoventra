import requests
import json
import re
import os
import urllib.parse
import shutil

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

OUT_DIR = 'motomod-ai/backend/app/static/images'

MODELS = [
    ("Avenger Cruise 220", "bajaj_avenger_cruise_220.png", "Bajaj Avenger Cruise 220 official studio photo transparent or white background motorcycle"),
    ("CT 125X", "bajaj_ct_125x.png", "Bajaj CT 125X official bike photo side profile"),
    ("Chetak Premium EV", "bajaj_chetak_premium_ev.png", "Bajaj Chetak Premium EV scooter official photo side view"),
    ("Dominar 250", "bajaj_dominar_250.png", "Bajaj Dominar 250 bike official photo side profile"),
    ("Dominar 400", "bajaj_dominar_400.png", "Bajaj Dominar 400 bike official photo side profile"),
    ("Freedom 125 CNG", "bajaj_freedom_125_cng.png", "Bajaj Freedom 125 CNG motorcycle official photo side view"),
    ("Pulsar 220F", "bajaj_pulsar_220f.png", "Bajaj Pulsar 220F bike official studio photo side view"),
    ("Pulsar N160", "bajaj_pulsar_n160.png", "Bajaj Pulsar N160 bike official photo side profile"),
    ("Pulsar N250", "bajaj_pulsar_n250.png", "Bajaj Pulsar N250 bike official photo side profile"),
    ("Pulsar NS125", "bajaj_pulsar_ns125.png", "Bajaj Pulsar NS125 bike official photo side profile"),
    ("Pulsar NS160", "bajaj_pulsar_ns160.png", "Bajaj Pulsar NS160 bike official photo side profile"),
    ("Pulsar NS200", "bajaj_pulsar_ns200.png", "Bajaj Pulsar NS200 bike official studio photo side profile"),
]

def fetch_ddg_image_url(query):
    try:
        # Step 1: get vqd
        req_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
        res = requests.get(req_url, headers=HEADERS, timeout=10)
        vqd_match = re.search(r'vqd=([\d-]+)\&', res.text)
        if not vqd_match:
            vqd_match = re.search(r'vqd=["\']([\d-]+)["\']', res.text)
        if not vqd_match:
            print(f"Could not find vqd for query: {query}")
            return None
        vqd = vqd_match.group(1)

        # Step 2: fetch images
        params = {
            'l': 'us-en',
            'o': 'json',
            'q': query,
            'vqd': vqd,
            'f': ',,,',
            'p': '1'
        }
        img_res = requests.get("https://duckduckgo.com/i.js", headers=HEADERS, params=params, timeout=10)
        data = img_res.json()
        results = data.get('results', [])
        for r in results:
            img_url = r.get('image')
            if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return img_url
    except Exception as e:
        print(f"DDG search error for {query}: {e}")
    return None

def download_and_save(url, filename):
    filepath = os.path.join(OUT_DIR, filename)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(f"✅ Saved {filename} ({os.path.getsize(filepath)//1024} KB) from {url[:60]}...")
            return True
    except Exception as e:
        print(f"❌ Download error for {filename}: {e}")
    return False

if __name__ == "__main__":
    print("Starting exact image collection for Bajaj models...")
    for name, filename, query in MODELS:
        print(f"\nSearching for exact model picture: {name}...")
        img_url = fetch_ddg_image_url(query)
        if img_url:
            success = download_and_save(img_url, filename)
            if not success:
                print(f"Failed download for {name}")
        else:
            print(f"No URL found for {name}")
