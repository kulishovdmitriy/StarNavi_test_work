from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
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

    def check_profanity(self):
        profanity_list = ["плохое_слово1", "плохое_слово2"]
        content_lower = self.content.lower()
        title_lower = self.title.lower()

        for word in profanity_list:
            if word in content_lower or word in title_lower:
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

    def check_profanity(self):

        profanity_list = ["плохое_слово1", "плохое_слово2"]
        for word in profanity_list:
            if word in self.description.lower():
                self.is_blocked = True
                return True
        return False