from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import decode_token, get_current_user
from .db import get_db_session
from .models import User

async def get_db() -> AsyncSession:
    async for session in get_db_session():
        yield session

async def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not current_user.is_admin: # Changed to current_user.is_admin
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user