from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from nex.db.mod.task import Task

class TaskRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, title: str, desc: str = "", parent_id: int | None = None, start_date: datetime | None = None, due_date: datetime | None = None) -> Task:
        task = Task(title=title, desc=desc, parent_id=parent_id, start_date=start_date, due_date=due_date)
        self.session.add(task)
        await self.session.commit()
        

        stmt = select(Task).where(Task.id == task.id).options(selectinload(Task.children), selectinload(Task.blockers))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> list[Task]:

        stmt = select(Task).options(selectinload(Task.children), selectinload(Task.blockers))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_roots(self) -> list[Task]:
        """Get only top-level tasks (no parent)."""
        stmt = select(Task).where(Task.parent_id == None).options(selectinload(Task.children))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, task_id: int, status: str) -> None:
        task = await self.session.get(Task, task_id)
        if task:
            task.status = status
            await self.session.commit()

    async def update(self, task_id: int, title: str, desc: str, start_date: datetime | None = None, due_date: datetime | None = None) -> None:
        task = await self.session.get(Task, task_id)
        if task:
            task.title = title
            task.desc = desc
            if start_date: task.start_date = start_date
            if due_date: task.due_date = due_date
            await self.session.commit()

    async def add_blocker(self, ticket_id: int, blocker_id: int) -> None:
        task = await self.session.get(Task, ticket_id, options=[selectinload(Task.blockers)])
        blocker = await self.session.get(Task, blocker_id)
        if task and blocker:
            task.blockers.append(blocker)
            await self.session.commit()

    async def delete(self, task_id: int) -> None:
        task = await self.session.get(Task, task_id)
        if task:
            await self.session.delete(task)
            await self.session.commit()