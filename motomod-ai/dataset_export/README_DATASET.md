# MotoVentra Motorcycle & Modification Dataset

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
