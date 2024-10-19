from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from src.entity.models import Comment, User
from src.schemas.comment import CreateCommentSchema, UpdateCommentSchema


async def get_comments(post_id: int, db: AsyncSession, current_user: User):
    stmt = select(Comment).filter_by(user=current_user).where(Comment.post_id == post_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    return comments


async def get_comment_by_post(post_id: int, comment_id: int, db: AsyncSession, current_user: User):
    stmt = select(Comment).filter_by(user=current_user).filter(Comment.post_id == post_id, Comment.id == comment_id)
    comment = await db.execute(stmt)
    return comment.scalar_one_or_none()


async def create_comment(post_id: int, body: CreateCommentSchema, db: AsyncSession, current_user: User):
    new_comment = Comment(post_id=post_id, user=current_user, **body.model_dump(exclude_unset=True))

    if new_comment.check_profanity():
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment is blocked due to forbidden words")

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def update_comment(comment_id: int, body: UpdateCommentSchema, db: AsyncSession, current_user: User):
    stmt = select(Comment).filter_by(id=comment_id, user=current_user)
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


async def delete_comment(comment_id: int, db: AsyncSession, current_user: User):
    stmt = select(Comment).filter_by(id=comment_id, user=current_user)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment


async def get_comments_daily_breakdown(date_from: date, date_to: date, db: AsyncSession, current_user: User):
    stmt = select(
        func.date(Comment.created_at).label('date'),
        func.count().label('total_comments'),
        func.sum(
            case(
                (Comment.is_blocked, 1),
                else_=0
            )
        ).label('blocked_comments')
    ).filter(
        func.date(Comment.created_at).between(date_from, date_to),
        Comment.user == current_user
    ).group_by(
        func.date(Comment.created_at)
    ).order_by(
        func.date(Comment.created_at)
    )

    results = await db.execute(stmt)

    daily_data = results.all()

    response = [
        {
            'date': row[0],
            'total_comments': row[1],
            'blocked_comments': row[2]
        }
        for row in daily_data
    ]

    return response
