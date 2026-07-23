"""
MotoVentra — Modifications & Compatibility Routing
Endpoints to query modification products, categories, and evaluate component compatibility.

STRICT COMPATIBILITY ENGINE: Every part is only shown for compatible motorcycles.
Universal parts (is_universal=True) are shown for all bikes.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.modifications import ModificationCategoryModel, Modification, ModificationCompatibility
from app.schemas.motorcycle import (
    ModificationCategoryResponse, CompatibilityCheckRequest, CompatibilityCheckResponse
)
from app.schemas.auth import PaginationMeta

router = APIRouter(prefix="/modifications", tags=["Modifications Catalog"])


@router.get(
    "/categories",
    response_model=List[ModificationCategoryResponse],
    summary="Get all modification categories"
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    query = select(ModificationCategoryModel).filter_by(is_active=True).order_by(
        ModificationCategoryModel.sort_order.asc()
    )
    res = await db.execute(query)
    return res.scalars().all()


@router.get(
    "/accessories",
    summary="List modification accessories with optional variant and category filtering"
)
async def get_accessories(
    variant_id: Optional[UUID] = Query(None, description="Filter by motorcycle variant compatibility"),
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    from app.models.modifications import ModificationCompatibility, ModificationCategoryModel
    offset = (page - 1) * per_page
    
    if variant_id:
        # Strict filtering: only parts compatible with this variant OR universal parts
        compat_subq = (
            select(ModificationCompatibility.modification_id)
            .where(ModificationCompatibility.variant_id == variant_id)
            .scalar_subquery()
        )
        base_query = (
            select(Modification)
            .where(
                Modification.is_active == True,
                or_(
                    Modification.id.in_(compat_subq),
                    Modification.is_universal == True
                )
            )
        )
    else:
        base_query = select(Modification).where(Modification.is_active == True)
    
    if category_slug:
        cat_subq = select(ModificationCategoryModel.id).where(ModificationCategoryModel.slug == category_slug).scalar_subquery()
        base_query = base_query.where(Modification.category_id.in_(cat_subq))
    
    if featured is not None:
        base_query = base_query.where(Modification.is_featured == featured)
    
    count_res = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_res.scalar() or 0
    
    items_res = await db.execute(
        base_query.options(
            selectinload(Modification.category),
            selectinload(Modification.images)
        ).order_by(Modification.is_featured.desc(), Modification.brand_name.asc()).offset(offset).limit(per_page)
    )
    items = items_res.scalars().all()
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": [
            {
                "id": str(m.id),
                "category_id": str(m.category_id),
                "category": {
                    "id": str(m.category.id),
                    "name": m.category.name,
                    "slug": m.category.slug,
                    "icon_url": m.category.icon_url,
                } if m.category else None,
                "brand_name": m.brand_name,
                "model_name": m.model_name,
                "slug": m.slug,
                "sku": m.sku,
                "short_description": m.short_description,
                "price_inr": m.price_inr,
                "price_usd": m.price_usd,
                "hp_change_bhp": m.hp_change_bhp,
                "hp_change_percent": m.hp_change_percent,
                "torque_change_nm": m.torque_change_nm,
                "torque_change_percent": m.torque_change_percent,
                "mileage_change_kmpl": m.mileage_change_kmpl,
                "weight_change_kg": m.weight_change_kg,
                "noise_level_db": m.noise_level_db,
                "material": m.material,
                "warranty_months": m.warranty_months,
                "installation_time_minutes": m.installation_time_minutes,
                "is_featured": m.is_featured,
                "is_legal_for_road": m.is_legal_for_road,
                "is_universal": getattr(m, 'is_universal', False),
                "requires_professional_install": m.requires_professional_install,
                "average_rating": m.average_rating,
                "review_count": m.review_count,
                "image_url": m.images[0].url if m.images else None,
            }
            for m in items
        ],
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "filtered_by_variant": str(variant_id) if variant_id else None,
        }
    }



@router.post(
    "/compatibility-check",
    response_model=CompatibilityCheckResponse,
    summary="Verify compatibility of multiple accessories with a motorcycle variant"
)
async def check_compatibility(
    payload: CompatibilityCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    results = []
    overall_compatible = True

    for mod_id in payload.modification_ids:
        # Load modification
        mod_res = await db.execute(select(Modification).filter_by(id=mod_id))
        mod = mod_res.scalar_one_or_none()

        if not mod:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modification ID {mod_id} not found."
            )

        # Universal parts are always compatible
        if getattr(mod, 'is_universal', False):
            results.append({
                "modification_id": mod_id,
                "is_compatible": True,
                "compatibility_type": "universal",
                "notes": "Universal part compatible with all motorcycles.",
                "ai_confidence": 1.0
            })
            continue

        # Check explicit compatibility entry
        compat_query = select(ModificationCompatibility).filter_by(
            modification_id=mod_id,
            variant_id=payload.variant_id
        )
        res = await db.execute(compat_query)
        entry = res.scalar_one_or_none()

        if entry:
            results.append({
                "modification_id": mod_id,
                "is_compatible": True,
                "compatibility_type": entry.compatibility_type,
                "notes": entry.notes,
                "ai_confidence": entry.ai_confidence or 0.98
            })
        else:
            results.append({
                "modification_id": mod_id,
                "is_compatible": False,
                "compatibility_type": "incompatible",
                "notes": f"This part is not listed as compatible with your motorcycle. It may be designed for a different model.",
                "ai_confidence": 0.95
            })
            overall_compatible = False

    return {
        "variant_id": payload.variant_id,
        "results": results,
        "overall_compatible": overall_compatible
    }
