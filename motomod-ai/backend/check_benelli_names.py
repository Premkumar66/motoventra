import asyncio
from app.core.database import AsyncSessionLocal
from app.models.motorcycle import Motorcycle, Brand
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Motorcycle).join(Brand).where(Brand.name == 'Benelli'))
        for m in res.scalars().all():
            print(f"Model Name: '{m.name}' | Slug: '{m.slug}'")

if __name__ == '__main__':
    asyncio.run(main())
