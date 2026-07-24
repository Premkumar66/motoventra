import requests
import json
import re
import os
import urllib.parse
import shutil

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)

MODELS = [
    ("Avenger Cruise 220", "bajaj_avenger_cruise_220.png", "Bajaj Avenger Cruise 220 side profile bike photo"),
    ("CT 125X", "bajaj_ct_125x.png", "Bajaj CT 125X side profile bike photo"),
    ("Chetak Premium EV", "bajaj_chetak_premium_ev.png", "Bajaj Chetak Premium EV scooter side view photo"),
    ("Dominar 250", "bajaj_dominar_250.png", "Bajaj Dominar 250 side profile bike photo"),
    ("Dominar 400", "bajaj_dominar_400.png", "Bajaj Dominar 400 side profile bike photo"),
    ("Freedom 125 CNG", "bajaj_freedom_125_cng.png", "Bajaj Freedom 125 CNG bike side view photo"),
    ("Pulsar 220F", "bajaj_pulsar_220f.png", "Bajaj Pulsar 220F side profile bike photo"),
    ("Pulsar N160", "bajaj_pulsar_n160.png", "Bajaj Pulsar N160 side profile bike photo"),
    ("Pulsar N250", "bajaj_pulsar_n250.png", "Bajaj Pulsar N250 side profile bike photo"),
    ("Pulsar NS125", "bajaj_pulsar_ns125.png", "Bajaj Pulsar NS125 side profile bike photo"),
    ("Pulsar NS160", "bajaj_pulsar_ns160.png", "Bajaj Pulsar NS160 side profile bike photo"),
    ("Pulsar NS200", "bajaj_pulsar_ns200.png", "Bajaj Pulsar NS200 side profile bike photo"),
]

def fetch_bing_image_urls(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&FORM=HDRSC2"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', r.text)
        if not murls:
            murls = re.findall(r'"murl":"(https?://[^"]+)"', r.text)
        
        valid_urls = []
        for murl in murls:
            clean_url = murl.replace('\\/', '/')
            if any(clean_url.lower().endswith(ext) or ext in clean_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                valid_urls.append(clean_url)
        return valid_urls
    except Exception as e:
        print(f"Bing search error for {query}: {e}")
    return []

def download_and_save(urls, filename):
    filepath = os.path.join(OUT_DIR, filename)
    for url in urls[:5]:  # Try top 5 URLs
        try:
            r = requests.get(url, headers=HEADERS, timeout=12, stream=True)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                size_kb = os.path.getsize(filepath) // 1024
                if size_kb > 25:
                    print(f"SUCCESS: Saved {filename} ({size_kb} KB) from {url[:70]}...")
                    return True
                else:
                    print(f"Skip small image ({size_kb} KB): {url[:60]}")
        except Exception as e:
            print(f"Failed URL {url[:60]}: {e}")
    return False

if __name__ == "__main__":
    print("Collecting exact model pictures for all 12 Bajaj bikes via Bing Search...")
    success_count = 0
    for name, filename, query in MODELS:
        print(f"\nSearching for {name} ({query})...")
        urls = fetch_bing_image_urls(query)
        if urls:
            if download_and_save(urls, filename):
                success_count += 1
            else:
                print(f"Retrying alternative query for {name}...")
                alt_urls = fetch_bing_image_urls(f"Bajaj {name} official bike picture studio")
                if download_and_save(alt_urls, filename):
                    success_count += 1
        else:
            print(f"No Bing URLs found for {name}")

    print(f"\nFinished! Successfully updated {success_count}/12 images.")
