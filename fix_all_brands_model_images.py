import sqlite3
import os
import re
import requests
import shutil
from PIL import Image, ImageDraw

ROOT_DIR = r"c:\CCP PROJECT\Motoventra"
DB_PATH = os.path.join(ROOT_DIR, "motomod-ai", "backend", "motomod_ai.db")
STATIC_IMG_DIR = os.path.join(ROOT_DIR, "motomod-ai", "backend", "app", "static", "images")
INDEX_HTML_PATH = os.path.join(ROOT_DIR, "motomod-ai", "backend", "app", "static", "index.html")

os.makedirs(STATIC_IMG_DIR, exist_ok=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def create_model_card_image(brand_name, model_name, category, output_path):
    """Generates a clean HD motorcycle model card image for models missing photos."""
    target_w, target_h = 1000, 650
    canvas = Image.new("RGB", (target_w, target_h), (6, 11, 24))
    draw = ImageDraw.Draw(canvas)

    # Background accent circles
    draw.ellipse([target_w//2 - 200, target_h//2 - 200, target_w//2 + 200, target_h//2 + 200], outline=(0, 242, 254), width=1)
    draw.ellipse([target_w//2 - 130, target_h//2 - 130, target_w//2 + 130, target_h//2 + 130], outline=(155, 81, 224), width=1)

    # Stylized motorcycle silhouette frame
    cx, cy = target_w // 2, target_h // 2 - 20
    # Wheels
    draw.ellipse([cx - 200 - 65, cy + 40 - 65, cx - 200 + 65, cy + 40 + 65], outline=(0, 242, 254), width=5)
    draw.ellipse([cx - 200 - 30, cy + 40 - 30, cx - 200 + 30, cy + 40 + 30], outline=(0, 242, 254), width=2)
    draw.ellipse([cx + 200 - 65, cy + 40 - 65, cx + 200 + 65, cy + 40 + 65], outline=(155, 81, 224), width=5)
    draw.ellipse([cx + 200 - 30, cy + 40 - 30, cx + 200 + 30, cy + 40 + 30], outline=(155, 81, 224), width=2)
    
    # Chassis lines
    draw.line([cx - 135, cy + 40, cx + 135, cy + 40], fill=(0, 242, 254), width=7)
    draw.line([cx - 80, cy + 40, cx, cy - 70], fill=(0, 242, 254), width=6)
    draw.line([cx + 80, cy + 40, cx, cy - 70], fill=(155, 81, 224), width=6)
    draw.line([cx - 140, cy - 75, cx + 80, cy - 75], fill=(0, 242, 254), width=6)

    # Text overlays
    draw.text((target_w//2 - 180, target_h - 140), f"{brand_name.upper()} {model_name.upper()}", fill=(255, 255, 255))
    draw.text((target_w//2 - 120, target_h - 105), f"Category: {category}  |  Official Model", fill=(0, 242, 254))
    draw.text((target_w//2 - 140, target_h - 60), "MotoVentra Motorcycle Catalog", fill=(107, 127, 168))

    canvas.save(output_path, "PNG")

def process_all_brands():
    print("===========================================================================")
    print("FIXING AND POPULATING IMAGES FOR ALL 262 MODELS ACROSS ALL BRANDS")
    print("===========================================================================")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT br.name as brand_name, br.slug as brand_slug, m.id as model_id, m.name as model_name, m.category, m.thumbnail_url 
    FROM motorcycles m
    JOIN brands br ON m.brand_id = br.id
    ORDER BY br.name, m.name
    """)
    models = cur.fetchall()

    fixed_db_count = 0
    generated_file_count = 0

    for brand_name, brand_slug, model_id, model_name, category, thumb_url in models:
        clean_brand = slugify(brand_name)
        clean_model = slugify(model_name)
        file_name = f"{clean_brand}_{clean_model}.png"
        target_path = os.path.join(STATIC_IMG_DIR, file_name)
        target_url = f"/static/images/{file_name}"

        # If file doesn't exist, generate card image
        if not os.path.exists(target_path):
            create_model_card_image(brand_name, model_name, category, target_path)
            generated_file_count += 1

        # Update DB thumbnail_url for model
        cur.execute(
            "UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (target_url, model_id)
        )
        if cur.rowcount > 0:
            fixed_db_count += 1

    conn.commit()

    # Final DB audit check
    cur.execute("SELECT COUNT(*) FROM motorcycles WHERE thumbnail_url IS NULL OR thumbnail_url=''")
    missing_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM motorcycles")
    total_count = cur.fetchone()[0]

    conn.close()

    print(f"\nCompletion Summary:")
    print(f"  - Total Models Processed: {total_count}")
    print(f"  - DB Records Updated: {fixed_db_count}")
    print(f"  - New Model Card Images Generated: {generated_file_count}")
    print(f"  - Models Remaining Without thumbnail_url: {missing_count}")

if __name__ == "__main__":
    process_all_brands()
