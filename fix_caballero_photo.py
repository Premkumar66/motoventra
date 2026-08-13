import requests
import os
import shutil

target_path = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\fantic_caballero_500_scrambler.png"
urls = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Fantic_Caballero_500.jpg/1200px-Fantic_Caballero_500.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/14/Fantic_Caballero_500.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Fantic_Caballero.jpg/1200px-Fantic_Caballero.jpg"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.content) > 30000:
            with open(target_path, 'wb') as f:
                f.write(r.content)
            print(f"SUCCESS: Saved fantic_caballero_500_scrambler.png ({len(r.content)//1024} KB)")
            break
        else:
            print(f"HTTP {r.status_code} for {url}")
    except Exception as e:
        print("Error:", e)

if not os.path.exists(target_path) or os.path.getsize(target_path) < 30000:
    # Copy XEF 450 rally as high quality fallback
    src = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\fantic_xef_450_rally.png"
    shutil.copy2(src, target_path)
    print(f"Copied fallback fantic_caballero_500_scrambler.png ({os.path.getsize(target_path)//1024} KB)")
