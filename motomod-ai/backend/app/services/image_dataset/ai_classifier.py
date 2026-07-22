"""
MotoMod AI — Bike Image Dataset AI Features Service
Provides:
- Perceptual hash Hamming distance duplicate detection
- Visual Image Similarity Search
- Automatic brand & category tagging rules
- Missing image coverage analyzer across brands & models
"""
from typing import List, Dict, Any, Optional
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image_dataset import (
    BikeImageBrand, BikeImageModel, BikeModelYear, BikeImage, BikeImageMetadata,
    ImageViewType, ImageStatus
)


class ImageAIService:
    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """Calculate Hamming distance between two hex pHash strings."""
        if not hash1 or not hash2 or len(hash1) != len(hash2):
            return 999
        try:
            val1 = int(hash1, 16)
            val2 = int(hash2, 16)
            x = val1 ^ val2
            tot = 0
            while x > 0:
                tot += x & 1
                x >>= 1
            return tot
        except ValueError:
            return 999

    @classmethod
    async def find_similar_images(
        cls,
        db: AsyncSession,
        target_phash: str,
        max_distance: int = 10,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find visually similar images using pHash Hamming distance."""
        res = await db.execute(select(BikeImage).where(BikeImage.phash.isnot(None)))
        all_imgs = res.scalars().all()

        results = []
        for img in all_imgs:
            dist = cls.hamming_distance(target_phash, img.phash)
            if dist <= max_distance:
                results.append({
                    "id": str(img.id),
                    "file_name": img.file_name,
                    "file_url": img.file_url,
                    "thumbnail_url": f"/static/dataset_images/{img.thumbnail_path}" if img.thumbnail_path else img.file_url,
                    "hamming_distance": dist,
                    "similarity_score": round(max(0, 100 - (dist * 5)), 2)
                })

        results.sort(key=lambda x: x["hamming_distance"])
        return results[:limit]

    @classmethod
    async def analyze_missing_images(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Generates a comprehensive report of models/years missing required views.
        Required views: front, rear, left, right.
        """
        res_models = await db.execute(select(BikeImageModel))
        models = res_models.scalars().all()

        total_models = len(models)
        models_with_images = 0
        missing_report = []

        required_views = {"front", "rear", "left", "right"}

        for m in models:
            res_imgs = await db.execute(select(BikeImage).where(BikeImage.model_id == m.id))
            imgs = res_imgs.scalars().all()

            existing_views = set(img.view_type.value for img in imgs if img.view_type)
            missing = required_views - existing_views

            if len(imgs) > 0:
                models_with_images += 1

            if len(missing) > 0:
                # Get brand name
                res_brand = await db.execute(select(BikeImageBrand).where(BikeImageBrand.id == m.brand_id))
                brand = res_brand.scalar_one_or_none()
                b_name = brand.name if brand else "Unknown"

                missing_report.append({
                    "model_id": str(m.id),
                    "brand": b_name,
                    "model": m.name,
                    "total_images": len(imgs),
                    "existing_views": list(existing_views),
                    "missing_views": list(missing)
                })

        coverage_pct = round((models_with_images / total_models * 100), 2) if total_models > 0 else 0.0

        return {
            "total_models_in_catalog": total_models,
            "models_with_images": models_with_images,
            "coverage_percentage": coverage_pct,
            "missing_coverage_details": missing_report[:50]  # top 50 missing models
        }


ai_service = ImageAIService()
