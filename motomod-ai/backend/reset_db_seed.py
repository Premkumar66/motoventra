"""
MotoVentra — Database Reset & Re-seed Utility
Drops all tables, recreates schema, seeds all data including strict modification parts.
"""
import asyncio
import sys
import os

# Ensure PYTHONPATH is set
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.base import Base
# Import all models so they register with Base metadata
from app.models.user import User, UserRole, RefreshToken, EmailVerificationToken, PasswordResetToken, Notification, APIKey, AuditLog  # noqa
from app.models.motorcycle import Brand, Motorcycle, MotorcycleVariant, MotorcycleImage  # noqa
from app.models.modifications import (  # noqa
    ModificationCategoryModel, Modification, ModificationImage, ModificationCompatibility
)
from app.models.builds import UserBuild, BuildModification, GarageMotorcycle, Review, Order, OrderItem, PredictionHistory, WishlistItem  # noqa
from app.models.image_dataset import (  # noqa
    ImageLicense, ImageSource, BikeImage, BikeImageBrand, BikeImageModel,
    BikeImageVariant, BikeModelYear, BikeImageMetadata, ImageProcessingLog
)
from app.core.database import AsyncSessionLocal
from app.core.seed import seed_data



async def reset_and_seed():
    from app.core.database import engine, Base

    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Tables dropped.")

    print("Creating all tables with new schema (3D fields, is_universal, etc.)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    print("Running seed_data()...")
    await seed_data()
    print("Database reset & re-seeded successfully!")


    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_and_seed())
