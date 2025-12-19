from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from nex.db.mod.secret import Secret

class SecretRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def set(self, key: str, value: str, description: str = None) -> None:
        stmt = select(Secret).where(Secret.key == key)
        result = await self.session.execute(stmt)
        secret = result.scalars().first()
        
        if secret:
            secret.value = value
            if description:
                secret.description = description
        else:
            secret = Secret(key=key, value=value, description=description)
            self.session.add(secret)
        
        await self.session.commit()

    async def get(self, key: str) -> str | None:
        stmt = select(Secret).where(Secret.key == key)
        result = await self.session.execute(stmt)
        secret = result.scalars().first()
        return secret.value if secret else None
