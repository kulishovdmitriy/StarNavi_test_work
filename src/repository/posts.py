from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post
from src.schemas.posts import CreatePostSchema, UpdatePostSchema


async def get_posts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Post).limit(limit).offset(offset)
    posts = await db.execute(stmt)
    return posts.scalars().all()


async def get_post(post_id: int, db: AsyncSession):
    stmt = select(Post).filter_by(id=post_id)
    post = await db.execute(stmt)
    return post.scalar_one_or_none()


async def create_post(body: CreatePostSchema, db: AsyncSession):
    new_post = Post(**body.model_dump(exclude_unset=True))
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def update_post(post_id: int, body: UpdatePostSchema, db: AsyncSession):
    stmt = select(Post).filter_by(id=post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if post:
        post.title = body.title
        post.content = body.content
        await db.commit()
        await db.refresh(post)
    return post


async def delete_post(post_id: int, db: AsyncSession):
    stmt = select(Post).filter_by(id=post_id)
    post = await db.execute(stmt)
    post = post.scalar_one_or_none()
    if post:
        await db.delete(post)
        await db.commit()
    return post
