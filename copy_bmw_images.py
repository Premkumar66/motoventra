import os
import shutil
import sqlite3
import requests

GEN_DIR = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb"
TARGET_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

BMW_MODEL_FILES = {
    "CE02 eParkourer": ("bmw_ce02_eparkourer", "bmw_ce02_eparkourer.png"),
    "CE04 Electric": ("bmw_ce04_electric", "bmw_ce04_electric.png"),
    "F900R": ("bmw_f900r", "bmw_f900r.png"),
    "F900XR": ("bmw_f900xr", "bmw_f900xr.png"),
    "G310GS": ("bmw_g310gs", "bmw_g310gs.png"),
    "G310R": ("bmw_g310r", "bmw_g310r.png"),
    "M1000RR": ("bmw_m1000rr", "bmw_m1000rr.png"),
    "R1250GS Adventure": ("bmw_r1250gs_adv", "bmw_r1250gs_adventure.png"),
    "R1300GS": ("bmw_r1300gs", "bmw_r1300gs.png"),
    "R18 Cruiser": ("bmw_r18_cruiser", "bmw_r18_cruiser.png"),
    "S1000RR": ("bmw_s1000rr", "bmw_s1000rr.png"),
    "S1000XR": (None, "bmw_s1000xr.png"),
}

print("=== Step 1: Copying High-Res BMW Model Images ===")
for model_name, (gen_prefix, target_name) in BMW_MODEL_FILES.items():
    target_path = os.path.join(TARGET_DIR, target_name)
    found_gen = False
    
    if gen_prefix:
        for f in os.listdir(GEN_DIR):
            if f.startswith(gen_prefix) and f.endswith(".png"):
                src_path = os.path.join(GEN_DIR, f)
                shutil.copy2(src_path, target_path)
                size_kb = os.path.getsize(target_path) // 1024
                print(f"  [GEN OK] {model_name:20} -> {target_name:30} ({size_kb} KB)")
                found_gen = True
                break

    if not found_gen:
        # Try fetching real photo from Wikimedia or fallback
        if not os.path.exists(target_path) or os.path.getsize(target_path) < 20000:
            wm_url = "https://upload.wikimedia.org/wikipedia/commons/e/eb/BMW_S1000XR_red_2016.jpg"
            try:
                r = requests.get(wm_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                if r.status_code == 200:
                    with open(target_path, 'wb') as f:
                        f.write(r.content)
                    print(f"  [WM OK]  {model_name:20} -> {target_name:30} ({len(r.content)//1024} KB)")
            except Exception as e:
                print(f"  [WARN]   {model_name}: {e}")
        else:
            print(f"  [EXISTING] {model_name:18} -> {target_name:30} ({os.path.getsize(target_path)//1024} KB)")

print("\n=== Step 2: Updating Database thumbnail_url for BMW Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%bmw%'")
brand_row = cur.fetchone()
if not brand_row:
    print("Error: BMW brand not found in DB!")
    exit(1)
bmw_brand_id = brand_row[0]

updated_count = 0
for model_name, (_, target_name) in BMW_MODEL_FILES.items():
    img_url = f"/static/images/{target_name}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, bmw_brand_id, model_name)
    )
    if cur.rowcount > 0:
        updated_count += cur.rowcount
        print(f"  [DB OK] {model_name:22} -> {img_url}")
    else:
        print(f"  [DB WARN] {model_name:22} not matched")

conn.commit()
conn.close()
print(f"Total DB rows updated: {updated_count}")

print("\n=== Step 3: Verifying BMW Image Files on Disk ===")
for model_name, (_, target_name) in BMW_MODEL_FILES.items():
    fp = os.path.join(TARGET_DIR, target_name)
    exists = os.path.exists(fp)
    size_kb = (os.path.getsize(fp) // 1024) if exists else 0
    print(f"  BMW {model_name:22} | {target_name:30} | {size_kb:6} KB | Exists: {exists}")
