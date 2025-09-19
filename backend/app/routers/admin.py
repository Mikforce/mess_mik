from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..dependencies import admin_required, get_db
from ..models import User
from ..schemas import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_db), admin=Depends(admin_required)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@router.post("/users/{user_id}/toggle_active")
async def toggle_user_active_status(user_id: int, session: AsyncSession = Depends(get_db),
                                    admin=Depends(admin_required)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active  # Toggle the active status
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"detail": f"User {user.email} active status changed to {user.is_active}"}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, session: AsyncSession = Depends(get_db), admin=Depends(admin_required)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    session.add(user)
    await session.commit()
    return {"detail": f"User {user.email} deactivated"}


@router.post("/users/{user_id}/activate")
async def activate_user(user_id: int, session: AsyncSession = Depends(get_db), admin=Depends(admin_required)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    session.add(user)
    await session.commit()
    return {"detail": f"User {user.email} activated"}