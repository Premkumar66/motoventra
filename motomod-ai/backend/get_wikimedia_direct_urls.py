import urllib.request
import urllib.parse
import json
import os

files = {
    "benelli_502c_cruiser.png": "File:Benelli 502C.jpg",
    "benelli_imperiale_400.png": "File:Benelli Imperiale.jpg",
    "benelli_leoncino_500.png": "File:Benelli - Leoncino.jpg",
    "benelli_tnt_600i_inline_4.png": "File:Benelli TNT 899 S (1).jpg",
    "benelli_trk_502x.png": "File:TRK X.jpg"
}

target_dir = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
headers = {"User-Agent": "MotoVentraPlatform/1.0 (contact@motoventra.com)"}

for filename, title in files.items():
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data['query']['pages']
            for p in pages.values():
                if 'imageinfo' in p:
                    img_url = p['imageinfo'][0]['url']
                    print(f"Fetching {filename} from {img_url}...")
                    img_req = urllib.request.Request(img_url, headers=headers)
                    dest = os.path.join(target_dir, filename)
                    with urllib.request.urlopen(img_req) as img_resp, open(dest, 'wb') as f:
                        f.write(img_resp.read())
                    print(f"SUCCESS: Saved {filename} ({os.path.getsize(dest)} bytes)")
                else:
                    print(f"No imageinfo for {title}")
    except Exception as e:
        print(f"Error for {title}: {e}")
