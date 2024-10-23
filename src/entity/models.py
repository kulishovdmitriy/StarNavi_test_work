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
    """
    class Post(Base):
        Represents a blog post in the application.

        Table name in the database is 'posts'.

        Attributes:
            id: The primary key of the post in the database.
            title: The title of the post, indexed and limited to 65 characters.
            content: The main content of the post, limited to 255 characters.
            created_at: The date and time when the post was created, defaults to the current timestamp.
            completed: Indicates whether the post is completed, defaults to False.
            is_blocked: Indicates whether the post is blocked, defaults to False.
            comments: Relationship to the Comment model, with cascade delete-orphan.
            user_id: Foreign key to the user who owns the post.
            user: Relationship to the User model, lazy-loaded.

        Methods:
            async check_profanity():
                Analyzes the content and title of the post for profanity.
                If profanity is found, marks the post as blocked and returns True.
                Otherwise, returns False.
    """

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
        response = await analyze_content_post(self.content, self.title)
        if response.get("is_blocked"):
            self.is_blocked = True
            return True
        return False


class Comment(Base):
    """
    The `Comment` class represents a comment entity in the database. It maps to the `comments` table and includes several
    properties to store comment details and relationships to other entities.

    Attributes
    ----------
    id : int
        The primary key identifier of the comment.
    description : str
        The text content of the comment, limited to 255 characters.
    created_at : date
        The timestamp when the comment was created. This field is automatically set to the current time.
    is_blocked : bool
        A flag indicating whether the comment is blocked. Default is False.
    post_id : int
        The foreign key linking to the related post. References the `posts` table.
    post : relationship
        The relationship to the `Post` entity, showing which post the comment belongs to.
    user_id : generics.GUID
        The foreign key linking to the user who wrote the comment, optional. References the `users` table.
    user : relationship
        The relationship to the `User` entity, indicating the author of the comment.
    parent_comment_id : int
        The foreign key linking to a parent comment if this comment is a reply. References the `comments` table.
    parent_comment : relationship
        The relationship to another `Comment` entity if this comment is a reply.

    Methods
    -------
    check_profanity():
        Asynchronously checks for profanity in the comment's description using an external service. If profanity is detected, sets the comment as blocked.
    """

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
        logger.info(f"Checking profanity for comment: {self.description}")
        response = await analyze_content_comment(self.description)
        logger.info(f"Profanity check response: {response}")
        if response.get("is_blocked"):
            self.is_blocked = True
            return True
        return False


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User defines a user entity for the database.

    Inherits from:
        SQLAlchemyBaseUserTableUUID
        Base

    Table Name:
        users

    Attributes:
        username (str): The username of the user. Must be unique and cannot be null. Maximum length is 50 characters.
        created_at (date): The timestamp when the user was created. Defaults to the current time.
        updated_at (date): The timestamp when the user was last updated. Defaults to the current time and updates automatically.
        auto_reply_enabled (bool): A flag indicating whether automatic reply is enabled for the user. Defaults to False.
        reply_delay_minutes (int): The delay in minutes before sending an automatic reply. Defaults to 0.

    Relationships:
        posts: One-to-many relationship with the Post table.
        comments: One-to-many relationship with the Comment table.
    """

    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_delay_minutes: Mapped[int] = mapped_column(Integer, default=0)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
