import urllib.request
import os
import time

images = {
    "benelli_tnt_600i_inline_4.png": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Benelli_TnT_1130_Caf%C3%A9_Racer.JPG",
    "benelli_trk_502x.png": "https://upload.wikimedia.org/wikipedia/commons/f/f6/TRK_X.jpg"
}

target_dir = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
headers = {"User-Agent": "MotoVentraApp/1.0 (contact@motoventra.com; research project)"}

for filename, url in images.items():
    dest = os.path.join(target_dir, filename)
    print(f"Downloading {filename} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        print(f"SUCCESS: Saved {filename} ({os.path.getsize(dest)} bytes)")
    except Exception as e:
        print(f"ERROR downloading {filename}: {e}")
    time.sleep(3)
