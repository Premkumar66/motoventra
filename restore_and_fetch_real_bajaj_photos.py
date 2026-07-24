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

# Direct high quality authentic photos from Wikimedia and trusted sources
DIRECT_MOTORCYCLE_PHOTOS = {
    "bajaj_avenger_cruise_220.png": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Bajaj_avenger_220.jpg",
    "bajaj_chetak_premium_ev.png": "https://upload.wikimedia.org/wikipedia/commons/0/07/Bajaj_Chetak_electric_scooters_%282026%29_05.jpg",
    "bajaj_dominar_250.png": "https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg",
    "bajaj_dominar_400.png": "https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg",
    "bajaj_pulsar_220f.png": "https://upload.wikimedia.org/wikipedia/commons/7/7b/I_and_Pulsar_220.JPG",
    "bajaj_pulsar_ns125.png": "https://upload.wikimedia.org/wikipedia/commons/3/30/Bajaj_pulsar_NS_125.jpg",
    "bajaj_pulsar_ns160.png": "https://upload.wikimedia.org/wikipedia/commons/d/df/BAJAJ_Pulsar_NS160.jpg",
    "bajaj_pulsar_ns200.png": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Pulsar_200_ns_grey_and_red.jpg",
}

# For the remaining models (CT 125X, Freedom 125 CNG, Pulsar N160, Pulsar N250),
# search specifically on automotive domains
MOTORCYCLE_SEARCHES = [
    ("CT 125X", "bajaj_ct_125x.png", "Bajaj CT 125X motorcycle site:bikewale.com OR site:bikedekho.com OR site:autocarindia.com"),
    ("Freedom 125 CNG", "bajaj_freedom_125_cng.png", "Bajaj Freedom 125 CNG motorcycle site:bikewale.com OR site:bikedekho.com OR site:autocarindia.com"),
    ("Pulsar N160", "bajaj_pulsar_n160.png", "Bajaj Pulsar N160 motorcycle site:bikewale.com OR site:bikedekho.com OR site:autocarindia.com"),
    ("Pulsar N250", "bajaj_pulsar_n250.png", "Bajaj Pulsar N250 motorcycle site:bikewale.com OR site:bikedekho.com OR site:autocarindia.com"),
]

def download_file(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            size_kb = os.path.getsize(filepath) // 1024
            if size_kb > 50:
                print(f"SUCCESS: Saved {os.path.basename(filepath)} ({size_kb} KB) from {url[:70]}...")
                return True
            else:
                print(f"FAILED: File too small ({size_kb} KB) for {os.path.basename(filepath)}")
        else:
            print(f"HTTP {r.status_code} for {url}")
    except Exception as e:
        print(f"Download error: {e}")
    return False

def search_bing_moto_image(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&FORM=HDRSC2"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', r.text)
        if not murls:
            murls = re.findall(r'"murl":"(https?://[^"]+)"', r.text)
        
        for murl in murls:
            clean_url = murl.replace('\\/', '/')
            # Only keep URLs from bike/auto sites or images with motorcycle keywords in URL
            if any(domain in clean_url.lower() for domain in ['bikewale', 'bikedekho', 'autocar', 'zigwheels', 'motorbeam', 'carandbike', 'bajajauto', 'wikimedia', 'wikimedia.org', 'cloudfront']):
                return clean_url
            if any(kw in clean_url.lower() for kw in ['bajaj', 'pulsar', 'motorcycle', 'bike']):
                return clean_url
    except Exception as e:
        print(f"Search error for {query}: {e}")
    return None

if __name__ == "__main__":
    print("--- 1. Downloading direct authentic Wikimedia motorcycle photos ---")
    for filename, url in DIRECT_MOTORCYCLE_PHOTOS.items():
        filepath = os.path.join(OUT_DIR, filename)
        print(f"Downloading real photo for {filename}...")
        download_file(url, filepath)

    print("\n--- 2. Searching motorcycle media sites for remaining models ---")
    for name, filename, query in MOTORCYCLE_SEARCHES:
        filepath = os.path.join(OUT_DIR, filename)
        print(f"Searching real motorcycle photo for {name}...")
        img_url = search_bing_moto_image(query)
        if not img_url:
            # Fallback search query
            img_url = search_bing_moto_image(f"Bajaj {name} motorcycle bike site:bikewale.com OR site:bikedekho.com")
        if not img_url:
            img_url = search_bing_moto_image(f"Bajaj {name} motorcycle profile view")
            
        if img_url:
            download_file(img_url, filepath)
        else:
            print(f"Could not find motorcycle image for {name}")

    print("\n--- 3. Verifying final image file sizes ---")
    for fname in sorted(os.listdir(OUT_DIR)):
        if fname.startswith("bajaj_"):
            fp = os.path.join(OUT_DIR, fname)
            print(f"  {fname:30} : {os.path.getsize(fp)//1024:6} KB")
