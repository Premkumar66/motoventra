"""
BikeVerse AI — Multi-Format Dataset Exporter
Generates CSV, JSON, SQLite Database, and MongoDB Import Files from the dataset directory.
"""
import csv
import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any

from app.collector.config import (
    DATASET_DIR, BRANDS_DIR, BIKES_DIR, EXPORTS_DIR,
    CSV_EXPORT_PATH, JSON_EXPORT_PATH, SQLITE_EXPORT_PATH, MONGO_EXPORT_PATH
)
from app.collector.schemas import BrandSchema, MotorcycleSpecsSchema

logger = logging.getLogger("bikeverse.collector.exporter")


class DatasetExporter:
    """Exports collected motorcycle catalog and image metadata into multiple standard formats."""

    def __init__(self, dataset_dir: Path = DATASET_DIR, exports_dir: Path = EXPORTS_DIR):
        self.dataset_dir = dataset_dir
        self.exports_dir = exports_dir
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def load_dataset_records(self) -> Dict[str, Any]:
        """Load all collected brand and bike spec records from disk."""
        brands: List[Dict[str, Any]] = []
        models: List[Dict[str, Any]] = []

        # Load Brands
        for b_dir in BRANDS_DIR.glob("*"):
            info_file = b_dir / "brand_info.json"
            if info_file.exists():
                with open(info_file, "r", encoding="utf-8") as f:
                    brands.append(json.load(f))

        # Load Models
        for m_dir in BIKES_DIR.glob("*/*"):
            specs_file = m_dir / "specs.json"
            if specs_file.exists():
                with open(specs_file, "r", encoding="utf-8") as f:
                    spec = json.load(f)
                    # Gather images in model folder
                    images = [str(img.relative_to(self.dataset_dir)) for img in m_dir.glob("*.*") if img.suffix in [".jpg", ".png", ".svg"]]
                    spec["image_paths"] = images
                    models.append(spec)

        return {"brands": brands, "models": models}

    def export_csv(self, records: Dict[str, Any]) -> Path:
        """Export dataset to CSV file."""
        models = records.get("models", [])
        if not models:
            logger.warning("No model records to export to CSV.")
            return CSV_EXPORT_PATH

        headers = [
            "id", "brand", "model_name", "generation", "year", "category",
            "engine_cc", "power_hp", "torque_nm", "fuel_tank_l", "mileage_kmpl",
            "transmission", "weight_kg", "seat_height_mm", "ground_clearance_mm",
            "wheelbase_mm", "has_abs", "top_speed_kmh", "fuel_type", "cooling_type",
            "cylinders", "price_inr", "price_usd", "image_paths"
        ]

        with open(CSV_EXPORT_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            for r in models:
                row = r.copy()
                row["image_paths"] = ";".join(row.get("image_paths", []))
                writer.writerow(row)

        logger.info(f"Exported CSV: {CSV_EXPORT_PATH}")
        return CSV_EXPORT_PATH

    def export_json(self, records: Dict[str, Any]) -> Path:
        """Export dataset to hierarchical JSON file."""
        with open(JSON_EXPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        logger.info(f"Exported JSON: {JSON_EXPORT_PATH}")
        return JSON_EXPORT_PATH

    def export_sqlite(self, records: Dict[str, Any]) -> Path:
        """Export dataset to standalone relational SQLite database."""
        if SQLITE_EXPORT_PATH.exists():
            try:
                SQLITE_EXPORT_PATH.unlink()
            except Exception as e:
                logger.debug(f"Could not unlink SQLite export directly: {e}")

        conn = sqlite3.connect(SQLITE_EXPORT_PATH)
        cursor = conn.cursor()

        # Create Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
                brand_name TEXT NOT NULL,
                slug TEXT NOT NULL,
                country TEXT,
                year_founded INTEGER,
                official_website TEXT,
                parent_company TEXT,
                logo_path TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motorcycles (
                id TEXT PRIMARY KEY,
                brand TEXT NOT NULL,
                brand_slug TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_slug TEXT NOT NULL,
                generation TEXT,
                year INTEGER,
                category TEXT,
                engine_cc REAL,
                power_hp REAL,
                torque_nm REAL,
                fuel_tank_l REAL,
                mileage_kmpl REAL,
                transmission TEXT,
                weight_kg REAL,
                seat_height_mm REAL,
                ground_clearance_mm REAL,
                wheelbase_mm REAL,
                has_abs INTEGER,
                top_speed_kmh REAL,
                fuel_type TEXT,
                cooling_type TEXT,
                cylinders INTEGER,
                price_inr REAL,
                price_usd REAL
            )
        ''')

        # Insert Brands
        for b in records.get("brands", []):
            cursor.execute('''
                INSERT INTO brands (id, brand_name, slug, country, year_founded, official_website, parent_company, logo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (b["id"], b["brand_name"], b["slug"], b["country"], b.get("year_founded"), b.get("official_website"), b.get("parent_company"), b.get("logo_path")))

        # Insert Motorcycles
        for m in records.get("models", []):
            cursor.execute('''
                INSERT INTO motorcycles (id, brand, brand_slug, model_name, model_slug, generation, year, category,
                    engine_cc, power_hp, torque_nm, fuel_tank_l, mileage_kmpl, transmission, weight_kg,
                    seat_height_mm, ground_clearance_mm, wheelbase_mm, has_abs, top_speed_kmh, fuel_type,
                    cooling_type, cylinders, price_inr, price_usd)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (m["id"], m["brand"], m["brand_slug"], m["model_name"], m["model_slug"], m.get("generation"), m["year"],
                  m["category"], m["engine_cc"], m["power_hp"], m["torque_nm"], m["fuel_tank_l"], m["mileage_kmpl"],
                  m["transmission"], m["weight_kg"], m["seat_height_mm"], m["ground_clearance_mm"], m["wheelbase_mm"],
                  1 if m.get("has_abs") else 0, m["top_speed_kmh"], m["fuel_type"], m["cooling_type"], m["cylinders"],
                  m["price_inr"], m.get("price_usd")))

        conn.commit()
        conn.close()

        logger.info(f"Exported SQLite DB: {SQLITE_EXPORT_PATH}")
        return SQLITE_EXPORT_PATH

    def export_mongodb_json(self, records: Dict[str, Any]) -> Path:
        """Export dataset to mongoimport newline-delimited JSON format."""
        with open(MONGO_EXPORT_PATH, "w", encoding="utf-8") as f:
            for b in records.get("brands", []):
                doc = {"type": "brand", **b}
                f.write(json.dumps(doc) + "\n")
            for m in records.get("models", []):
                doc = {"type": "motorcycle", **m}
                f.write(json.dumps(doc) + "\n")

        logger.info(f"Exported MongoDB Import JSON: {MONGO_EXPORT_PATH}")
        return MONGO_EXPORT_PATH

    def export_all(self) -> Dict[str, Path]:
        """Generate all export formats."""
        records = self.load_dataset_records()
        return {
            "csv": self.export_csv(records),
            "json": self.export_json(records),
            "sqlite": self.export_sqlite(records),
            "mongo": self.export_mongodb_json(records),
        }
