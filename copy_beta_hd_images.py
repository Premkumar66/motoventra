import os
import shutil
import sqlite3

GEN_DIR = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb"
TARGET_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

# Find generated files
evo_file = None
xtrainer_file = None

for f in os.listdir(GEN_DIR):
    if f.startswith("beta_evo_300_trial_hd"):
        evo_file = os.path.join(GEN_DIR, f)
    elif f.startswith("beta_xtrainer_300_enduro_hd"):
        xtrainer_file = os.path.join(GEN_DIR, f)

if evo_file:
    target_evo = os.path.join(TARGET_DIR, "beta_evo_300_trial.png")
    shutil.copy2(evo_file, target_evo)
    print(f"Copied EVO 300 Trial HD ({os.path.getsize(target_evo)//1024} KB)")

if xtrainer_file:
    target_xtrainer = os.path.join(TARGET_DIR, "beta_xtrainer_300_enduro.png")
    shutil.copy2(xtrainer_file, target_xtrainer)
    print(f"Copied Xtrainer 300 Enduro HD ({os.path.getsize(target_xtrainer)//1024} KB)")

print("\n=== Updating Database thumbnail_url for Beta Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE name='Beta'")
beta_id = cur.fetchone()[0]

beta_models = [
    ("EVO 300 Trial", "beta_evo_300_trial.png"),
    ("RR 390 4T", "beta_rr_390_4t.png"),
    ("Xtrainer 300 Enduro", "beta_xtrainer_300_enduro.png")
]

for name, filename in beta_models:
    img_url = f"/static/images/{filename}"
    cur.execute("UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?", (img_url, beta_id, name))
    print(f"  [DB OK] {name:22} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Final Verification of Beta Images ===")
for name, filename in beta_models:
    fp = os.path.join(TARGET_DIR, filename)
    sz = os.path.getsize(fp) // 1024 if os.path.exists(fp) else 0
    print(f"  Beta {name:22} | {filename:30} | {sz:5} KB | Exists: {os.path.exists(fp)}")
