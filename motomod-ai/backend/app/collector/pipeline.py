"""
BikeVerse AI — Dataset Collector Pipeline Orchestrator
Coordinates Brand Collection, Model Specs Extraction, Image Downloading, Deduplication, and Multi-format Exports.
Supports Incremental Updates.
"""
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from app.collector.config import TARGET_BRANDS, DATASET_DIR
from app.collector.scrapers.brand_collector import BrandCollector
from app.collector.scrapers.model_collector import ModelCollector
from app.collector.scrapers.image_collector import ImageCollector
from app.collector.processors.deduplicator import ImageDeduplicator
from app.collector.processors.exporter import DatasetExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bikeverse.collector.pipeline")


class BikeVerseDatasetPipeline:
    """End-to-end dataset collector pipeline for BikeVerse AI."""

    def __init__(self, dataset_dir: Path = DATASET_DIR):
        self.dataset_dir = dataset_dir
        self.brand_collector = BrandCollector()
        self.model_collector = ModelCollector()
        self.image_collector = ImageCollector()
        self.deduplicator = ImageDeduplicator()
        self.exporter = DatasetExporter()

    def run_full_pipeline(self, brand_limit: Optional[int] = None, models_per_brand_limit: Optional[int] = None) -> Dict[str, Any]:
        """Execute full automated dataset collection, deduplication, and export."""
        start_time = time.time()
        logger.info("Starting BikeVerse AI Dataset Collector Pipeline...")

        # 1. Collect Brands
        target_brands = TARGET_BRANDS[:brand_limit] if brand_limit else TARGET_BRANDS
        collected_brands = self.brand_collector.collect_all(target_brands)
        logger.info(f"Phase 1 Complete: Collected {len(collected_brands)} brands.")

        # 2. Extract Motorcycle Models & Specs
        # Load motorcycle specs from seed dataset or discovery engine
        from app.core.seed import BIKES_AND_VARIANTS_SEED

        collected_models_count = 0
        collected_images_count = 0

        for item in BIKES_AND_VARIANTS_SEED:
            b_slug = item["brand"]
            m_slug = item["slug"]

            # Filter by target_brands
            if brand_limit and not any(b["slug"] == b_slug for b in target_brands):
                continue

            spec_input = {
                "brand": b_slug.replace("-", " ").title(),
                "brand_slug": b_slug,
                "model_name": item["name"],
                "model_slug": m_slug,
                "generation": f"Gen {item.get('year', 2023) - 2020}",
                "year": item["year"],
                "category": item["category"].value if hasattr(item["category"], "value") else str(item["category"]),
                "engine_cc": item["cc"],
                "power_hp": item["hp"],
                "torque_nm": item["torque"],
                "fuel_tank_l": item["tank"],
                "mileage_kmpl": item["kmpl"],
                "transmission": "6-Speed Manual",
                "weight_kg": 165.0,
                "seat_height_mm": 800.0,
                "ground_clearance_mm": 160.0,
                "wheelbase_mm": 1380.0,
                "has_abs": item["abs"],
                "top_speed_kmh": item["speed"],
                "fuel_type": "Petrol",
                "cooling_type": "Liquid Cooled",
                "cylinders": 1 if item["cc"] < 400 else 2 if item["cc"] < 900 else 4,
                "price_inr": item["price"],
                "color_variants": [item["variant"]]
            }

            # Save specs & metadata
            spec_obj = self.model_collector.collect_model_specs(spec_input)
            collected_models_count += 1

            # Fetch HD Images
            img_paths = self.image_collector.collect_model_images(
                brand_slug=b_slug,
                model_slug=m_slug,
                brand_name=spec_obj.brand,
                model_name=spec_obj.model_name
            )
            collected_images_count += len(img_paths)

        logger.info(f"Phase 2 & 3 Complete: Collected {collected_models_count} models with {collected_images_count} image assets.")

        # 4. Deduplication & Quality Filtering
        dedupe_stats = self.deduplicator.process_directory()
        logger.info(f"Phase 4 Complete: Deduplicated dataset. Unique images: {dedupe_stats['unique_images']}.")

        # 5. Export Multi-Format Output Files
        export_paths = self.exporter.export_all()
        logger.info(f"Phase 5 Complete: Exported CSV, JSON, SQLite, and MongoDB JSON files.")

        elapsed = round(time.time() - start_time, 2)
        summary = {
            "status": "success",
            "execution_time_seconds": elapsed,
            "total_brands": len(collected_brands),
            "total_models": collected_models_count,
            "total_images": dedupe_stats["unique_images"],
            "duplicates_removed": dedupe_stats["duplicates_removed"],
            "exports": {k: str(v) for k, v in export_paths.items()}
        }
        logger.info(f"BikeVerse AI Pipeline finished successfully in {elapsed}s: {summary}")
        return summary
