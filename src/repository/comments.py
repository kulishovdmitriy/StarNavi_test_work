from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.entity.models import Comment
from src.schemas.comments import CreateCommentSchema, UpdateCommentSchema


async def get_comments(post_id: int, db: AsyncSession):
    stmt = select(Comment).where(Comment.post_id == post_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    return comments


async def get_comment_by_post(post_id: int, comment_id: int, db: AsyncSession):
    stmt = select(Comment).filter(Comment.post_id == post_id, Comment.id == comment_id)
    comment = await db.execute(stmt)
    return comment.scalar_one_or_none()


async def create_comment(post_id: int, body: CreateCommentSchema, db: AsyncSession):
    new_comment = Comment(post_id=post_id, **body.model_dump(exclude_unset=True))

    if new_comment.check_profanity():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment contains forbidden words")

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def update_comment(comment_id: int, body: UpdateCommentSchema, db: AsyncSession):
    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id {comment_id} not found")

    comment.description = body.description

    if comment.check_profanity():
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment contains forbidden words")

    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession):
    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment
