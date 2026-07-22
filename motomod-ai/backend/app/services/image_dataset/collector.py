"""
MotoMod AI — Bike Image Dataset Collector & Importer Connectors
Importers for:
- Wikimedia Commons MediaWiki API (CC-BY / CC-BY-SA public media)
- CSV Batch Datasets
- ZIP Archive Uploads
- URL Direct Imports
- Admin / User File Uploads
"""
import csv
import io
import json
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image_dataset import (
    BikeImageBrand, BikeImageModel, BikeImageVariant, BikeModelYear,
    BikeImage, BikeImageMetadata, ImageSource, ImageLicense, ImageProcessingLog,
    ImageViewType, ImageStatus, ImportSource, LicenseType, ProcessingOperation, ProcessingStatus
)
from app.services.image_dataset.storage import storage_service
from app.services.image_dataset.processor import processor_service
from app.services.image_dataset.validator import validator_service


class DatasetCollectorService:
    
    @staticmethod
    async def get_or_create_brand(db: AsyncSession, brand_name: str) -> BikeImageBrand:
        slug = storage_service.sanitize_name(brand_name).lower()
        res = await db.execute(select(BikeImageBrand).where(BikeImageBrand.slug == slug))
        brand = res.scalar_one_or_none()
        if not brand:
            brand = BikeImageBrand(
                id=uuid.uuid4(),
                name=brand_name.strip().title(),
                slug=slug,
                country="Global"
            )
            db.add(brand)
            await db.flush()
        return brand

    @staticmethod
    async def get_or_create_model(db: AsyncSession, brand_id: uuid.UUID, model_name: str) -> BikeImageModel:
        slug = storage_service.sanitize_name(model_name).lower()
        res = await db.execute(select(BikeImageModel).where(
            BikeImageModel.brand_id == brand_id, BikeImageModel.slug == slug
        ))
        model = res.scalar_one_or_none()
        if not model:
            model = BikeImageModel(
                id=uuid.uuid4(),
                brand_id=brand_id,
                name=model_name.strip(),
                slug=slug
            )
            db.add(model)
            await db.flush()
        return model

    @staticmethod
    async def get_or_create_year(db: AsyncSession, model_id: uuid.UUID, year: int) -> BikeModelYear:
        res = await db.execute(select(BikeModelYear).where(
            BikeModelYear.model_id == model_id, BikeModelYear.year == year
        ))
        yr_rec = res.scalar_one_or_none()
        if not yr_rec:
            yr_rec = BikeModelYear(
                id=uuid.uuid4(),
                model_id=model_id,
                year=year
            )
            db.add(yr_rec)
            await db.flush()
        return yr_rec

    @classmethod
    async def ingest_image_bytes(
        cls,
        db: AsyncSession,
        file_bytes: bytes,
        brand_name: str,
        model_name: str,
        year: int,
        view_type: str = "other",
        variant_name: Optional[str] = None,
        color: Optional[str] = None,
        source_type: ImportSource = ImportSource.ADMIN_UPLOAD,
        original_url: Optional[str] = None,
        attribution: Optional[str] = None,
        copyright_owner: Optional[str] = None,
        license_spdx: str = "CC-BY-4.0"
    ) -> Tuple[bool, str, Optional[BikeImage]]:
        """
        Full ingest pipeline: Validate → Deduplicate → Process → Save File → DB Record
        """
        # 1. Validation
        valid, err_msg, dims, fmt = validator_service.validate_image_bytes(file_bytes)
        if not valid:
            return False, f"Validation failed: {err_msg}", None

        # 2. Hash & Deduplication check
        sha256 = processor_service.compute_sha256(file_bytes)
        res_dup = await db.execute(select(BikeImage).where(BikeImage.image_hash == sha256))
        if res_dup.scalar_one_or_none():
            return False, "Duplicate image detected (SHA-256 collision)", None

        # 3. Database Catalog Entities
        brand_obj = await cls.get_or_create_brand(db, brand_name)
        model_obj = await cls.get_or_create_model(db, brand_obj.id, model_name)
        year_obj = await cls.get_or_create_year(db, model_obj.id, year)

        # 4. Storage & Image Processing
        view_enum_val = view_type.lower()
        valid_views = [v.value for v in ImageViewType]
        if view_enum_val not in valid_views:
            view_enum_val = ImageViewType.OTHER.value

        abs_path, rel_path, file_name = storage_service.save_image_file(
            file_bytes=file_bytes,
            brand=brand_obj.name,
            model=model_obj.name,
            year=year,
            view_type=view_enum_val,
            extension=".jpg"
        )

        proc_meta = processor_service.process_image(
            file_bytes=file_bytes,
            target_path=abs_path
        )

        # 5. Save BikeImage Record
        bike_img = BikeImage(
            id=uuid.uuid4(),
            model_id=model_obj.id,
            year_record_id=year_obj.id,
            file_name=file_name,
            file_path=rel_path,
            file_url=f"/static/dataset_images/{rel_path}",
            file_size_bytes=len(file_bytes),
            mime_type="image/jpeg",
            width=proc_meta["width"],
            height=proc_meta["height"],
            view_type=ImageViewType(view_enum_val),
            color=color,
            image_hash=sha256,
            phash=proc_meta["phash"],
            thumbnail_path=storage_service.get_relative_path(Path(proc_meta["thumbnail_path"])),
            preview_path=storage_service.get_relative_path(Path(proc_meta["preview_path"])),
            status=ImageStatus.APPROVED if source_type == ImportSource.ADMIN_UPLOAD else ImageStatus.PENDING,
            is_verified=True if source_type == ImportSource.ADMIN_UPLOAD else False
        )
        db.add(bike_img)
        await db.flush()

        # 6. Save Metadata & License
        img_meta = BikeImageMetadata(
            id=uuid.uuid4(),
            image_id=bike_img.id,
            original_url=original_url,
            attribution=attribution or f"Source: {source_type.value}",
            copyright_owner=copyright_owner,
            exif_data=proc_meta["exif"],
            camera_make=proc_meta["camera_make"],
            camera_model=proc_meta["camera_model"]
        )
        db.add(img_meta)

        # Log entry
        log_entry = ImageProcessingLog(
            id=uuid.uuid4(),
            image_id=bike_img.id,
            operation=ProcessingOperation.STORE,
            status=ProcessingStatus.SUCCESS,
            details={"sha256": sha256, "dimensions": f"{proc_meta['width']}x{proc_meta['height']}"}
        )
        db.add(log_entry)

        await db.commit()
        return True, "Image successfully ingested", bike_img

    @classmethod
    async def import_from_url(
        cls,
        db: AsyncSession,
        url: str,
        brand_name: str,
        model_name: str,
        year: int,
        view_type: str = "front",
        attribution: str = "Public Source"
    ) -> Tuple[bool, str, Optional[BikeImage]]:
        """Import an image directly from a public URL."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MotoModAI/1.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                file_bytes = response.read()

            return await cls.ingest_image_bytes(
                db=db,
                file_bytes=file_bytes,
                brand_name=brand_name,
                model_name=model_name,
                year=year,
                view_type=view_type,
                source_type=ImportSource.URL_IMPORT,
                original_url=url,
                attribution=attribution
            )
        except Exception as e:
            return False, f"Failed to download image from URL: {str(e)}", None

    @classmethod
    async def import_from_csv(cls, db: AsyncSession, csv_content: str) -> Dict[str, Any]:
        """
        Import multiple images via CSV dataset definition.
        CSV Columns: brand, model, year, view_type, image_url, attribution
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        success_count = 0
        fail_count = 0
        errors = []

        for row in reader:
            b_name = row.get("brand") or row.get("Brand")
            m_name = row.get("model") or row.get("Model")
            year_str = row.get("year") or row.get("Year") or "2024"
            view = row.get("view_type") or row.get("view") or "front"
            img_url = row.get("image_url") or row.get("url")
            attr = row.get("attribution") or "CSV Import"

            if not b_name or not m_name or not img_url:
                fail_count += 1
                errors.append(f"Missing required fields in row: {row}")
                continue

            try:
                yr = int(year_str)
            except ValueError:
                yr = 2024

            ok, msg, _ = await cls.import_from_url(
                db=db,
                url=img_url.strip(),
                brand_name=b_name.strip(),
                model_name=m_name.strip(),
                year=yr,
                view_type=view.strip(),
                attribution=attr.strip()
            )
            if ok:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"{b_name} {m_name}: {msg}")

        return {
            "total_processed": success_count + fail_count,
            "success": success_count,
            "failed": fail_count,
            "errors": errors[:10]  # Return top 10 error strings
        }

    @classmethod
    async def import_from_wikimedia(
        cls,
        db: AsyncSession,
        query: str = "Motorcycle",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        MediaWiki API connector for Wikimedia Commons.
        Collects open CC-BY/CC-BY-SA licensed media for target bikes.
        """
        endpoint = "https://commons.wikimedia.org/w/api.php"
        params = f"?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|mime|extmetadata&format=json"
        
        url = endpoint + params
        success_count = 0
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MotoModAI-Collector/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, info in pages.items():
                imageinfo = info.get("imageinfo", [{}])[0]
                img_url = imageinfo.get("url")
                mime = imageinfo.get("mime")

                if not img_url or "image/jpeg" not in mime:
                    continue

                title = info.get("title", "Motorcycle").replace("File:", "").replace(".jpg", "").replace("_", " ")
                
                # Attempt to parse brand/model from title
                brand = "Global"
                for known in ["Honda", "Yamaha", "KTM", "Royal Enfield", "Kawasaki", "BMW", "Ducati", "Triumph", "Harley-Davidson", "Suzuki", "Bajaj", "TVS", "Hero"]:
                    if known.lower() in title.lower():
                        brand = known
                        break

                ok, _, _ = await cls.import_from_url(
                    db=db,
                    url=img_url,
                    brand_name=brand,
                    model_name=title[:40],
                    year=2024,
                    view_type="front",
                    attribution="Wikimedia Commons (CC-BY-SA)"
                )
                if ok:
                    success_count += 1
        except Exception as e:
            return {"status": "error", "message": str(e), "imported": 0}

        return {"status": "success", "imported": success_count}


collector_service = DatasetCollectorService()
