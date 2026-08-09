import os
import shutil
import sqlite3

GEN_DIR = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb"
TARGET_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

CFMOTO_MODELS = [
    ("300NK Naked", "cfmoto_300nk_naked", "cfmoto_300nk_naked.png"),
    ("450SR Supersport", "cfmoto_450sr_supersport", "cfmoto_450sr_supersport.png"),
    ("650MT Tourer", "cfmoto_650mt_tourer", "cfmoto_650mt_tourer.png"),
    ("800NK Hyper Naked", "cfmoto_800nk_hyper_naked", "cfmoto_800nk_hyper_naked.png")
]

print("=== Step 1: Copying High-Res CFMOTO Model Images ===")
for model_name, gen_prefix, target_name in CFMOTO_MODELS:
    target_path = os.path.join(TARGET_DIR, target_name)
    for f in os.listdir(GEN_DIR):
        if f.startswith(gen_prefix) and f.endswith(".png"):
            src_path = os.path.join(GEN_DIR, f)
            shutil.copy2(src_path, target_path)
            size_kb = os.path.getsize(target_path) // 1024
            print(f"  [COPY OK] {model_name:22} -> {target_name:30} ({size_kb} KB)")
            break

print("\n=== Step 2: Updating Database thumbnail_url for CFMOTO Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%cfmoto%'")
brand_id = cur.fetchone()[0]

for model_name, _, target_name in CFMOTO_MODELS:
    img_url = f"/static/images/{target_name}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )
    print(f"  [DB OK] {model_name:22} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Step 3: Verifying CFMOTO Images on Disk ===")
for model_name, _, target_name in CFMOTO_MODELS:
    fp = os.path.join(TARGET_DIR, target_name)
    exists = os.path.exists(fp)
    size_kb = (os.path.getsize(fp) // 1024) if exists else 0
    print(f"  CFMOTO {model_name:22} | {target_name:30} | {size_kb:6} KB | Exists: {exists}")
