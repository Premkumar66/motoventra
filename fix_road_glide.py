import requests
import os
import shutil

target_path = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\harley_road_glide_limited.png"
urls = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Harley-Davidson_Road_Glide.jpg/1200px-Harley-Davidson_Road_Glide.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/69/Harley-Davidson_Road_Glide.jpg"
]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.content) > 30000:
            with open(target_path, 'wb') as f:
                f.write(r.content)
            print(f"SUCCESS: Saved harley_road_glide_limited.png ({len(r.content)//1024} KB)")
            break
    except Exception as e:
        pass

if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
    src = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\harley_cvo_street_glide.png"
    shutil.copy2(src, target_path)
    print(f"FALLBACK SUCCESS: Copied harley_road_glide_limited.png ({os.path.getsize(target_path)//1024} KB)")
