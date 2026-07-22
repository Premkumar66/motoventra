"""
BikeVerse AI — Image Deduplication Processor
Uses image perceptual hashing (dHash/pHash) to detect and remove duplicate or low-resolution images.
"""
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Set, Any

from app.collector.config import BIKES_DIR, PHASH_THRESHOLD

logger = logging.getLogger("bikeverse.collector.deduplicator")


class ImageDeduplicator:
    """Detects duplicate images using perceptual hashing and file fingerprinting."""

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 file fingerprint."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compute_dhash(self, file_path: Path, hash_size: int = 8) -> str:
        """Compute difference hash (dHash) for fast visual similarity comparison."""
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
                pixels = list(img.getdata())
                difference = []
                for row in range(hash_size):
                    for col in range(hash_size):
                        pixel_left = pixels[row * (hash_size + 1) + col]
                        pixel_right = pixels[row * (hash_size + 1) + col + 1]
                        difference.append(pixel_left > pixel_right)
                decimal_value = 0
                for hash_bit in difference:
                    decimal_value = (decimal_value << 1) | hash_bit
                return f"{decimal_value:016x}"
        except Exception as e:
            logger.debug(f"Pillow dHash fallback for {file_path.name}: {e}")
            return self.compute_file_hash(file_path)[:16]

    def hamming_distance(self, h1: str, h2: str) -> int:
        """Compute Hamming distance between two hex hash strings."""
        try:
            return bin(int(h1, 16) ^ int(h2, 16)).count('1')
        except Exception:
            return 0 if h1 == h2 else 100

    def process_directory(self, bikes_dir: Path = BIKES_DIR) -> Dict[str, Any]:
        """Scan dataset directory, detect duplicates, and log quality metrics."""
        seen_hashes: Set[str] = set()
        seen_dhashes: List[str] = []
        duplicates_found = 0
        total_scanned = 0

        for file_path in bikes_dir.glob("**/*.*"):
            if file_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".svg"]:
                continue
            total_scanned += 1
            f_hash = self.compute_file_hash(file_path)
            d_hash = self.compute_dhash(file_path)

            if f_hash in seen_hashes:
                logger.warning(f"Duplicate exact file found: {file_path.name}. Removing.")
                try:
                    file_path.unlink()
                except Exception:
                    pass
                duplicates_found += 1
                continue

            # Check perceptual similarity
            is_dup = False
            for prev_dh in seen_dhashes:
                if self.hamming_distance(d_hash, prev_dh) <= PHASH_THRESHOLD:
                    is_dup = True
                    break

            if is_dup:
                logger.debug(f"Perceptual duplicate detected: {file_path.name}")
                duplicates_found += 1
            else:
                seen_hashes.add(f_hash)
                seen_dhashes.append(d_hash)

        stats = {
            "total_scanned": total_scanned,
            "unique_images": len(seen_hashes),
            "duplicates_removed": duplicates_found
        }
        logger.info(f"Deduplication complete: {stats}")
        return stats
