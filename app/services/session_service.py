from fastapi import (
    Request,
    Response
)

from repositories.redis.session_repo import SessionRepo
from schemas.session import SessionCreate, SessionResponse
from models.redis.sessions import Session
from models.users import User
from core import exceptions


class SessionService:
    session_repo: SessionRepo
    session_ttl: int
    cookie_name: str
    cookie_secure: bool
    cookie_httponly: bool
    cookie_samesite: str

    def __init__(
        self,
        session_repo: SessionRepo,
        session_ttl: int = 60 * 60,
        cookie_name: str = 'session_id',
        cookie_secure: bool = False,
        cookie_httponly: bool = True,
        cookie_samesite: str = 'lax'
    ):
        self.session_repo = session_repo
        self.session_ttl = session_ttl
        self.cookie_name = cookie_name
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

    def _set_cookie(
        self,
        session_id: str,
        response: Response
    ) -> None:
        response.set_cookie(
            key=self.cookie_name,
            value=session_id,
            httponly=self.cookie_httponly,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            max_age=self.session_ttl,
            path='/'
        )

    def _delete_cookie(
        self,
        response: Response
    ) -> None:
        response.delete_cookie(
            key=self.cookie_name,
            httponly=self.cookie_httponly,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            path='/'
        )

    def get_session_response_model(
        self,
        session: Session
    ) -> SessionResponse:
        session_dict = session.model_dump()
        session_pk = session_dict.pop('pk')
        session_dict['session_id'] = session_pk

        return SessionResponse(**session_dict)

    async def create_session(
        self,
        user: User,
        request: Request,
        response: Response
    ) -> SessionResponse:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')

        session_data = SessionCreate(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            expires_in=self.session_ttl,
            ip_address=ip_address,
            user_agent=user_agent
        )

        session = await self.session_repo.create_session(
            session_data
        )

        self._set_cookie(session.pk, response)

        return self.get_session_response_model(session)
    
    async def get_session(
        self,
        session_id: str
    ) -> SessionResponse:
        session = await self.session_repo.get_session_by_id(
            session_id
        )

        if not session:
            raise exceptions.NotFoundException(
                'Session not found'
            )
        
        return self.get_session_response_model(session)
    
    async def update_activity(
        self,
        session_id: str,
        response: Response
    ) -> bool:
        result = await self.session_repo.update_session_activity(
            session_id
        )
        
        if not result:
            return False
        
        self._set_cookie(session_id, response)

        return True
    
    async def delete_session(
        self,
        session_id: str,
        response: Response
    ) -> bool:
        result = await self.session_repo.delete_session(
            session_id
        )

        if not result:
            return False
        
        self._delete_cookie(response)

        return True
    
    async def delete_all_sessions(
        self
    ) -> int:
        return await self.session_repo.delete_all_sessions()
