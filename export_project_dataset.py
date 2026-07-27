import sqlite3
import json
import csv
import os

ROOT_DIR = r"c:\CCP PROJECT\Motoventra"
DB_PATH = os.path.join(ROOT_DIR, "motomod-ai", "backend", "motomod_ai.db")
EXPORT_DIR = os.path.join(ROOT_DIR, "motomod-ai", "dataset_export")
os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("===========================================================================")
print("EXPORTING COMPLETE MOTOVENTRA PROJECT DATASET (CSV + JSON)")
print("===========================================================================")

# 1. Export Brands Dataset
cur.execute("SELECT id, name, slug, country, logo_url FROM brands ORDER BY name")
brand_rows = cur.fetchall()
brand_list = []

csv_brands_path = os.path.join(EXPORT_DIR, "brands_dataset.csv")
with open(csv_brands_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["brand_id", "brand_name", "slug", "country", "logo_url"])
    for row in brand_rows:
        writer.writerow(row)
        brand_list.append({
            "brand_id": row[0],
            "brand_name": row[1],
            "slug": row[2],
            "country": row[3],
            "logo_url": row[4]
        })
print(f"Exported {len(brand_list)} Brands to {csv_brands_path}")

# 2. Export Motorcycles Dataset
cur.execute("""
SELECT 
    m.id as model_id,
    br.name as brand_name,
    m.name as model_name,
    m.slug as model_slug,
    m.category,
    m.thumbnail_url,
    mv.engine_cc,
    mv.horsepower_bhp,
    mv.torque_nm,
    mv.top_speed_kmh,
    mv.mileage_kmpl,
    mv.price_inr,
    mv.price_usd,
    mv.weight_kg,
    mv.fuel_tank_liters
FROM motorcycles m
JOIN brands br ON m.brand_id = br.id
LEFT JOIN motorcycle_variants mv ON mv.motorcycle_id = m.id
ORDER BY br.name, m.name
""")
moto_rows = cur.fetchall()
moto_list = []

csv_motos_path = os.path.join(EXPORT_DIR, "motorcycles_dataset.csv")
with open(csv_motos_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "model_id", "brand_name", "model_name", "model_slug", "category", "thumbnail_url",
        "engine_cc", "horsepower_bhp", "torque_nm", "top_speed_kmh", "mileage_kmpl",
        "price_inr", "price_usd", "weight_kg", "fuel_tank_liters"
    ])
    for row in moto_rows:
        writer.writerow(row)
        moto_list.append({
            "model_id": row[0],
            "brand_name": row[1],
            "model_name": row[2],
            "model_slug": row[3],
            "category": row[4],
            "thumbnail_url": row[5],
            "engine_cc": row[6],
            "horsepower_bhp": row[7],
            "torque_nm": row[8],
            "top_speed_kmh": row[9],
            "mileage_kmpl": row[10],
            "price_inr": row[11],
            "price_usd": row[12],
            "weight_kg": row[13],
            "fuel_tank_liters": row[14]
        })
print(f"Exported {len(moto_list)} Motorcycles to {csv_motos_path}")

# 3. Export Modification Accessories Dataset
cur.execute("""
SELECT 
    mod.id,
    cat.name as category_name,
    mod.brand_name,
    mod.model_name,
    mod.price_inr,
    mod.price_usd,
    mod.hp_change_bhp,
    mod.torque_change_nm,
    mod.mileage_change_kmpl,
    mod.weight_change_kg,
    mod.material,
    mod.is_universal
FROM modifications mod
LEFT JOIN modification_categories cat ON mod.category_id = cat.id
ORDER BY cat.name, mod.brand_name
""")
mod_rows = cur.fetchall()
mod_list = []

csv_mods_path = os.path.join(EXPORT_DIR, "modifications_dataset.csv")
with open(csv_mods_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "modification_id", "category_name", "brand_name", "part_name",
        "price_inr", "price_usd", "hp_change_bhp", "torque_change_nm",
        "mileage_change_kmpl", "weight_change_kg", "material", "is_universal"
    ])
    for row in mod_rows:
        writer.writerow(row)
        mod_list.append({
            "modification_id": row[0],
            "category_name": row[1],
            "brand_name": row[2],
            "part_name": row[3],
            "price_inr": row[4],
            "price_usd": row[5],
            "hp_change_bhp": row[6],
            "torque_change_nm": row[7],
            "mileage_change_kmpl": row[8],
            "weight_change_kg": row[9],
            "material": row[10],
            "is_universal": bool(row[11])
        })
print(f"Exported {len(mod_list)} Modifications to {csv_mods_path}")

# 4. Export Complete Master Dataset JSON
json_master_path = os.path.join(EXPORT_DIR, "full_motoventra_dataset.json")
master_dataset = {
    "project_name": "MotoVentra - AI Motorcycle Platform",
    "version": "1.0",
    "total_brands": len(brand_list),
    "total_motorcycles": len(moto_list),
    "total_modifications": len(mod_list),
    "brands": brand_list,
    "motorcycles": moto_list,
    "modifications": mod_list
}

with open(json_master_path, "w", encoding="utf-8") as f:
    json.dump(master_dataset, f, indent=2)

print(f"Exported Master JSON Dataset ({os.path.getsize(json_master_path)//1024} KB) to {json_master_path}")
conn.close()
