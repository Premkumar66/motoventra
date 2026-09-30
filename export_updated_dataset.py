import sqlite3
import pandas as pd
import json
import os
import zipfile

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
EXPORT_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\dataset_export"
STATIC_DS_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\dataset"

os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(STATIC_DS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("=== Exporting Updated MotoVentra Dataset ===")
# 1. Brands
df_brands = pd.read_sql_query("SELECT * FROM brands ORDER BY name", conn)
df_brands.to_csv(os.path.join(EXPORT_DIR, "brands_dataset.csv"), index=False)
print(f"  Brands Exported: {len(df_brands)} rows")

# 2. Motorcycles
df_motos = pd.read_sql_query("""
    SELECT m.id, b.name as brand_name, m.name as model_name, m.category, m.thumbnail_url, m.created_at
    FROM motorcycles m
    JOIN brands b ON m.brand_id = b.id
    ORDER BY b.name, m.name
""", conn)
df_motos.to_csv(os.path.join(EXPORT_DIR, "motorcycles_dataset.csv"), index=False)
print(f"  Motorcycles Exported: {len(df_motos)} rows")

# 3. Modifications
df_mods = pd.read_sql_query("""
    SELECT m.id, c.name as category, m.brand_name, m.model_name, m.description, m.price_inr,
           m.hp_change_bhp, m.torque_change_nm, m.weight_change_kg, m.material, m.is_legal_for_road
    FROM modifications m
    JOIN modification_categories c ON m.category_id = c.id
    ORDER BY c.name, m.model_name
""", conn)
df_mods.to_csv(os.path.join(EXPORT_DIR, "modifications_dataset.csv"), index=False)
print(f"  Modifications Exported: {len(df_mods)} rows")

# 4. JSON Export
full_json = {
    "total_brands": len(df_brands),
    "total_motorcycles": len(df_motos),
    "total_modifications": len(df_mods),
    "brands": df_brands.to_dict(orient="records"),
    "motorcycles": df_motos.to_dict(orient="records"),
    "modifications": df_mods.to_dict(orient="records")
}
with open(os.path.join(EXPORT_DIR, "full_motoventra_dataset.json"), "w", encoding="utf-8") as f:
    json.dump(full_json, f, indent=2)
print("  Full JSON Dataset Exported")

# 5. ZIP Package
zip_path_export = os.path.join(EXPORT_DIR, "motoventra_dataset_package.zip")
zip_path_static = os.path.join(STATIC_DS_DIR, "motoventra_dataset_package.zip")

with zipfile.ZipFile(zip_path_export, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(EXPORT_DIR, "brands_dataset.csv"), arcname="brands_dataset.csv")
    z.write(os.path.join(EXPORT_DIR, "motorcycles_dataset.csv"), arcname="motorcycles_dataset.csv")
    z.write(os.path.join(EXPORT_DIR, "modifications_dataset.csv"), arcname="modifications_dataset.csv")
    z.write(os.path.join(EXPORT_DIR, "full_motoventra_dataset.json"), arcname="full_motoventra_dataset.json")

# Copy ZIP to static serving path
with open(zip_path_export, "rb") as sf, open(zip_path_static, "wb") as df:
    df.write(sf.read())

conn.close()
print("  ZIP Package Exported to static path serving")
