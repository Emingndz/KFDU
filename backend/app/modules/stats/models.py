from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class UserGoal(Base, TimestampMixin):
    __tablename__ = "user_goals"
    __table_args__ = (
        UniqueConstraint("user_id", "year", "media_type", name="uq_user_goals_user_year_type"),
        CheckConstraint("media_type IN ('movie', 'tv', 'book')", name="media_type_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    media_type: Mapped[str] = mapped_column(nullable=False)
    target: Mapped[int] = mapped_column(nullable=False)
