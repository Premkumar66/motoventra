"""
MotoMod AI — Motorcycle Catalog Routing
Endpoints to query brands, motorcycle models, specs, and compare different models.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.motorcycle import Brand, Motorcycle, MotorcycleVariant
from app.schemas.motorcycle import (
    BrandResponse, BrandListResponse, MotorcycleResponse, MotorcycleListResponse,
    VariantSpecsResponse, VariantListItem
)
from app.schemas.auth import PaginationMeta

router = APIRouter(prefix="/bikes", tags=["Motorcycle Catalog"])


@router.get(
    "/brands",
    response_model=BrandListResponse,
    summary="List all motorcycle brands"
)
async def get_brands(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page
    
    # Query count and items
    count_query = select(func.count(Brand.id)).filter_by(is_active=True)
    count_res = await db.execute(count_query)
    total = count_res.scalar() or 0
    
    items_query = select(Brand).filter_by(is_active=True).order_by(Brand.sort_order.asc(), Brand.name.asc()).offset(offset).limit(per_page)
    items_res = await db.execute(items_query)
    items = items_res.scalars().all()
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": items,
        "meta": PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    }


@router.get(
    "/motorcycles",
    response_model=MotorcycleListResponse,
    summary="List models under a brand or category"
)
async def get_motorcycles(
    brand_id: Optional[UUID] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page
    
    query = select(Motorcycle).filter_by(is_active=True)
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if category:
        query = query.filter_by(category=category)
        
    count_query = select(func.count()).select_from(query.subquery())
    count_res = await db.execute(count_query)
    total = count_res.scalar() or 0
    
    items_query = query.options(
        selectinload(Motorcycle.brand),
        selectinload(Motorcycle.variants)
    ).order_by(Motorcycle.sort_order.asc(), Motorcycle.name.asc()).offset(offset).limit(per_page)
    items_res = await db.execute(items_query)
    items = items_res.scalars().all()
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": items,
        "meta": PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    }


@router.get(
    "/variants/{variant_id}/full-details",
    summary="Get complete bike details including images, 3D models, compatible parts"
)
async def get_variant_full_details(
    variant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Returns all sections needed for the Bike Detail modal."""
    from app.models.modifications import Modification, ModificationCompatibility
    
    q = select(MotorcycleVariant).options(
        selectinload(MotorcycleVariant.motorcycle).selectinload(Motorcycle.brand),
        selectinload(MotorcycleVariant.images)
    ).filter_by(id=variant_id, is_active=True)
    res = await db.execute(q)
    variant = res.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="Motorcycle variant not found.")
    
    compat_subq = (
        select(ModificationCompatibility.modification_id)
        .where(ModificationCompatibility.variant_id == variant_id)
        .scalar_subquery()
    )
    mods_q = select(Modification).options(
        selectinload(Modification.category),
        selectinload(Modification.images)
    ).where(
        Modification.is_active == True,
        or_(Modification.id.in_(compat_subq), Modification.is_universal == True)
    )
    mods_res = await db.execute(mods_q)
    all_mods = mods_res.scalars().all()
    
    mods_by_category: dict = {}
    for mod in all_mods:
        cat_name = mod.category.name if mod.category else "Other"
        cat_slug = mod.category.slug if mod.category else "other"
        if cat_slug not in mods_by_category:
            mods_by_category[cat_slug] = {"category_name": cat_name, "category_slug": cat_slug, "items": []}
        mods_by_category[cat_slug]["items"].append({
            "id": str(mod.id),
            "brand_name": mod.brand_name,
            "model_name": mod.model_name,
            "price_inr": mod.price_inr,
            "hp_change_bhp": mod.hp_change_bhp,
            "torque_change_nm": mod.torque_change_nm,
            "mileage_change_kmpl": mod.mileage_change_kmpl,
            "material": mod.material,
            "image_url": mod.images[0].url if mod.images else None,
            "is_universal": mod.is_universal,
        })
    
    moto = variant.motorcycle
    brand = moto.brand if moto else None
    images = [
        {
            "url": img.url, "thumbnail_url": img.thumbnail_url,
            "alt_text": img.alt_text, "color_name": img.color_name,
            "image_type": img.image_type, "is_primary": img.is_primary, "sort_order": img.sort_order,
        }
        for img in sorted(variant.images, key=lambda x: (not x.is_primary, x.sort_order))
    ]
    primary_image = (
        getattr(variant, 'primary_image_url', None) or
        (images[0]["url"] if images else
         f"/api/v1/bikes/placeholder/{brand.slug if brand else 'unknown'}/{moto.slug if moto else 'unknown'}")
    )
    return {
        "id": str(variant.id), "variant_name": variant.variant_name, "year": variant.year,
        "primary_image": primary_image,
        "three_d_model_url": getattr(variant, 'three_d_model_url', None),
        "spin_360_urls": getattr(variant, 'spin_360_urls', None) or [],
        "images": images,
        "brand": {"id": str(brand.id), "name": brand.name, "slug": brand.slug, "logo_url": brand.logo_url} if brand else None,
        "model": {"id": str(moto.id), "name": moto.name, "slug": moto.slug, "category": moto.category.value if moto else None} if moto else None,
        "specs": {
            "engine_cc": variant.engine_cc, "engine_type": variant.engine_type,
            "cylinders": variant.cylinders, "fuel_type": variant.fuel_type.value if variant.fuel_type else None,
            "horsepower_bhp": variant.horsepower_bhp, "horsepower_rpm": variant.horsepower_rpm,
            "torque_nm": variant.torque_nm, "torque_rpm": variant.torque_rpm,
            "top_speed_kmh": variant.top_speed_kmh, "mileage_kmpl": variant.mileage_kmpl,
            "mileage_city_kmpl": variant.mileage_city_kmpl, "mileage_highway_kmpl": variant.mileage_highway_kmpl,
            "acceleration_0_100": variant.acceleration_0_100,
            "transmission": variant.transmission.value if variant.transmission else None,
            "gear_count": variant.gear_count, "weight_kg": variant.weight_kg,
            "kerb_weight_kg": variant.kerb_weight_kg, "wheelbase_mm": variant.wheelbase_mm,
            "seat_height_mm": variant.seat_height_mm, "ground_clearance_mm": variant.ground_clearance_mm,
            "fuel_tank_liters": variant.fuel_tank_liters,
            "front_suspension": variant.front_suspension, "rear_suspension": variant.rear_suspension,
            "front_brake": variant.front_brake, "rear_brake": variant.rear_brake,
            "has_abs": variant.has_abs, "abs_type": variant.abs_type,
            "front_tyre": variant.front_tyre, "rear_tyre": variant.rear_tyre,
            "instrument_cluster": variant.instrument_cluster, "headlight_type": variant.headlight_type,
            "has_led_tail": variant.has_led_tail, "has_traction_control": variant.has_traction_control,
            "has_ride_modes": variant.has_ride_modes, "has_quickshifter": variant.has_quickshifter,
            "has_bluetooth": variant.has_bluetooth, "electronics_features": variant.electronics_features,
            "price_inr": variant.price_inr, "price_usd": variant.price_usd,
            "official_colors": variant.official_colors,
        },
        "compatible_parts": list(mods_by_category.values()),
    }


@router.get(
    "/variants/{variant_id}",
    response_model=VariantSpecsResponse,
    summary="Retrieve full specifications of a variant"
)
async def get_variant_by_id(
    variant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    query = select(MotorcycleVariant).options(selectinload(MotorcycleVariant.motorcycle)).filter_by(id=variant_id, is_active=True)
    res = await db.execute(query)
    variant = res.scalar_one_or_none()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorcycle variant specs not found."
        )
        
    return variant


@router.get(
    "/motorcycles/{motorcycle_id}/variants",
    response_model=List[VariantListItem],
    summary="Get all variants of a specific motorcycle model"
)
async def get_motorcycle_variants(
    motorcycle_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    query = select(MotorcycleVariant).filter_by(motorcycle_id=motorcycle_id, is_active=True).order_by(MotorcycleVariant.year.desc())
    res = await db.execute(query)
    return res.scalars().all()


@router.get(
    "/placeholder/{brand_slug}/{model_slug}",
    summary="Dynamic SVG placeholder for bikes without photos"
)
async def get_bike_placeholder(brand_slug: str, model_slug: str):
    from fastapi.responses import Response
    brand_name = brand_slug.replace("-", " ").title()
    model_name = model_slug.replace("-", " ").title()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#060b18"/>
      <stop offset="100%" style="stop-color:#0d1525"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00f2fe"/>
      <stop offset="100%" style="stop-color:#9b51e0"/>
    </linearGradient>
  </defs>
  <rect width="800" height="500" fill="url(#bg)"/>
  <circle cx="400" cy="200" r="130" fill="none" stroke="url(#accent)" stroke-width="1" opacity="0.2"/>
  <g transform="translate(400,210)" opacity="0.6">
    <circle cx="-120" cy="60" r="55" fill="none" stroke="#00f2fe" stroke-width="4"/>
    <circle cx="-120" cy="60" r="28" fill="none" stroke="#00f2fe" stroke-width="2"/>
    <circle cx="120" cy="60" r="55" fill="none" stroke="#9b51e0" stroke-width="4"/>
    <circle cx="120" cy="60" r="28" fill="none" stroke="#9b51e0" stroke-width="2"/>
    <line x1="-65" y1="60" x2="65" y2="60" stroke="#00f2fe" stroke-width="6" stroke-linecap="round"/>
    <line x1="-40" y1="60" x2="0" y2="-40" stroke="#00f2fe" stroke-width="5" stroke-linecap="round"/>
    <line x1="40" y1="60" x2="0" y2="-40" stroke="#9b51e0" stroke-width="5" stroke-linecap="round"/>
    <rect x="-25" y="-10" width="50" height="40" rx="6" fill="none" stroke="#6b7fa8" stroke-width="3"/>
    <path d="M -30,-40 Q 0,-60 40,-40" fill="none" stroke="#00f2fe" stroke-width="5" stroke-linecap="round"/>
    <line x1="-70" y1="10" x2="-120" y2="60" stroke="#6b7fa8" stroke-width="4"/>
    <line x1="-80" y1="10" x2="-120" y2="60" stroke="#6b7fa8" stroke-width="4"/>
  </g>
  <text x="400" y="370" text-anchor="middle" font-family="Arial,sans-serif" font-size="28" font-weight="900" fill="url(#accent)">{brand_name}</text>
  <text x="400" y="400" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" fill="#6b7fa8">{model_name}</text>
  <text x="400" y="455" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="rgba(107,127,168,0.5)" letter-spacing="3">IMAGE COMING SOON</text>
  <rect x="0" y="0" width="800" height="3" fill="url(#accent)" opacity="0.8"/>
</svg>'''
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})
