from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from nex.db.mod.base import Base

class Stat(Base):
    __tablename__ = "stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    value: Mapped[float] = mapped_column(Float)
