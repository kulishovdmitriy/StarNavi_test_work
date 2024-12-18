from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, generics

from src.services.google_analyze_content import analyze_content_post, analyze_content_comment
from src.services.logger import setup_logger


logger = setup_logger(__name__)


class Base(DeclarativeBase):
    """
    Base class for all models.
    """
    pass


class Post(Base):

    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(65), index=True)
    content: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    completed: Mapped[bool] = mapped_column(default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    user_id: Mapped[int] = mapped_column(generics.GUID(), ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates="posts", lazy="joined")

    async def check_profanity(self):
        """Checks if the post content contains profanity and marks it as blocked if necessary."""

        response = await analyze_content_post(self.content, self.title)
        if response.get("is_blocked"):
            self.is_blocked = True
            return True
        return False


class Comment(Base):

    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")

    user_id: Mapped[int] = mapped_column(generics.GUID(), ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates="comments", lazy="joined")

    parent_comment_id: Mapped[int] = mapped_column(Integer, ForeignKey('comments.id'), nullable=True)
    parent_comment = relationship("Comment", remote_side=[id])

    async def check_profanity(self):
        """Checks if the comment description contains profanity and marks it as blocked if necessary."""

        logger.info(f"Checking profanity for comment: {self.description}")
        response = await analyze_content_comment(self.description)

        if response.get("is_blocked"):
            self.is_blocked = True
            return True
        return False


class User(SQLAlchemyBaseUserTableUUID, Base):

    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_delay_minutes: Mapped[int] = mapped_column(Integer, default=0)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
