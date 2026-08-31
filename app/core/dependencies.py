from fastapi import (
    Depends,
    Security
)
from fastapi.security import (
    APIKeyCookie,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from passlib.context import CryptContext

from functools import lru_cache
from typing import (
    Annotated,
    AsyncGenerator,
    Callable
)

from core.config import get_settings
from core.web_socket import WebSocketManager
from core import exceptions
from repositories.redis import SessionRepo
from repositories.postgres import (
    UserRepo,
    IssueTypesRepo,
    InventoryRepo,
    TicketRepo
)
from services import (
    SessionService,
    HashService,
    UserService,
    AuthService,
    IssueTypesService,
    InventoryService,
    TicketService
)
from schemas.session import SessionUser
from models.users import UserRole
from core.role_hierarchy import ROLE_HIERARCHY


settings = get_settings()


# ===============================================
#                   PostgreSQL
# ===============================================


@lru_cache(maxsize=1)
def get_pg_engine() -> AsyncEngine:
    return create_async_engine(
        settings.async_postgres_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True
    )


@lru_cache(maxsize=1)
def get_pg_sessionmaker(
    engine: AsyncEngine = Depends(get_pg_engine)
) -> async_sessionmaker:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )


async def get_pg_session(
    sessionmaker: async_sessionmaker = Depends(
        get_pg_sessionmaker
    )
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


PgSessionDep = Annotated[
    AsyncSession,
    Depends(get_pg_session)
]


# ===============================================
#                 Repositories
# ===============================================


@lru_cache(maxsize=1)
def get_session_repo() -> SessionRepo:
    return SessionRepo()

SessionRepoDep = Annotated[
    SessionRepo,
    Depends(get_session_repo)
]


def get_pg_user_repo(
    session: PgSessionDep
) -> UserRepo:
    return UserRepo(session)

PgUserRepoDep = Annotated[
    UserRepo,
    Depends(get_pg_user_repo)
]


def get_pg_issue_types_repo(
    session: PgSessionDep
) -> IssueTypesRepo:
    return IssueTypesRepo(session)

PgIssueTypesRepoDep = Annotated[
    IssueTypesRepo,
    Depends(get_pg_issue_types_repo)
]


def get_pg_inventory_repo(
    session: PgSessionDep
) -> InventoryRepo:
    return InventoryRepo(session)

PgInventoryRepoDep = Annotated[
    InventoryRepo,
    Depends(get_pg_inventory_repo)
]


def get_pg_ticket_repo(
    session: PgSessionDep
) -> TicketRepo:
    return TicketRepo(session)

PgTicketRepoDep = Annotated[
    TicketRepo,
    Depends(get_pg_ticket_repo)
]


# ===============================================
#                 Services
# ===============================================


@lru_cache(maxsize=1)
def get_session_service(
    session_repo: SessionRepoDep
) -> SessionService:
    return SessionService(
        session_repo=session_repo,
        session_ttl=settings.session_ttl
    )

SessionServiceDep = Annotated[
    SessionService,
    Depends(get_session_service)
]


@lru_cache(maxsize=1)
def get_hash_service() -> HashService:
    return HashService(
        CryptContext(
            schemes=['argon2'],
            deprecated='auto',
            argon2__rounds=2,
            argon2__memory_cost=102400,
            argon2__parallelism=8,
            argon2__hash_len=32,
            argon2__salt_len=16 
        )
    )

HashServiceDep = Annotated[
    HashService,
    Depends(get_hash_service)
]


def get_user_service(
    user_repo: PgUserRepoDep,
    hash_service: HashServiceDep  
) -> UserService:
    return UserService(
        user_repo=user_repo,
        hash_service=hash_service
    )

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service)
]


def get_auth_service(
    user_service: UserServiceDep,
    session_service: SessionServiceDep
) -> AuthService:
    return AuthService(
        user_service=user_service,
        session_service=session_service
    )

AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service)
]


def get_issue_types_service(
    issue_types_repo: PgIssueTypesRepoDep
) -> IssueTypesService:
    return IssueTypesService(
        issue_types_repo
    )

IssueTypesServiceDep = Annotated[
    IssueTypesService,
    Depends(get_issue_types_service)
]


def get_inventory_service(
    inventory_repo: PgInventoryRepoDep
) -> InventoryService:
    return InventoryService(inventory_repo)

InventoryServiceDep = Annotated[
    InventoryService,
    Depends(get_inventory_service)
]


def get_ticket_service(
    ticket_repo: PgTicketRepoDep,
    inventory_service: InventoryServiceDep,
    issue_types_repo: PgIssueTypesRepoDep  
) -> TicketService:
    return TicketService(
        ticket_repo,
        inventory_service,
        issue_types_repo
    )

TicketServiceDep = Annotated[
    TicketService,
    Depends(get_ticket_service)
]


# ===============================================
#                  Authorization
# ===============================================


security_scheme = APIKeyCookie(
    name=settings.session_cookie_name,
    auto_error=False
)

SessionIdDep = Annotated[
    str,
    Security(security_scheme)
]


async def get_current_user(
    session_id: SessionIdDep,
    session_service: SessionServiceDep
) -> SessionUser:
    if not session_id:
        raise exceptions.UnauthorizedException()
    
    session = await session_service.get_session(session_id)

    return SessionUser(
        id=session.user_id,
        username=session.username,
        full_name=session.full_name,
        role=session.role
    )

CurrentUserDep = Annotated[
    SessionUser,
    Security(get_current_user)
]


# ===============================================
#                  WebSocket
# ===============================================


@lru_cache(maxsize=1)
def get_web_socket_manager():
    return WebSocketManager()

WebSocketManagerDep = Annotated[
    WebSocketManager,
    Depends(get_web_socket_manager)
]


# ===============================================
#                  Permissions
# ===============================================


def require_author(service_dep: Callable):
    
    async def dependency(
        resource_id: int,
        current_user: CurrentUserDep,
        service = Depends(service_dep)
    ) -> SessionUser:
        resource = await service.get_by_id(
            resource_id,
            raw_model=True
        )

        if hasattr(resource, 'created_by'):
            if current_user.id == resource.created_by:
                return current_user
        
        raise exceptions.ForbiddenException()
    
    return dependency


def require_role(role: UserRole):
    
    def dependency(
        current_user: CurrentUserDep
    ) -> SessionUser:
        current_role = UserRole(current_user.role)
        require_role_grade = ROLE_HIERARCHY[role]
        current_role_grade = ROLE_HIERARCHY[current_role]

        if current_role_grade >= require_role_grade:
            return current_user
        
        raise exceptions.ForbiddenException()
    
    return dependency

def require_role_or_author(
    service_dep: Callable,
    role: UserRole
):
    
    async def dependency(
        resource_id: int,
        current_user: CurrentUserDep,
        service = Depends(service_dep)
    ):
        resource = await service.get_by_id(
            resource_id,
            raw_model=True
        )

        current_role = UserRole(current_user.role)
        require_role_grade = ROLE_HIERARCHY[role]
        current_role_grade = ROLE_HIERARCHY[current_role]

        if hasattr(resource, 'created_by'):
            if (
                current_user.id == resource.created_by
                or current_role_grade >= require_role_grade
            ):
                return current_user
            
        raise exceptions.ForbiddenException()

    return dependency
