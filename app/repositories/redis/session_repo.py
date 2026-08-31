from aredis_om import NotFoundError

from datetime import datetime, timezone

from models.redis.sessions import Session
from schemas.session import SessionCreate


class SessionRepo:

    def get_prefix(
        self,
        session_id: int
    ) -> str:
        global_prefix = Session.Meta.global_key_prefix
        model_prefix = Session.Meta.model_key_prefix
        return f'{global_prefix}:{model_prefix}:{session_id}'
    
    async def get_session_by_id(
        self,
        session_id: str
    ) -> Session | None:
        try:
            session = await Session.get(session_id)
            return session
        except NotFoundError:
            return None
        
    async def create_session(
        self,
        session_data: SessionCreate
    ) -> Session:
        new_session = Session(
            **session_data.model_dump(),
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc)
        )

        await new_session.save()
        await new_session.expire(new_session.expires_in)

        return new_session
    
    async def delete_session(
        self,
        session_id: str
    ) -> bool:
        deleted = await Session.delete(session_id)
        if not deleted:
            return False
        return True
    
    async def update_session_activity(
        self,
        session_id: str
    ) -> bool:
        session = await self.get_session_by_id(session_id)
        if not session:
            return False
        
        await session.update(last_activity=datetime.now(timezone.utc))
        await session.expire(session.expires_in)

        return True
    
    async def delete_all_sessions(
        self
    ) -> int:
        all_keys = await Session.all_pks()
        
        client = Session.Meta.database

        keys_to_del = []

        async for pk in all_keys:
            keys_to_del.append(self.get_prefix(pk))

        if not keys_to_del:
            return 0
        
        return await client.delete(*keys_to_del)