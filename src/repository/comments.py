import asyncio
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from src.entity.models import Comment, User
from src.schemas.comment import CreateCommentSchema, UpdateCommentSchema
from src.services.tasks import send_auto_reply_after_delay
from src.services.logger import setup_logger
from src.conf import messages


logger = setup_logger(__name__)


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

    if await new_comment.check_profanity():
        logger.warning(
            f"Profanity detected in comment for post_id={post_id} by user_id={current_user.id}. Comment blocked.")
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.COMMENT_CONTAINS_FORBIDDEN_WORDS)

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    if current_user.auto_reply_enabled:
        try:
            asyncio.create_task(send_auto_reply_after_delay(post_id, new_comment.id, current_user.id, current_user.reply_delay_minutes))

        except Exception as err:
            logger.error(f"Error while sending automatic reply: {str(err)}")

    return new_comment


async def update_comment(comment_id: int, body: UpdateCommentSchema, db: AsyncSession, current_user: User):

    stmt = select(Comment).filter_by(id=comment_id, user=current_user)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND.format(comment_id=comment_id))

    comment.description = body.description

    if await comment.check_profanity():
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.COMMENT_CONTAINS_FORBIDDEN_WORDS)

    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession, current_user: User):

    stmt = select(Comment).filter_by(id=comment_id, user=current_user)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND.format(comment_id=comment_id))

    await db.delete(comment)
    await db.commit()


async def get_comments_daily_breakdown(date_from: date, date_to: date, db: AsyncSession):
    """
    Asynchronously retrieves a breakdown of comments for each day within the specified date range.

    This function calculates the total number of comments and the number of blocked comments
    for each day within the specified date range. It returns a list of dictionaries
    with the date, total comments count, and blocked comments count.

    :param date_from: The start date for the period to fetch comments breakdown.
    :param date_to: The end date for the period to fetch comments breakdown.
    :param db: The asynchronous database session used to execute the query.

    :return: A list of dictionaries containing the date, total_comments, and blocked_comments
             for each day within the given date range.
    """

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
