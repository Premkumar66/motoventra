"""
MotoMod AI — Security & Authentication Dependencies
Helper functions to inject verified user accounts and RBAC access guards into route functions.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token, ACCESS_TOKEN_TYPE, RolePermissions
from app.models.user import User, UserStatus

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Decodes the access token and checks if the user exists and is active.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token, ACCESS_TOKEN_TYPE)
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    if user.status == UserStatus.BANNED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been banned."
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive."
        )
        
    return user


class PermissionGuard:
    """
    Enforces that a user has a specific permission scope.
    """
    def __init__(self, permission: str):
        self.permission = permission

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not RolePermissions.has_permission(current_user.role.value, self.permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )
        return current_user


class RoleGuard:
    """
    Enforces that a user has a specific role.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied due to insufficient role permissions."
            )
        return current_user
