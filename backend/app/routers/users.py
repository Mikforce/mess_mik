from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..db import get_db_session
from ..models import User
from ..schemas import UserRead


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
async def list_users(_: User = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users





