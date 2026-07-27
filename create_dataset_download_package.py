import os
import shutil
import zipfile
import json

ROOT_DIR = r"c:\CCP PROJECT\Motoventra"
EXPORT_DIR = os.path.join(ROOT_DIR, "motomod-ai", "dataset_export")
STATIC_DATASET_DIR = os.path.join(ROOT_DIR, "motomod-ai", "backend", "app", "static", "dataset")

os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(STATIC_DATASET_DIR, exist_ok=True)

# 1. Create a README_DATASET.md for library usage (Pandas, Python, JS)
readme_content = """# MotoVentra Motorcycle & Modification Dataset

This package contains the complete dataset for the MotoVentra AI platform.

## Files Included

1. `motorcycles_dataset.csv` - 262 Motorcycles with engine specs, horsepower, torque, top speed, mileage, price, category, and image URLs.
2. `modifications_dataset.csv` - Aftermarket modification parts, price, material, compatibility, and performance changes (+BHP, +Nm, -kmpl, -kg).
3. `brands_dataset.csv` - 46 Global Motorcycle Brands with origin country and logo URLs.
4. `full_motoventra_dataset.json` - Complete Master Dataset in structured JSON format.
5. `bajaj_dataset_metadata.json` - Image dataset metadata for Bajaj motorcycle models.

## Quick Start Guide for Data Science & Python Libraries

### Load into Pandas (Python)
```python
import pandas as pd

# Load Motorcycles
bikes_df = pd.read_csv("motorcycles_dataset.csv")
print(bikes_df.head())

# Load Modifications
mods_df = pd.read_csv("modifications_dataset.csv")
print(mods_df.head())

# Load Brands
brands_df = pd.read_csv("brands_dataset.csv")
print(brands_df.head())
```

### Load Master JSON in Python / Node.js
```python
import json

with open("full_motoventra_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Total Brands: {dataset['total_brands']}")
print(f"Total Motorcycles: {dataset['total_motorcycles']}")
```
"""

readme_path = os.path.join(EXPORT_DIR, "README_DATASET.md")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content)

# Copy bajaj dataset metadata into EXPORT_DIR
bajaj_src = os.path.join(ROOT_DIR, "assets", "bikes", "Bajaj", "dataset_metadata.json")
bajaj_dest = os.path.join(EXPORT_DIR, "bajaj_dataset_metadata.json")
if os.path.exists(bajaj_src):
    shutil.copy2(bajaj_src, bajaj_dest)

# 2. Package into a Zip Archive for easy one-click download
zip_path = os.path.join(EXPORT_DIR, "motoventra_dataset_package.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for fname in ["motorcycles_dataset.csv", "modifications_dataset.csv", "brands_dataset.csv", "full_motoventra_dataset.json", "bajaj_dataset_metadata.json", "README_DATASET.md"]:
        fpath = os.path.join(EXPORT_DIR, fname)
        if os.path.exists(fpath):
            zipf.write(fpath, arcname=fname)

print(f"Created ZIP Package: {zip_path} ({os.path.getsize(zip_path)//1024} KB)")

# 3. Copy files to static folder for HTTP download
for fname in os.listdir(EXPORT_DIR):
    src = os.path.join(EXPORT_DIR, fname)
    if os.path.isfile(src):
        shutil.copy2(src, os.path.join(STATIC_DATASET_DIR, fname))

print(f"Copied dataset files to static web folder: {STATIC_DATASET_DIR}")
