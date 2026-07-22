"""
MotoMod AI — Motorcycle Catalog Routing
Endpoints to query brands, motorcycle models, specs, and compare different models.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
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
