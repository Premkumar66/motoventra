"""
MotoVentra - Strict Modification Parts Seed
Each part is mapped ONLY to specifically compatible motorcycle variants.
NO generic catch-all compatibility - every mapping is intentional and accurate.
"""
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.modifications import (
    ModificationCategoryModel, Modification, ModificationImage, ModificationCompatibility
)
from app.models.motorcycle import MotorcycleVariant, Motorcycle, Brand


CAT_DEFINITIONS = [
    {"name": "Exhaust Systems", "slug": "exhaust-systems", "enum": "exhaust", "icon": "🔥", "affects_performance": True, "affects_mileage": True, "requires_dyno": True, "sort": 1},
    {"name": "Performance Air Filters", "slug": "performance-air-filters", "enum": "air_filter", "icon": "💨", "affects_performance": True, "affects_mileage": True, "sort": 2},
    {"name": "ECU Chips & Tuning", "slug": "ecu-chips-tuning", "enum": "ecu_tune", "icon": "⚡", "affects_performance": True, "requires_dyno": True, "sort": 3},
    {"name": "Fuel Optimizers & Modules", "slug": "fuel-optimizers", "enum": "fuelx", "icon": "🔋", "affects_performance": True, "affects_mileage": True, "sort": 4},
    {"name": "Auxiliary Lights & Lighting", "slug": "lights-auxiliary", "enum": "fog_lights", "icon": "💡", "sort": 5},
    {"name": "Bumpers & Crash Protection", "slug": "bumpers-crash-guards", "enum": "crash_guards", "icon": "🛡️", "sort": 6},
    {"name": "Windshields & Aerodynamics", "slug": "windshields-visors", "enum": "windshield", "icon": "🎐", "sort": 7},
    {"name": "Performance Tyres", "slug": "performance-tyres", "enum": "tyres", "icon": "🛞", "sort": 8},
    {"name": "Ergonomics & Touring Seats", "slug": "touring-seats", "enum": "seats", "icon": "🪑", "sort": 9},
    {"name": "High Performance Brakes", "slug": "high-performance-brakes", "enum": "brake_pads", "icon": "🔴", "sort": 10},
    {"name": "Mirrors & Visibility", "slug": "mirrors", "enum": "mirrors", "icon": "🪞", "sort": 11},
    {"name": "Headlights & Tail Lights", "slug": "lighting-headtail", "enum": "headlights", "icon": "🔦", "sort": 12},
]


MODIFICATION_PRODUCTS = [
    # ═══════════════════════════════════════════════════
    # EXHAUST SYSTEMS - Specific per model
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "exhaust-systems",
        "brand": "AEW Exhausts",
        "model": "AEW 102 Stainless Steel Full Exhaust System",
        "slug": "aew-102-stainless-gt650",
        "sku": "AEW-102-GT650",
        "short_desc": "Hand-crafted 102mm stainless steel full exhaust with baffle for Continental GT 650 & Interceptor 650",
        "price_inr": 22500.0,
        "price_usd": 270.0,
        "hp_change": 3.5, "tq_change": 3.0, "ml_change": -0.8,
        "weight_change": -3.2, "noise_db": 96.0,
        "material": "Stainless Steel 304",
        "warranty": 12,
        "legal": True,
        "install_mins": 90,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Powerage Performance",
        "model": "Powerage GT 650 Short Muffler Slip-On Exhaust",
        "slug": "powerage-gt650-slip-on",
        "sku": "PWR-GT650-SLP",
        "short_desc": "Deep throaty sound with 5dB louder note; plug-and-play slip-on for GT 650",
        "price_inr": 12800.0,
        "price_usd": 154.0,
        "hp_change": 2.0, "tq_change": 1.8, "ml_change": -0.5,
        "weight_change": -1.8, "noise_db": 94.0,
        "material": "Stainless Steel / Heat Wrap",
        "warranty": 6,
        "legal": True,
        "install_mins": 45,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Red Rooster Performance",
        "model": "RRP 650 Twin Stainless Exhaust System",
        "slug": "rrp-650-twin-exhaust",
        "sku": "RRP-650-TWIN",
        "short_desc": "Premium twin-exit stainless steel exhaust specifically designed for RE 650 Twins; +4BHP",
        "price_inr": 18500.0,
        "price_usd": 222.0,
        "hp_change": 4.0, "tq_change": 3.5, "ml_change": -0.9,
        "weight_change": -4.1, "noise_db": 98.0,
        "material": "Stainless Steel 316L",
        "warranty": 12,
        "legal": False,
        "install_mins": 120,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Zard",
        "model": "Zard GT 650 Racing Full Titanium Exhaust",
        "slug": "zard-gt650-titanium-racing",
        "sku": "ZRD-GT650-TI",
        "short_desc": "Italian-made full titanium racing exhaust for Continental GT 650; race-track ready",
        "price_inr": 58000.0,
        "price_usd": 696.0,
        "hp_change": 6.8, "tq_change": 5.5, "ml_change": -1.5,
        "weight_change": -5.5, "noise_db": 102.0,
        "material": "Titanium Grade 9",
        "warranty": 24,
        "legal": False,
        "install_mins": 150,
        "compatible_model_slugs": ["continental-gt-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Akrapovic",
        "model": "Akrapovic S-Y10SO47-HAPC Slip-On Racing Exhaust",
        "slug": "akrapovic-r15v4-slip-on",
        "sku": "AKR-R15V4-SO",
        "short_desc": "World-class Akrapovic titanium slip-on system for Yamaha R15 V4; race-proven +5.2bhp",
        "price_inr": 68500.0,
        "price_usd": 822.0,
        "hp_change": 5.2, "tq_change": 3.8, "ml_change": -1.2,
        "weight_change": -4.1, "noise_db": 99.0,
        "material": "Titanium / Carbon Fibre",
        "warranty": 24,
        "legal": False,
        "install_mins": 60,
        "compatible_model_slugs": ["r15-v4", "r15", "yzf-r15"],
        "image": "/static/images/yamaha_r15_v4.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Austin Racing",
        "model": "Austin Racing GP1R Titanium Full System",
        "slug": "austin-racing-gp1r-duke390",
        "sku": "AR-GP1R-D390",
        "short_desc": "Race-grade GP1R full titanium system for KTM Duke 390; track-only loud performance",
        "price_inr": 42000.0,
        "price_usd": 504.0,
        "hp_change": 5.5, "tq_change": 4.8, "ml_change": -1.1,
        "weight_change": -3.8, "noise_db": 101.0,
        "material": "Titanium",
        "warranty": 12,
        "legal": False,
        "install_mins": 120,
        "compatible_model_slugs": ["duke-390", "rc-390"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Akrapovic",
        "model": "Akrapovic Evolution Full Exhaust (CBR650R)",
        "slug": "akrapovic-cbr650r-evolution",
        "sku": "AKR-CBR650R-EV",
        "short_desc": "Full titanium system for Honda CBR650R; dyno-proven +8 BHP gain",
        "price_inr": 82000.0,
        "price_usd": 984.0,
        "hp_change": 8.0, "tq_change": 5.2, "ml_change": -1.8,
        "weight_change": -6.2, "noise_db": 103.0,
        "material": "Titanium / Carbon",
        "warranty": 24,
        "legal": False,
        "install_mins": 180,
        "compatible_model_slugs": ["cbr-650r", "cbr650r", "cb650r"],
        "image": "/static/images/honda_cbr_650r_1784353816828.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Akrapovic",
        "model": "Akrapovic Racing Line Full Exhaust (Ninja 400)",
        "slug": "akrapovic-ninja400-racing-line",
        "sku": "AKR-N400-RL",
        "short_desc": "Stainless steel full system optimized for Kawasaki Ninja 400; street-legal version available",
        "price_inr": 55000.0,
        "price_usd": 660.0,
        "hp_change": 5.0, "tq_change": 4.2, "ml_change": -1.0,
        "weight_change": -3.6, "noise_db": 98.0,
        "material": "Stainless / Titanium",
        "warranty": 12,
        "legal": True,
        "install_mins": 90,
        "compatible_model_slugs": ["ninja-400", "ninja400", "z400"],
        "image": "/static/images/kawasaki_ninja_bike_1784354195267.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Borla",
        "model": "Borla ATAK Full Exhaust (Apache RTR 310)",
        "slug": "borla-apache310-atak",
        "sku": "BRL-APRTR310",
        "short_desc": "Performance exhaust for TVS Apache RTR 310; hand-polished stainless construction",
        "price_inr": 18000.0,
        "price_usd": 216.0,
        "hp_change": 3.5, "tq_change": 2.8, "ml_change": -0.7,
        "weight_change": -2.0, "noise_db": 95.0,
        "material": "Stainless Steel",
        "warranty": 12,
        "legal": True,
        "install_mins": 60,
        "compatible_model_slugs": ["apache-rtr-310", "apache-rtr310"],
        "image": "/static/images/tvs_apache_rtr_310.png",
    },
    {
        "category_slug": "exhaust-systems",
        "brand": "Dominator Exhausts",
        "model": "Dominator HP1 Carbon Exhaust (Himalayan 450)",
        "slug": "dominator-himalayan450-hp1",
        "sku": "DOM-HIM450-HP1",
        "short_desc": "Adventure-ready carbon body exhaust for Royal Enfield Himalayan 450; trail-tested",
        "price_inr": 28000.0,
        "price_usd": 336.0,
        "hp_change": 4.0, "tq_change": 3.5, "ml_change": -1.0,
        "weight_change": -3.0, "noise_db": 96.0,
        "material": "Carbon Fibre / Stainless",
        "warranty": 12,
        "legal": True,
        "install_mins": 90,
        "compatible_model_slugs": ["himalayan-450", "himalayan450"],
        "image": "/static/images/re_himalayan_450_bike_1784474579547.png",
    },

    # ═══════════════════════════════════════════════════
    # ECU CHIPS & TUNING - Model-specific
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "ecu-chips-tuning",
        "brand": "PowerTRONIC",
        "model": "PowerTRONIC V4 ECU for RE 650 Twins",
        "slug": "powertronic-v4-re650",
        "sku": "PWR-V4-RE650",
        "short_desc": "Piggyback ECU module for RE 650 Twins; dual map toggle, rev limiter unlock, +6BHP",
        "price_inr": 18000.0,
        "price_usd": 216.0,
        "hp_change": 6.0, "tq_change": 5.2, "ml_change": -0.8,
        "weight_change": 0.0, "noise_db": None,
        "material": "PCB / Aluminium Enclosure",
        "warranty": 24,
        "legal": True,
        "install_mins": 30,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "fuel-optimizers",
        "brand": "FuelX",
        "model": "FuelX Pro Autotune Fuel Optimizer (RE 650)",
        "slug": "fuelx-pro-re650",
        "sku": "FLX-PRO-RE650",
        "short_desc": "Plug-and-play autotune fuel optimizer for RE 650; self-adjusting O2 sensor, +2kmpl",
        "price_inr": 9990.0,
        "price_usd": 120.0,
        "hp_change": 1.5, "tq_change": 1.2, "ml_change": 2.0,
        "weight_change": 0.0, "noise_db": None,
        "material": "PCB",
        "warranty": 12,
        "legal": True,
        "install_mins": 20,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "ecu-chips-tuning",
        "brand": "PowerTRONIC",
        "model": "PowerTRONIC V4 ECU for KTM Duke 390",
        "slug": "powertronic-v4-duke390",
        "sku": "PWR-V4-D390",
        "short_desc": "Dedicated piggyback ECU for KTM Duke 390; Sport/Track map toggle, wheelie control adjust",
        "price_inr": 16500.0,
        "price_usd": 198.0,
        "hp_change": 5.5, "tq_change": 4.8, "ml_change": -0.5,
        "weight_change": 0.0, "noise_db": None,
        "material": "PCB / Aluminium Enclosure",
        "warranty": 24,
        "legal": True,
        "install_mins": 30,
        "compatible_model_slugs": ["duke-390", "rc-390"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },
    {
        "category_slug": "fuel-optimizers",
        "brand": "FuelX",
        "model": "FuelX Pro Autotune for KTM Duke 390",
        "slug": "fuelx-pro-duke390",
        "sku": "FLX-PRO-D390",
        "short_desc": "Auto fuel optimizer for KTM Duke 390; adapts fuelling across RPM range, 10-min install",
        "price_inr": 8490.0,
        "price_usd": 102.0,
        "hp_change": 1.2, "tq_change": 1.0, "ml_change": 1.8,
        "weight_change": 0.0, "noise_db": None,
        "material": "PCB",
        "warranty": 12,
        "legal": True,
        "install_mins": 15,
        "compatible_model_slugs": ["duke-390", "rc-390", "duke-250", "duke-200"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },
    {
        "category_slug": "ecu-chips-tuning",
        "brand": "Bazzaz",
        "model": "Bazzaz Z-FI TC Traction Control + Fuel System (R15 V4)",
        "slug": "bazzaz-zfi-tc-r15v4",
        "sku": "BAZ-ZFI-R15V4",
        "short_desc": "Full traction control + fuel controller for Yamaha R15 V4; race-ready setup",
        "price_inr": 28000.0,
        "price_usd": 336.0,
        "hp_change": 4.8, "tq_change": 3.8, "ml_change": -0.6,
        "weight_change": 0.0, "noise_db": None,
        "material": "PCB / Aluminium",
        "warranty": 12,
        "legal": True,
        "install_mins": 60,
        "compatible_model_slugs": ["r15-v4", "r15", "yzf-r15", "r15-v3"],
        "image": "/static/images/yamaha_r15_v4.png",
    },

    # ═══════════════════════════════════════════════════
    # PERFORMANCE AIR FILTERS
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "performance-air-filters",
        "brand": "K&N Filters",
        "model": "K&N RE-0930 High-Flow Air Filter (RE 650 Twins)",
        "slug": "kn-re0930-re650",
        "sku": "KN-RE0930-650",
        "short_desc": "Drop-in cotton gauze high-flow filter for RE 650 Twins; washable & reusable lifetime filter",
        "price_inr": 5490.0,
        "price_usd": 66.0,
        "hp_change": 1.2, "tq_change": 1.0, "ml_change": 0.8,
        "weight_change": 0.0, "noise_db": None,
        "material": "Cotton Gauze / Aluminium Frame",
        "warranty": 120,
        "legal": True,
        "install_mins": 20,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "performance-air-filters",
        "brand": "DNA Filters",
        "model": "DNA Stage-2 Air Box & Filter (KTM Duke 390)",
        "slug": "dna-stage2-duke390",
        "sku": "DNA-STG2-D390",
        "short_desc": "Complete Stage-2 air box + high-flow filter for KTM Duke 390; +2.5BHP with matching ECU tune",
        "price_inr": 9200.0,
        "price_usd": 110.0,
        "hp_change": 2.5, "tq_change": 2.0, "ml_change": -0.3,
        "weight_change": -0.2, "noise_db": None,
        "material": "Cotton Gauze / ABS Airbox",
        "warranty": 24,
        "legal": True,
        "install_mins": 45,
        "compatible_model_slugs": ["duke-390", "rc-390"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },
    {
        "category_slug": "performance-air-filters",
        "brand": "K&N Filters",
        "model": "K&N YA-1517 High-Flow Air Filter (R15 V4)",
        "slug": "kn-ya1517-r15v4",
        "sku": "KN-YA1517-R15",
        "short_desc": "OEM-replacement K&N filter for Yamaha R15 V4; washable, 10-year warranty",
        "price_inr": 4200.0,
        "price_usd": 50.0,
        "hp_change": 1.0, "tq_change": 0.8, "ml_change": 0.5,
        "weight_change": 0.0, "noise_db": None,
        "material": "Cotton Gauze",
        "warranty": 120,
        "legal": True,
        "install_mins": 15,
        "compatible_model_slugs": ["r15-v4", "r15", "yzf-r15", "r15-v3"],
        "image": "/static/images/yamaha_r15_v4.png",
    },

    # ═══════════════════════════════════════════════════
    # BUMPERS & CRASH GUARDS
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "bumpers-crash-guards",
        "brand": "Zana Motorcycles",
        "model": "Zana Heavy-Duty Bumper & Engine Guard (GT 650)",
        "slug": "zana-bumper-guard-gt650",
        "sku": "ZNA-BUMP-GT650",
        "short_desc": "Powder-coated steel bumper + engine guard with bar-end sliders for Continental GT 650",
        "price_inr": 4800.0,
        "price_usd": 58.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": 1.8, "noise_db": None,
        "material": "Powder-Coated MS Steel",
        "warranty": 12,
        "legal": True,
        "install_mins": 60,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "bumpers-crash-guards",
        "brand": "Legundary",
        "model": "Legundary Crash Protector Kit (GT 650)",
        "slug": "legundary-crash-protector-gt650",
        "sku": "LEG-CRK-GT650",
        "short_desc": "Full crash protector set for Continental GT 650 with frame sliders, bar-end sliders, and engine guards",
        "price_inr": 6500.0,
        "price_usd": 78.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": 2.4, "noise_db": None,
        "material": "6061 Aluminium / Polyoxymethylene",
        "warranty": 12,
        "legal": True,
        "install_mins": 45,
        "compatible_model_slugs": ["continental-gt-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "bumpers-crash-guards",
        "brand": "KTM Powerparts",
        "model": "KTM Powerparts Frame Sliders & Crash Pads (Duke 390)",
        "slug": "ktm-powerparts-sliders-duke390",
        "sku": "KTM-PWR-SLD-390",
        "short_desc": "Genuine KTM Powerparts crash sliders specifically engineered for Duke 390; track-proven",
        "price_inr": 5200.0,
        "price_usd": 62.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": 0.6, "noise_db": None,
        "material": "Anodised Aluminium / POM",
        "warranty": 12,
        "legal": True,
        "install_mins": 30,
        "compatible_model_slugs": ["duke-390", "rc-390", "duke-250"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },
    {
        "category_slug": "bumpers-crash-guards",
        "brand": "Zana Motorcycles",
        "model": "Zana Himalayan 450 Knuckle Guard Set",
        "slug": "zana-knuckle-guard-himalayan450",
        "sku": "ZNA-KNG-HIM450",
        "short_desc": "Heavy-duty aluminium knuckle guards for Himalayan 450; hand protection for trail riding",
        "price_inr": 3800.0,
        "price_usd": 46.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": 0.8, "noise_db": None,
        "material": "6061 Aluminium",
        "warranty": 12,
        "legal": True,
        "install_mins": 20,
        "compatible_model_slugs": ["himalayan-450", "himalayan450"],
        "image": "/static/images/re_himalayan_450_bike_1784474579547.png",
    },

    # ═══════════════════════════════════════════════════
    # WINDSHIELDS & AERODYNAMICS
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "windshields-visors",
        "brand": "Royal Enfield Official",
        "model": "RE Official GT 650 Touring Screen",
        "slug": "re-official-gt650-touring-screen",
        "sku": "RE-TOUR-GT650",
        "short_desc": "Genuine Royal Enfield touring windscreen for Continental GT 650; perfect OEM fit",
        "price_inr": 4500.0,
        "price_usd": 54.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.2,
        "weight_change": 0.5, "noise_db": None,
        "material": "Polycarbonate (3mm)",
        "warranty": 12,
        "legal": True,
        "install_mins": 15,
        "compatible_model_slugs": ["continental-gt-650"],
        "image": "/static/images/re_gt_650_bike_1784474594038.png",
    },
    {
        "category_slug": "windshields-visors",
        "brand": "MotoTorque",
        "model": "MotoTorque Carbon Fibre Racing Visor (GT 650)",
        "slug": "mototorque-carbon-visor-gt650",
        "sku": "MTT-CRVSR-GT650",
        "short_desc": "Real carbon fibre racing visor for Continental GT 650; lightweight aero advantage",
        "price_inr": 7800.0,
        "price_usd": 94.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.3,
        "weight_change": 0.2, "noise_db": None,
        "material": "Carbon Fibre",
        "warranty": 6,
        "legal": True,
        "install_mins": 20,
        "compatible_model_slugs": ["continental-gt-650"],
        "image": "/static/images/re_gt_650_bike_1784474594038.png",
    },
    {
        "category_slug": "windshields-visors",
        "brand": "Puig",
        "model": "Puig Dark Smoke Double Bubble Screen (KTM Duke 390)",
        "slug": "puig-double-bubble-duke390",
        "sku": "PUIG-DB-D390",
        "short_desc": "Spanish-made aerodynamic double bubble windscreen for Duke 390; reduces chest wind pressure",
        "price_inr": 8500.0,
        "price_usd": 102.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.4,
        "weight_change": 0.3, "noise_db": None,
        "material": "Polycarbonate (4mm)",
        "warranty": 12,
        "legal": True,
        "install_mins": 20,
        "compatible_model_slugs": ["duke-390", "rc-390"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },
    {
        "category_slug": "windshields-visors",
        "brand": "Puig",
        "model": "Puig R-Racer Screen (Yamaha R15 V4)",
        "slug": "puig-r-racer-r15v4",
        "sku": "PUIG-RR-R15V4",
        "short_desc": "R-Racer aerodynamic windscreen for Yamaha R15 V4; track-focused design, 5 colour options",
        "price_inr": 7200.0,
        "price_usd": 86.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.5,
        "weight_change": 0.2, "noise_db": None,
        "material": "Polycarbonate",
        "warranty": 12,
        "legal": True,
        "install_mins": 15,
        "compatible_model_slugs": ["r15-v4", "r15", "yzf-r15"],
        "image": "/static/images/yamaha_r15_v4.png",
    },
    {
        "category_slug": "windshields-visors",
        "brand": "Zana Motorcycles",
        "model": "Zana Himalayan 450 Tall Windscreen",
        "slug": "zana-tall-windscreen-himalayan450",
        "sku": "ZNA-WS-HIM450",
        "short_desc": "Tall touring windscreen for Himalayan 450; 50% more wind deflection than stock",
        "price_inr": 3200.0,
        "price_usd": 38.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.3,
        "weight_change": 0.4, "noise_db": None,
        "material": "Polycarbonate (5mm)",
        "warranty": 6,
        "legal": True,
        "install_mins": 15,
        "compatible_model_slugs": ["himalayan-450", "himalayan450"],
        "image": "/static/images/re_himalayan_450_bike_1784474579547.png",
    },

    # ═══════════════════════════════════════════════════
    # SEATS & ERGONOMICS
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "touring-seats",
        "brand": "Motero Comfort",
        "model": "Motero Dual-Gel Touring Seat (RE 650)",
        "slug": "motero-dual-gel-seat-re650",
        "sku": "MTR-GEL-RE650",
        "short_desc": "Memory foam + dual-gel touring seat for RE Continental GT 650; eliminates fatigue on long rides",
        "price_inr": 4200.0,
        "price_usd": 50.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": 0.3, "noise_db": None,
        "material": "Memory Foam / Dual Gel",
        "warranty": 12,
        "legal": True,
        "install_mins": 10,
        "compatible_model_slugs": ["continental-gt-650"],
        "image": "/static/images/re_gt_650_bike_1784474594038.png",
    },

    # ═══════════════════════════════════════════════════
    # LIGHTING
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "lights-auxiliary",
        "brand": "Code6 Lighting",
        "model": "Code6 60W Quad LED Auxiliary Fog Lights",
        "slug": "code6-60w-fog-lights-universal",
        "sku": "C6-FOG-60W-UNI",
        "short_desc": "Universal 60W IP68-rated quad LED fog lights; fits any motorcycle with 22-28mm handlebar",
        "price_inr": 3200.0,
        "price_usd": 38.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": -0.2,
        "weight_change": 0.4, "noise_db": None,
        "material": "Die-Cast Aluminium / IP68 Lens",
        "warranty": 12,
        "legal": True,
        "install_mins": 30,
        "is_universal": True,
        "compatible_model_slugs": [],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "lighting-headtail",
        "brand": "NightEye",
        "model": "NightEye 7-inch LED Projector Headlight Universal",
        "slug": "nighteye-7inch-led-headlight-universal",
        "sku": "NE-7P-LED-UNI",
        "short_desc": "Universal 7-inch H4 LED projector headlight; 6000K white beam, DRL halo ring",
        "price_inr": 4200.0,
        "price_usd": 50.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": -0.4, "noise_db": None,
        "material": "Die-Cast Aluminium",
        "warranty": 24,
        "legal": True,
        "install_mins": 45,
        "is_universal": True,
        "compatible_model_slugs": [],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },

    # ═══════════════════════════════════════════════════
    # PERFORMANCE TYRES
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "performance-tyres",
        "brand": "Metzeler",
        "model": "Metzeler Roadtec 01 SE Tyre Set (RE 650)",
        "slug": "metzeler-roadtec01se-re650",
        "sku": "MET-RT01SE-RE650",
        "short_desc": "Premium touring + sport tyre set for RE 650 Twins; superior wet grip and longevity",
        "price_inr": 18500.0,
        "price_usd": 222.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": -0.4,
        "weight_change": 0.6, "noise_db": None,
        "material": "Silica Rubber Compound",
        "warranty": 0,
        "legal": True,
        "install_mins": 60,
        "compatible_model_slugs": ["continental-gt-650", "interceptor-650"],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
    {
        "category_slug": "performance-tyres",
        "brand": "Michelin",
        "model": "Michelin Power 6 Sport Tyre Set (KTM Duke 390)",
        "slug": "michelin-power6-duke390",
        "sku": "MCH-PWR6-D390",
        "short_desc": "Sport tyre set for KTM Duke 390; XST+ sipe technology for rain confidence",
        "price_inr": 14500.0,
        "price_usd": 174.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": -0.3,
        "weight_change": 0.4, "noise_db": None,
        "material": "Silica Compound",
        "warranty": 0,
        "legal": True,
        "install_mins": 60,
        "compatible_model_slugs": ["duke-390", "duke-250", "rc-390"],
        "image": "/static/images/ktm_duke_390_1784353801208.png",
    },

    # ═══════════════════════════════════════════════════
    # HIGH PERFORMANCE BRAKES
    # ═══════════════════════════════════════════════════
    {
        "category_slug": "high-performance-brakes",
        "brand": "EBC Brakes",
        "model": "EBC Double-H Sintered Brake Pads Universal",
        "slug": "ebc-double-h-pads-universal",
        "sku": "EBC-DH-UNI",
        "short_desc": "Sintered HH-rated brake pads for any disc brake motorcycle; excellent wet and dry performance",
        "price_inr": 3600.0,
        "price_usd": 43.0,
        "hp_change": 0.0, "tq_change": 0.0, "ml_change": 0.0,
        "weight_change": 0.0, "noise_db": None,
        "material": "Sintered Metal Compound",
        "warranty": 6,
        "legal": True,
        "install_mins": 30,
        "is_universal": True,
        "compatible_model_slugs": [],
        "image": "/static/images/royal_enfield_bike_1784354169781.png",
    },
]

async def _get_or_create_category(session: AsyncSession, slug: str, data: dict) -> ModificationCategoryModel:
    res = await session.execute(select(ModificationCategoryModel).where(ModificationCategoryModel.slug == slug))
    cat = res.scalar_one_or_none()
    if cat:
        return cat
    cat = ModificationCategoryModel(
        name=data["name"],
        slug=slug,
        category_enum=data["enum"],
        icon_url=data.get("icon", ""),
        sort_order=data.get("sort", 99),
        is_active=True,
        affects_performance=data.get("affects_performance", False),
        affects_mileage=data.get("affects_mileage", False),
        requires_dyno=data.get("requires_dyno", False),
    )

    session.add(cat)
    await session.flush()
    return cat

async def _get_variant_ids_for_model_slugs(session: AsyncSession, model_slugs: list[str]) -> list:
    if not model_slugs:
        return []
    q = (
        select(MotorcycleVariant.id, Motorcycle.slug)
        .join(Motorcycle, MotorcycleVariant.motorcycle_id == Motorcycle.id)
        .where(Motorcycle.slug.in_(model_slugs))
        .where(MotorcycleVariant.is_active == True)
    )
    res = await session.execute(q)
    return [row[0] for row in res.fetchall()]

async def seed_modification_parts(session: AsyncSession) -> None:
    await session.execute(__import__('sqlalchemy', fromlist=['text']).text('DELETE FROM modification_compatibility'))
    await session.execute(__import__('sqlalchemy', fromlist=['text']).text('DELETE FROM modification_images'))
    await session.execute(__import__('sqlalchemy', fromlist=['text']).text('DELETE FROM modifications'))
    await session.execute(__import__('sqlalchemy', fromlist=['text']).text('DELETE FROM modification_categories'))
    await session.flush()

    cat_by_slug = {}
    for cat_def in CAT_DEFINITIONS:
        cat = await _get_or_create_category(session, cat_def["slug"], cat_def)
        cat_by_slug[cat_def["slug"]] = cat

    seeded_mods = 0
    for prod in MODIFICATION_PRODUCTS:
        cat = cat_by_slug.get(prod["category_slug"])
        if not cat:
            print(f"WARNING: Category {prod['category_slug']} not found, skipping {prod['slug']}")
            continue

        existing = await session.execute(select(Modification).where(Modification.slug == prod["slug"]))
        if existing.scalar_one_or_none():
            continue

        is_universal = prod.get("is_universal", False)

        mod = Modification(
            category_id=cat.id,
            brand_name=prod["brand"],
            model_name=prod["model"],
            slug=prod["slug"],
            sku=prod.get("sku"),
            short_description=prod.get("short_desc"),
            description=prod.get("short_desc"),
            price_inr=prod.get("price_inr"),
            price_usd=prod.get("price_usd"),
            hp_change_bhp=prod.get("hp_change"),
            torque_change_nm=prod.get("tq_change"),
            mileage_change_kmpl=prod.get("ml_change"),
            weight_change_kg=prod.get("weight_change"),
            noise_level_db=prod.get("noise_db"),
            material=prod.get("material"),
            warranty_months=prod.get("warranty"),
            is_legal_for_road=prod.get("legal", True),
            installation_time_minutes=prod.get("install_mins"),
            is_universal=is_universal,
            is_active=True,
            is_featured=False
        )
        session.add(mod)
        await session.flush()
        
        if prod.get("image"):
            img = ModificationImage(
                modification_id=mod.id,
                url=prod["image"],
                is_primary=True,
                sort_order=1
            )
            session.add(img)

        if not is_universal and prod.get("compatible_model_slugs"):
            variant_ids = await _get_variant_ids_for_model_slugs(session, prod["compatible_model_slugs"])
            for vid in variant_ids:
                compat = ModificationCompatibility(
                    modification_id=mod.id,
                    variant_id=vid,
                    compatibility_type="direct_fit",
                    is_verified=True,
                    ai_confidence=1.0
                )
                session.add(compat)
        
        seeded_mods += 1

    await session.commit()
    print(f"Successfully seeded {seeded_mods} modifications with strict variant compatibility.")
