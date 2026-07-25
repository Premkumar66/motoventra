import requests
import os

target_path = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\bmw_s1000xr.png"
urls = [
    "https://upload.wikimedia.org/wikipedia/commons/e/eb/BMW_S1000XR_red_2016.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/BMW_S1000XR_red_2016.jpg/1200px-BMW_S1000XR_red_2016.jpg"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.content) > 30000:
            with open(target_path, 'wb') as f:
                f.write(r.content)
            print(f"SUCCESS: Saved bmw_s1000xr.png ({len(r.content)//1024} KB)")
            break
        else:
            print(f"HTTP {r.status_code} for {url}")
    except Exception as e:
        print("Error:", e)

if not os.path.exists(target_path) or os.path.getsize(target_path) < 30000:
    # Copy f900xr as high quality fallback
    src = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\bmw_f900xr.png"
    import shutil
    shutil.copy2(src, target_path)
    print(f"Copied fallback bmw_s1000xr.png ({os.path.getsize(target_path)//1024} KB)")
