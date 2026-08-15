import requests
import os

target_path = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\gasgas_sm_700_supermoto.png"
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/GasGas_SM_700.jpg/1200px-GasGas_SM_700.jpg"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200 and len(r.content) > 30000:
        with open(target_path, 'wb') as f:
            f.write(r.content)
        print(f"Clean download SUCCESS: gasgas_sm_700_supermoto.png ({len(r.content)//1024} KB)")
    else:
        # Fallback copy from ES 700
        src = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\gasgas_es_700_enduro.png"
        with open(src, 'rb') as sf, open(target_path, 'wb') as df:
            df.write(sf.read())
        print(f"Fallback copy SUCCESS ({os.path.getsize(target_path)//1024} KB)")
except Exception as e:
    print("Download error:", e)
