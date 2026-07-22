"""
MotoMod AI — Bike Image Dataset Storage Service
Manages local filesystem directory structure according to specification:
/images/{Brand}/{Model}/{Year}/{view_type}.jpg
Creates folders automatically and cleans up filenames.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Tuple, Optional


class ImageStorageService:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to app/static/images dataset root
            backend_root = Path(__file__).resolve().parent.parent.parent
            self.base_dir = backend_root / "static" / "dataset_images"
        else:
            self.base_dir = Path(base_dir)
        
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_name(self, name: str) -> str:
        """Sanitize names for safe directory/file paths."""
        if not name:
            return "Unknown"
        # Replace non-alphanumeric chars (except dashes/underscores) with underscores
        clean = re.sub(r'[^\w\-]', '_', name.strip())
        # Collapse multiple underscores
        clean = re.sub(r'_+', '_', clean)
        return clean.strip('_')

    def get_target_dir(self, brand: str, model: str, year: int) -> Path:
        """
        Creates and returns folder path following specification:
        /images/{Brand}/{Model}/{Year}
        """
        safe_brand = self.sanitize_name(brand)
        safe_model = self.sanitize_name(model)
        safe_year = str(year) if year and year > 1900 else "General"

        target_path = self.base_dir / safe_brand / safe_model / safe_year
        target_path.mkdir(parents=True, exist_ok=True)
        return target_path

    def get_relative_path(self, absolute_path: Path) -> str:
        """Returns relative path from dataset root for DB storage."""
        try:
            return str(absolute_path.relative_to(self.base_dir)).replace('\\', '/')
        except ValueError:
            return str(absolute_path).replace('\\', '/')

    def save_image_file(
        self,
        file_bytes: bytes,
        brand: str,
        model: str,
        year: int,
        view_type: str,
        extension: str = ".jpg"
    ) -> Tuple[Path, str, str]:
        """
        Saves raw image bytes to correct Brand/Model/Year directory with standard view filename.
        Returns (absolute_path, relative_path, file_name)
        """
        target_dir = self.get_target_dir(brand, model, year)
        safe_view = self.sanitize_name(view_type).lower()
        if not extension.startswith('.'):
            extension = '.' + extension
        
        file_name = f"{safe_view}{extension.lower()}"
        dest_path = target_dir / file_name

        # If file exists, append unique suffix
        counter = 1
        while dest_path.exists():
            dest_path = target_dir / f"{safe_view}_{counter}{extension.lower()}"
            file_name = dest_path.name
            counter += 1

        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        rel_path = self.get_relative_path(dest_path)
        return dest_path, rel_path, file_name

    def delete_image_file(self, relative_path: str) -> bool:
        """Deletes file and cleans up empty parent directories if any."""
        full_path = self.base_dir / relative_path
        if full_path.exists():
            full_path.unlink()
            # Clean empty directories up to base_dir
            parent = full_path.parent
            while parent != self.base_dir:
                if not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                else:
                    break
            return True
        return False


storage_service = ImageStorageService()
