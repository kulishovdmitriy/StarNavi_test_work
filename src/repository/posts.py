from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User
from src.schemas.post import CreatePostSchema, UpdatePostSchema
from src.conf import messages


async def get_posts(limit: int, offset: int, db: AsyncSession, current_user: User):

    stmt = select(Post).filter_by(user=current_user).limit(limit).offset(offset)
    posts = await db.execute(stmt)
    return posts.scalars().all()


async def get_post(post_id: int, db: AsyncSession, current_user: User):

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    post = await db.execute(stmt)
    return post.scalar_one_or_none()


async def create_post(body: CreatePostSchema, db: AsyncSession, current_user: User):

    new_post = Post(**body.model_dump(exclude_unset=True))

    if await new_post.check_profanity():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_CONTAINS_FORBIDDEN_WORDS)

    new_post.user = current_user

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def update_post(post_id: int, body: UpdatePostSchema, db: AsyncSession, current_user: User):

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    post.title = body.title
    post.content = body.content

    if await post.check_profanity():
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_CONTAINS_FORBIDDEN_WORDS)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(post_id: int, db: AsyncSession, current_user: User):

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    await db.delete(post)
    await db.commit()
