"""
BikeVerse AI — Motorcycle Model & Specs Collector
Extracts complete technical specifications across motorcycle models, generations, and variants.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from app.collector.config import BIKES_DIR
from app.collector.schemas import MotorcycleSpecsSchema

logger = logging.getLogger("bikeverse.collector.model")


class ModelCollector:
    """Collects and stores motorcycle specifications per brand and model."""

    def __init__(self, bikes_dir: Path = BIKES_DIR):
        self.bikes_dir = bikes_dir
        self.bikes_dir.mkdir(parents=True, exist_ok=True)

    def collect_model_specs(self, spec_data: Dict[str, Any]) -> MotorcycleSpecsSchema:
        """Process and save specs.json and metadata.json for a motorcycle model."""
        brand_slug = spec_data["brand_slug"]
        model_slug = spec_data["model_slug"]
        
        m_dir = self.bikes_dir / brand_slug / model_slug
        m_dir.mkdir(parents=True, exist_ok=True)

        specs_file = m_dir / "specs.json"
        meta_file = m_dir / "metadata.json"

        # Build schema object
        spec_obj = MotorcycleSpecsSchema(
            id=f"{brand_slug}-{model_slug}",
            brand=spec_data["brand"],
            brand_slug=brand_slug,
            model_name=spec_data["model_name"],
            model_slug=model_slug,
            generation=spec_data.get("generation", "Gen 1"),
            year=spec_data.get("year", 2024),
            category=spec_data.get("category", "Naked"),
            engine_cc=spec_data.get("engine_cc", 350.0),
            power_hp=spec_data.get("power_hp", 25.0),
            torque_nm=spec_data.get("torque_nm", 30.0),
            fuel_tank_l=spec_data.get("fuel_tank_l", 13.0),
            mileage_kmpl=spec_data.get("mileage_kmpl", 35.0),
            transmission=spec_data.get("transmission", "6-Speed Manual"),
            weight_kg=spec_data.get("weight_kg", 165.0),
            seat_height_mm=spec_data.get("seat_height_mm", 800.0),
            ground_clearance_mm=spec_data.get("ground_clearance_mm", 160.0),
            wheelbase_mm=spec_data.get("wheelbase_mm", 1380.0),
            has_abs=spec_data.get("has_abs", True),
            top_speed_kmh=spec_data.get("top_speed_kmh", 140.0),
            fuel_type=spec_data.get("fuel_type", "Petrol"),
            cooling_type=spec_data.get("cooling_type", "Liquid Cooled"),
            cylinders=spec_data.get("cylinders", 1),
            price_inr=spec_data.get("price_inr", 200000.0),
            price_usd=round(spec_data.get("price_inr", 200000.0) / 83.5, 2),
            color_variants=spec_data.get("color_variants", ["Black", "Red", "Blue"]),
            image_paths=[]
        )

        with open(specs_file, "w", encoding="utf-8") as f:
            json.dump(spec_obj.model_dump(), f, indent=2)

        # Write metadata.json
        meta_data = {
            "brand": spec_obj.brand,
            "model": spec_obj.model_name,
            "year": str(spec_obj.year),
            "category": spec_obj.category,
            "engine": f"{spec_obj.engine_cc}cc",
            "images": [
                "front.jpg", "rear.jpg", "left.jpg", "right.jpg",
                "dashboard.jpg", "engine.jpg", "exhaust.jpg",
                "color1.jpg", "color2.jpg"
            ]
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)

        logger.info(f"Collected specs for model: {spec_obj.brand} {spec_obj.model_name}")
        return spec_obj
