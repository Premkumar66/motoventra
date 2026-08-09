from PIL import Image
import os
import sqlite3

GRID_IMG_PATH = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb\media__1786268849329.jpg"
TARGET_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"
DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

# Grid mapping (Row, Col) -> Model Name & File Name
# 3 Rows x 4 Cols
GRID_MODELS = [
    # Row 1
    (0, 0, "Avenger Cruise 220", "bajaj_avenger_cruise_220.png"),
    (0, 1, "CT 125X", "bajaj_ct_125x.png"),
    (0, 2, "Chetak Premium EV", "bajaj_chetak_premium_ev.png"),
    (0, 3, "Dominar 250", "bajaj_dominar_250.png"),

    # Row 2
    (1, 0, "Dominar 400", "bajaj_dominar_400.png"),
    (1, 1, "Freedom 125 CNG", "bajaj_freedom_125_cng.png"),
    (1, 2, "Pulsar 220F", "bajaj_pulsar_220f.png"),
    (1, 3, "Pulsar N160", "bajaj_pulsar_n160.png"),

    # Row 3
    (2, 0, "Pulsar N250", "bajaj_pulsar_n250.png"),
    (2, 1, "Pulsar NS125", "bajaj_pulsar_ns125.png"),
    (2, 2, "Pulsar NS160", "bajaj_pulsar_ns160.png"),
    (2, 3, "Pulsar NS200", "bajaj_pulsar_ns200.png"),
]

print("=== Opening User Uploaded Bajaj Grid Image ===")
img = Image.open(GRID_IMG_PATH)
width, height = img.size
print(f"Uploaded Grid Dimensions: {width} x {height} px")

# Calculate cell dimensions
cell_w = width / 4.0
cell_h = height / 3.0

print("\n=== Cropping and Replacing All 12 Bajaj Model Images ===")
os.makedirs(TARGET_DIR, exist_ok=True)

for row, col, model_name, filename in GRID_MODELS:
    # Compute bounding box
    left = int(col * cell_w)
    top = int(row * cell_h)
    right = int((col + 1) * cell_w)
    # Crop slightly above label text at bottom if needed, or take cell
    bottom = int((row + 1) * cell_h)
    
    # Crop cell
    cell_crop = img.crop((left, top, right, bottom))
    
    # Save cropped image as PNG
    out_path = os.path.join(TARGET_DIR, filename)
    cell_crop.save(out_path, "PNG", optimize=True)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  [SAVED] {model_name:22} -> {filename:30} ({size_kb} KB)")

print("\n=== Updating Database thumbnail_url for All 12 Models ===")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM brands WHERE LOWER(name) LIKE '%bajaj%'")
brand_id = cur.fetchone()[0]

for _, _, model_name, filename in GRID_MODELS:
    img_url = f"/static/images/{filename}"
    cur.execute(
        "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE brand_id=? AND name=?",
        (img_url, brand_id, model_name)
    )
    print(f"  [DB OK] {model_name:22} -> {img_url}")

conn.commit()
conn.close()

print("\n=== Final Verification of Replaced Images ===")
for _, _, model_name, filename in GRID_MODELS:
    fp = os.path.join(TARGET_DIR, filename)
    sz = os.path.getsize(fp) // 1024 if os.path.exists(fp) else 0
    print(f"  Bajaj {model_name:22} | {filename:30} | {sz:5} KB | Exists: {os.path.exists(fp)}")
