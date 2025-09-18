from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int
    exp: int


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    is_group: bool = False


class ConversationRead(BaseModel):
    id: int
    title: Optional[str] = None
    is_group: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    conversation_id: int
    content: str


class MessageRead(BaseModel):
    id: int
    conversation_id: int
    sender_id: Optional[int]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True





