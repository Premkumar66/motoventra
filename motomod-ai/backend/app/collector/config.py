"""
BikeVerse AI — Global Motorcycle Dataset Collector Configuration
Defines 40+ global motorcycle brands, dataset storage layout, legal scraping settings,
rate limits, image resolution thresholds, and retry policies.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(r"c:\CCP PROJECT\Motoventra\motomod-ai\backend")
DATASET_DIR = BASE_DIR / "dataset"
BRANDS_DIR = DATASET_DIR / "brands"
BIKES_DIR = DATASET_DIR / "bikes"
EXPORTS_DIR = DATASET_DIR / "exports"

# Create directories on load
for d in [DATASET_DIR, BRANDS_DIR, BIKES_DIR, EXPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Global Brand Directory (40+ Global Manufacturers)
TARGET_BRANDS = [
    {"name": "Honda", "slug": "honda", "country": "Japan", "founded": 1948, "website": "https://global.honda/motorcycles", "parent": "Honda Motor Co., Ltd."},
    {"name": "Yamaha", "slug": "yamaha", "country": "Japan", "founded": 1955, "website": "https://global.yamaha-motor.com", "parent": "Yamaha Corporation"},
    {"name": "Suzuki", "slug": "suzuki", "country": "Japan", "founded": 1909, "website": "https://www.globalsuzuki.com/motorcycle", "parent": "Suzuki Motor Corporation"},
    {"name": "Kawasaki", "slug": "kawasaki", "country": "Japan", "founded": 1896, "website": "https://www.kawasaki-cp.khi.co.jp", "parent": "Kawasaki Heavy Industries"},
    {"name": "KTM", "slug": "ktm", "country": "Austria", "founded": 1934, "website": "https://www.ktm.com", "parent": "Pierer Mobility AG"},
    {"name": "Royal Enfield", "slug": "royal-enfield", "country": "India", "founded": 1901, "website": "https://www.royalenfield.com", "parent": "Eicher Motors"},
    {"name": "TVS", "slug": "tvs", "country": "India", "founded": 1978, "website": "https://www.tvsmotor.com", "parent": "TVS Group"},
    {"name": "Bajaj", "slug": "bajaj", "country": "India", "founded": 1945, "website": "https://www.bajajauto.com", "parent": "Bajaj Group"},
    {"name": "Hero", "slug": "hero", "country": "India", "founded": 1984, "website": "https://www.heromotocorp.com", "parent": "Hero Group"},
    {"name": "BMW Motorrad", "slug": "bmw-motorrad", "country": "Germany", "founded": 1923, "website": "https://www.bmw-motorrad.com", "parent": "BMW Group"},
    {"name": "Ducati", "slug": "ducati", "country": "Italy", "founded": 1926, "website": "https://www.ducati.com", "parent": "Audi AG (Volkswagen Group)"},
    {"name": "Triumph", "slug": "triumph", "country": "United Kingdom", "founded": 1983, "website": "https://www.triumphmotorcycles.com", "parent": "Bloor Holdings"},
    {"name": "Harley-Davidson", "slug": "harley-davidson", "country": "United States", "founded": 1903, "website": "https://www.harley-davidson.com", "parent": "Harley-Davidson, Inc."},
    {"name": "Indian Motorcycle", "slug": "indian-motorcycle", "country": "United States", "founded": 1901, "website": "https://www.indianmotorcycle.com", "parent": "Polaris Industries"},
    {"name": "Aprilia", "slug": "aprilia", "country": "Italy", "founded": 1945, "website": "https://www.aprilia.com", "parent": "Piaggio & C. SpA"},
    {"name": "Benelli", "slug": "benelli", "country": "Italy", "founded": 1911, "website": "https://www.benelli.com", "parent": "Qianjiang Motorcycle"},
    {"name": "MV Agusta", "slug": "mv-agusta", "country": "Italy", "founded": 1945, "website": "https://www.mvagusta.com", "parent": "PIERER Mobility AG"},
    {"name": "CFMoto", "slug": "cfmoto", "country": "China", "founded": 1989, "website": "https://www.cfmoto.com", "parent": "Zhejiang CFMoto Power Co., Ltd."},
    {"name": "Moto Guzzi", "slug": "moto-guzzi", "country": "Italy", "founded": 1921, "website": "https://www.motoguzzi.com", "parent": "Piaggio & C. SpA"},
    {"name": "Husqvarna", "slug": "husqvarna", "country": "Sweden", "founded": 1689, "website": "https://www.husqvarna-motorcycles.com", "parent": "Pierer Mobility AG"},
    {"name": "Zero Motorcycles", "slug": "zero-motorcycles", "country": "United States", "founded": 2006, "website": "https://www.zeromotorcycles.com", "parent": "Zero Motorcycles Inc."},
    {"name": "Kymco", "slug": "kymco", "country": "Taiwan", "founded": 1964, "website": "https://www.kymco.com", "parent": "Kwang Yang Motor Co., Ltd."},
    {"name": "SYM", "slug": "sym", "country": "Taiwan", "founded": 1954, "website": "https://www.sym-global.com", "parent": "Sanyang Motor Co., Ltd."},
    {"name": "Keeway", "slug": "keeway", "country": "Hungary", "founded": 1999, "website": "https://www.keeway.com", "parent": "Qianjiang Group"},
    {"name": "Jawa", "slug": "jawa", "country": "Czech Republic", "founded": 1929, "website": "https://www.jawa.eu", "parent": "Classic Legends (Mahindra)"},
    {"name": "Yezdi", "slug": "yezdi", "country": "India", "founded": 1969, "website": "https://www.yezdi.com", "parent": "Classic Legends (Mahindra)"},
    {"name": "BSA", "slug": "bsa", "country": "United Kingdom", "founded": 1861, "website": "https://www.bsacompany.co.uk", "parent": "Classic Legends (Mahindra)"},
    {"name": "Norton", "slug": "norton", "country": "United Kingdom", "founded": 1898, "website": "https://nortonmotorcycles.com", "parent": "TVS Motor Company"},
    {"name": "Ather", "slug": "ather", "country": "India", "founded": 2013, "website": "https://www.atherenergy.com", "parent": "Ather Energy"},
    {"name": "Ultraviolette", "slug": "ultraviolette", "country": "India", "founded": 2016, "website": "https://www.ultraviolette.com", "parent": "Ultraviolette Automotive"},
    {"name": "Ola Electric", "slug": "ola-electric", "country": "India", "founded": 2017, "website": "https://www.olaelectric.com", "parent": "ANI Technologies"},
    {"name": "Matter", "slug": "matter", "country": "India", "founded": 2019, "website": "https://www.matter.in", "parent": "Matter Motor Works"},
    {"name": "Revolt", "slug": "revolt", "country": "India", "founded": 2019, "website": "https://www.revoltmotors.com", "parent": "RattanIndia Enterprises"},
    {"name": "Can-Am", "slug": "can-am", "country": "Canada", "founded": 1972, "website": "https://can-am.brp.com", "parent": "Bombardier Recreational Products (BRP)"},
    {"name": "Moto Morini", "slug": "moto-morini", "country": "Italy", "founded": 1937, "website": "https://motomorini.eu", "parent": "Zhongneng Vehicle Group"},
    {"name": "Lifan", "slug": "lifan", "country": "China", "founded": 1992, "website": "https://www.lifan.com", "parent": "Geely Industry Group"},
    {"name": "QJMotor", "slug": "qjmotor", "country": "China", "founded": 1985, "website": "https://www.qjmotor.com", "parent": "Geely Technology Group"},
    {"name": "Zontes", "slug": "zontes", "country": "China", "founded": 2002, "website": "https://www.zontes.com", "parent": "Guangdong Tayo Motorcycle Technology Co., Ltd."},
    {"name": "Vespa", "slug": "vespa", "country": "Italy", "founded": 1946, "website": "https://www.vespa.com", "parent": "Piaggio & C. SpA"},
    {"name": "Piaggio", "slug": "piaggio", "country": "Italy", "founded": 1884, "website": "https://www.piaggio.com", "parent": "Piaggio & C. SpA"},
]

# Scraping & Download Settings
USER_AGENT = "BikeVerseAI-Bot/1.0 (+https://bikeverse.ai/bot; bot@bikeverse.ai)"
REQUEST_TIMEOUT = 12  # seconds
RATE_LIMIT_DELAY = 0.5  # delay between requests in seconds
MAX_RETRIES = 3

# Image Criteria
MIN_IMAGE_WIDTH = 600
MIN_IMAGE_HEIGHT = 400
TARGET_IMAGES_PER_MODEL = 10
PHASH_THRESHOLD = 6  # Perceptual hash difference threshold for duplicate detection

# Export Paths
CSV_EXPORT_PATH = EXPORTS_DIR / "bikeverse_catalog.csv"
JSON_EXPORT_PATH = EXPORTS_DIR / "bikeverse_catalog.json"
SQLITE_EXPORT_PATH = EXPORTS_DIR / "bikeverse_db.sqlite"
MONGO_EXPORT_PATH = EXPORTS_DIR / "bikeverse_mongo_export.json"
