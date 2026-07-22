"""
BikeVerse AI — Brand Collector
Gathers manufacturer details, brand logos (SVG/PNG), cover images, and saves brand_info.json.
"""
import json
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any

from app.collector.config import TARGET_BRANDS, BRANDS_DIR, USER_AGENT, REQUEST_TIMEOUT
from app.collector.schemas import BrandSchema

logger = logging.getLogger("bikeverse.collector.brand")


class BrandCollector:
    """Collects and stores manufacturer brand metadata and media logos."""

    def __init__(self, brands_dir: Path = BRANDS_DIR):
        self.brands_dir = brands_dir
        self.brands_dir.mkdir(parents=True, exist_ok=True)

    def download_asset(self, url: str, dest_path: Path) -> bool:
        """Download asset file with User-Agent header and timeout."""
        if dest_path.exists() and dest_path.stat().st_size > 500:
            logger.debug(f"Asset already exists: {dest_path.name}")
            return True
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response, open(dest_path, "wb") as out_file:
                out_file.write(response.read())
            logger.info(f"Downloaded asset: {dest_path.name}")
            return True
        except Exception as e:
            logger.warning(f"Could not download asset from {url}: {e}")
            return False

    def collect_brand(self, brand_info: Dict[str, Any]) -> BrandSchema:
        """Collect brand data, download logo/cover, and write brand_info.json."""
        slug = brand_info["slug"]
        b_dir = self.brands_dir / slug
        b_dir.mkdir(parents=True, exist_ok=True)

        logo_file = b_dir / "logo.png"
        cover_file = b_dir / "cover.jpg"
        info_file = b_dir / "brand_info.json"

        # Generate custom SVG/PNG brand badge if remote fetch fails
        logo_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{brand_info['name'].replace(' ', '_')}_logo.svg"
        logo_success = self.download_asset(logo_url, logo_file)
        
        if not logo_success or not logo_file.exists():
            # Create lightweight fallback SVG logo
            svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="120" viewBox="0 0 300 120">
              <rect width="100%" height="100%" fill="#0c1222" rx="12"/>
              <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" fill="#00f2fe" font-family="sans-serif" font-size="24" font-weight="bold">{brand_info['name']}</text>
              <text x="50%" y="80%" dominant-baseline="middle" text-anchor="middle" fill="#6b7fa8" font-family="sans-serif" font-size="12">{brand_info['country']}</text>
            </svg>'''
            with open(b_dir / "logo.svg", "w", encoding="utf-8") as f:
                f.write(svg_content)

        brand_obj = BrandSchema(
            id=slug,
            brand_name=brand_info["name"],
            slug=slug,
            country=brand_info["country"],
            year_founded=brand_info.get("founded"),
            official_website=brand_info.get("website"),
            parent_company=brand_info.get("parent"),
            description=f"{brand_info['name']} is a premier motorcycle manufacturer based in {brand_info['country']}, founded in {brand_info.get('founded', 'N/A')}.",
            popular_models=[],
            logo_path=str((b_dir / "logo.png" if logo_file.exists() else b_dir / "logo.svg").relative_to(self.brands_dir.parent)),
            cover_path=str((b_dir / "cover.jpg").relative_to(self.brands_dir.parent)) if cover_file.exists() else None
        )

        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(brand_obj.model_dump(), f, indent=2)

        logger.info(f"Brand collected: {brand_info['name']}")
        return brand_obj

    def collect_all(self, target_list: List[Dict[str, Any]] = TARGET_BRANDS) -> List[BrandSchema]:
        """Collect all target brands."""
        results = []
        for b in target_list:
            try:
                obj = self.collect_brand(b)
                results.append(obj)
            except Exception as e:
                logger.error(f"Error collecting brand {b.get('name')}: {e}")
        return results
