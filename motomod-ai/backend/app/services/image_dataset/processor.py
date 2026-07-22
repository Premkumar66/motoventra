"""
MotoMod AI — Bike Image Dataset Processor Service
Resizes, compresses, generates thumbnails & previews, computes SHA-256 and pHash, and extracts EXIF metadata.
"""
import hashlib
import io
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageOps, ExifTags


class ImageProcessorService:
    @staticmethod
    def compute_sha256(file_bytes: bytes) -> str:
        """Compute SHA-256 hash of raw file bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def compute_dhash(image: Image.Image, hash_size: int = 8) -> str:
        """
        Compute difference hash (dHash) for visual duplicate detection.
        Returns hex string representation of visual hash.
        """
        # Convert to grayscale and resize to (hash_size + 1, hash_size)
        resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(resized.getdata())
        
        difference = []
        for row in range(hash_size):
            for col in range(hash_size):
                pixel_left = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                difference.append(pixel_left > pixel_right)

        # Convert boolean array to hex string
        decimal_value = 0
        hex_string = []
        for index, value in enumerate(difference):
            if value:
                decimal_value += 2 ** (index % 8)
            if (index % 8) == 7 or index == len(difference) - 1:
                hex_string.append(f"{decimal_value:02x}")
                decimal_value = 0
        return "".join(hex_string)

    @staticmethod
    def extract_exif(image: Image.Image) -> Tuple[Dict[str, Any], Optional[str], Optional[str]]:
        """Extract camera EXIF metadata safely."""
        exif_dict = {}
        make = None
        model = None

        try:
            raw_exif = image._getexif()
            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    # Exclude binary data
                    if isinstance(value, (bytes, bytearray)):
                        continue
                    exif_dict[str(tag_name)] = str(value)

                make = exif_dict.get("Make")
                model = exif_dict.get("Model")
        except Exception:
            pass

        return exif_dict, make, model

    @classmethod
    def process_image(
        cls,
        file_bytes: bytes,
        target_path: Path,
        max_dimension: int = 1920,
        jpeg_quality: int = 85
    ) -> Dict[str, Any]:
        """
        Full image processing pipeline:
        1. Opens & verifies Pillow Image
        2. Auto-rotates using EXIF orientation
        3. Computes SHA256 & dHash
        4. Extracts EXIF metadata
        5. Generates optimized main image, preview (800px), and thumbnail (200px)
        """
        image = Image.open(io.BytesIO(file_bytes))
        image = ImageOps.exif_transpose(image)

        width, height = image.size
        sha256_hash = cls.compute_sha256(file_bytes)
        dhash_val = cls.compute_dhash(image)
        exif_dict, camera_make, camera_model = cls.extract_exif(image)

        # Prepare derivative file paths
        parent_dir = target_path.parent
        stem = target_path.stem
        ext = target_path.suffix.lower()

        thumb_dir = parent_dir / "thumbnails"
        thumb_dir.mkdir(exist_ok=True)
        thumb_path = thumb_dir / f"{stem}_thumb.jpg"

        preview_dir = parent_dir / "previews"
        preview_dir.mkdir(exist_ok=True)
        preview_path = preview_dir / f"{stem}_preview.jpg"

        # Save Main Processed Image (RGB converted, quality optimized)
        main_img = image.copy()
        if max(width, height) > max_dimension:
            main_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        if main_img.mode in ("RGBA", "P"):
            main_img = main_img.convert("RGB")

        main_img.save(target_path, format="JPEG", quality=jpeg_quality, optimize=True)

        # Save Preview (max 800px)
        preview_img = image.copy()
        preview_img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        if preview_img.mode in ("RGBA", "P"):
            preview_img = preview_img.convert("RGB")
        preview_img.save(preview_path, format="JPEG", quality=80, optimize=True)

        # Save Thumbnail (max 200px)
        thumb_img = image.copy()
        thumb_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
        if thumb_img.mode in ("RGBA", "P"):
            thumb_img = thumb_img.convert("RGB")
        thumb_img.save(thumb_path, format="JPEG", quality=75, optimize=True)

        return {
            "width": width,
            "height": height,
            "mime_type": "image/jpeg",
            "sha256": sha256_hash,
            "phash": dhash_val,
            "thumbnail_path": str(thumb_path),
            "preview_path": str(preview_path),
            "exif": exif_dict,
            "camera_make": camera_make,
            "camera_model": camera_model,
        }


processor_service = ImageProcessorService()
