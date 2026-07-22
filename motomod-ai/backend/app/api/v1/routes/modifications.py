"""
MotoMod AI — Modifications & Compatibility Routing
Endpoints to query modification products, categories, and evaluate component compatibility.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.modifications import ModificationCategoryModel, Modification, ModificationCompatibility
from app.schemas.motorcycle import (
    ModificationCategoryResponse, ModificationResponse, ModificationListResponse,
    CompatibilityCheckRequest, CompatibilityCheckResponse
)
from app.schemas.auth import PaginationMeta

router = APIRouter(prefix="/modifications", tags=["Modifications Catalog"])


@router.get(
    "/categories",
    response_model=List[ModificationCategoryResponse],
    summary="Get all modification categories"
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    query = select(ModificationCategoryModel).filter_by(is_active=True).order_by(ModificationCategoryModel.sort_order.asc())
    res = await db.execute(query)
    return res.scalars().all()


@router.get(
    "/accessories",
    response_model=ModificationListResponse,
    summary="List modification accessories with filtering"
)
async def get_accessories(
    category_id: Optional[UUID] = None,
    brand: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page
    
    query = select(Modification).filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if brand:
        query = query.filter_by(brand_name=brand)
        
    count_query = select(func.count()).select_from(query.subquery())
    count_res = await db.execute(count_query)
    total = count_res.scalar() or 0
    
    items_query = query.options(
        selectinload(Modification.category),
        selectinload(Modification.images)
    ).offset(offset).limit(per_page)
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
        # Check database compatibility entry
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
                "ai_confidence": entry.ai_confidence or 1.0
            })
        else:
            # Check if modification is universal
            mod_res = await db.execute(select(Modification).filter_by(id=mod_id))
            mod = mod_res.scalar_one_or_none()
            
            if mod:
                # Scaffolding default heuristic: if no explicit compatibility check, check is false
                is_compat = False
                results.append({
                    "modification_id": mod_id,
                    "is_compatible": is_compat,
                    "compatibility_type": "incompatible",
                    "notes": "Not explicitly listed as compatible for this model.",
                    "ai_confidence": 0.5
                })
                if not is_compat:
                    overall_compatible = False
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Modification ID {mod_id} not found."
                )
                
    return {
        "variant_id": payload.variant_id,
        "results": results,
        "overall_compatible": overall_compatible
    }
