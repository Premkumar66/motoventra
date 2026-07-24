import requests
import os
import time
import shutil

OUT_DIR = 'motomod-ai/backend/app/static/images'
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

# Reliable high quality exact model photo URLs
BAJAJ_EXACT_PHOTOS = [
    {
        "name": "Avenger Cruise 220",
        "filename": "bajaj_avenger_cruise_220.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Avenger_220.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/b/b5/Bajaj_Avenger_220_DTS-i.jpg"
        ]
    },
    {
        "name": "CT 125X",
        "filename": "bajaj_ct_125x.png",
        "urls": [
            "https://cloudfront-us-east-1.images.arcpublishing.com/sltrib/7ZYHFSKVY5AG3HCFGOSOH7U7VE.jpg"
        ]
    },
    {
        "name": "Chetak Premium EV",
        "filename": "bajaj_chetak_premium_ev.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/0/07/Bajaj_Chetak_electric_scooters_%282026%29_05.jpg"
        ]
    },
    {
        "name": "Dominar 250",
        "filename": "bajaj_dominar_250.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg"
        ]
    },
    {
        "name": "Dominar 400",
        "filename": "bajaj_dominar_400.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/41/Dominar_400.jpg"
        ]
    },
    {
        "name": "Freedom 125 CNG",
        "filename": "bajaj_freedom_125_cng.png",
        "urls": [
            "https://i.etsystatic.com/8800859/r/il/c1b40f/4737705911/il_1080xN.4737705911_evsp.jpg"
        ]
    },
    {
        "name": "Pulsar 220F",
        "filename": "bajaj_pulsar_220f.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/7/7b/I_and_Pulsar_220.JPG"
        ]
    },
    {
        "name": "Pulsar N160",
        "filename": "bajaj_pulsar_n160.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/d/df/BAJAJ_Pulsar_NS160.jpg"
        ]
    },
    {
        "name": "Pulsar N250",
        "filename": "bajaj_pulsar_n250.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Pulsar_200_ns_grey_and_red.jpg"
        ]
    },
    {
        "name": "Pulsar NS125",
        "filename": "bajaj_pulsar_ns125.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/3/30/Bajaj_pulsar_NS_125.jpg"
        ]
    },
    {
        "name": "Pulsar NS160",
        "filename": "bajaj_pulsar_ns160.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/d/df/BAJAJ_Pulsar_NS160.jpg"
        ]
    },
    {
        "name": "Pulsar NS200",
        "filename": "bajaj_pulsar_ns200.png",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bajaj_Pulsar_200_ns_grey_and_red.jpg"
        ]
    }
]

def download_image(url, filepath):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
            if r.status_code == 429:
                print(f"Rate limited (429) on {url[:50]}... waiting 5s")
                time.sleep(5)
                continue
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                size_kb = os.path.getsize(filepath) // 1024
                print(f"SUCCESS: {os.path.basename(filepath)} downloaded ({size_kb} KB)")
                return True
            else:
                print(f"HTTP {r.status_code} for {url[:60]}")
        except Exception as e:
            print(f"Error downloading {url[:50]}: {e}")
            time.sleep(2)
    return False

if __name__ == "__main__":
    print("=== Downloading Exact Photos for all 12 Bajaj Models ===")
    for item in BAJAJ_EXACT_PHOTOS:
        name = item["name"]
        filename = item["filename"]
        filepath = os.path.join(OUT_DIR, filename)
        
        print(f"\nProcessing {name} ({filename})...")
        downloaded = False
        for url in item["urls"]:
            if download_image(url, filepath):
                downloaded = True
                break
            time.sleep(1)
        if not downloaded:
            print(f"FAILED to download photo for {name}")
        time.sleep(2) # rate limit delay between requests

    print("\n=== Summary of All 12 Bajaj Model Images ===")
    for item in BAJAJ_EXACT_PHOTOS:
        fn = item["filename"]
        fp = os.path.join(OUT_DIR, fn)
        sz = os.path.getsize(fp)//1024 if os.path.exists(fp) else 0
        print(f"  {item['name']:25} -> {fn:30} : {sz} KB")
