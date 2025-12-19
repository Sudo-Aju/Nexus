from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from nex.db.mod.base import Base


task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('blocker_id', ForeignKey('tasks.id'), primary_key=True),
    Column('blocked_id', ForeignKey('tasks.id'), primary_key=True)
)

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    desc: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="todo")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    

    parent_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    

    children: Mapped[list["Task"]] = relationship("Task", back_populates="parent", cascade="all, delete-orphan")
    parent: Mapped["Task"] = relationship("Task", remote_side=[id], back_populates="children")
    

    blockers: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id==task_dependencies.c.blocked_id,
        secondaryjoin=id==task_dependencies.c.blocker_id,
        back_populates="blocking",
    )
    
    blocking: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id==task_dependencies.c.blocker_id,
        secondaryjoin=id==task_dependencies.c.blocked_id,
        back_populates="blockers",
    )