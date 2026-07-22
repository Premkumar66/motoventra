"""
MotoMod AI — Bike Image Dataset Validator Service
Validates image files against format, corruption, and minimum resolution requirements.
"""
import io
from typing import Tuple, Optional
from PIL import Image


class ImageValidatorService:
    MIN_WIDTH = 300
    MIN_HEIGHT = 200
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "MPO"}

    @classmethod
    def validate_image_bytes(cls, file_bytes: bytes) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]], Optional[str]]:
        """
        Validates raw image bytes.
        Returns (is_valid, error_reason, (width, height), format_name)
        """
        if not file_bytes or len(file_bytes) == 0:
            return False, "File is empty", None, None

        try:
            img_stream = io.BytesIO(file_bytes)
            img = Image.open(img_stream)
            img.verify()  # Check for corruption

            # Re-open after verify() as verify alters image state
            img_stream.seek(0)
            img = Image.open(img_stream)
            
            fmt = img.format
            if fmt not in cls.ALLOWED_FORMATS:
                return False, f"Unsupported format '{fmt}'. Allowed: {', '.join(cls.ALLOWED_FORMATS)}", None, fmt

            width, height = img.size
            if width < cls.MIN_WIDTH or height < cls.MIN_HEIGHT:
                return False, f"Image resolution ({width}x{height}) is below minimum allowed ({cls.MIN_WIDTH}x{cls.MIN_HEIGHT})", (width, height), fmt

            return True, None, (width, height), fmt

        except Exception as e:
            return False, f"Corrupted or invalid image file: {str(e)}", None, None


validator_service = ImageValidatorService()
