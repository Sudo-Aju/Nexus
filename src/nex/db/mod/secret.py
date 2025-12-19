from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from nex.db.mod.base import Base

class Secret(Base):
    __tablename__ = "secrets"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
