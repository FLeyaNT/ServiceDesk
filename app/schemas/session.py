from pydantic import BaseModel

from datetime import datetime

from models.users import UserRole


class BaseSession(BaseModel):
    user_id: int
    username: str
    role: UserRole
    full_name: str
    expires_in: int
    ip_address: str | None = None
    user_agent: str | None = None


class SessionCreate(BaseSession):
    pass


class SessionData(BaseSession):
    session_id: str
    created_at: datetime
    last_activity: datetime


class SessionResponse(SessionData):
    pass


class SessionUser(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
