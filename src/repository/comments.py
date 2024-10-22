import asyncio
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from src.entity.models import Comment, User
from src.schemas.comment import CreateCommentSchema, UpdateCommentSchema
from src.servises.tasks import send_auto_reply_after_delay
from src.servises.logger import setup_logger

logger = setup_logger(__name__)


async def get_comments(post_id: int, db: AsyncSession, current_user: User):
    """
    :param post_id: The ID of the post for which comments are being fetched.
    :param db: The asynchronous session for database operations.
    :param current_user: The current authenticated user object.
    :return: A list containing all comments for the specified post created by the current user.
    """

    stmt = select(Comment).filter_by(user=current_user).where(Comment.post_id == post_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    return comments


async def get_comment_by_post(post_id: int, comment_id: int, db: AsyncSession, current_user: User):
    """
    :param post_id: ID of the post to fetch the comment from.
    :param comment_id: ID of the comment to be fetched.
    :param db: Database session to use for the query.
    :param current_user: The user requesting the comment.
    :return: The specified comment if found, None otherwise.
    """

    stmt = select(Comment).filter_by(user=current_user).filter(Comment.post_id == post_id, Comment.id == comment_id)
    comment = await db.execute(stmt)
    return comment.scalar_one_or_none()


async def create_comment(post_id: int, body: CreateCommentSchema, db: AsyncSession, current_user: User):
    """
    :param post_id: The ID of the post to which the comment is being added.
    :param body: The schema containing data for the comment.
    :param db: The async database session used for database operations.
    :param current_user: The user currently creating the comment.
    :return: The newly created comment object.
    """

    new_comment = Comment(post_id=post_id, user=current_user, **body.model_dump(exclude_unset=True))

    logger.info(f"Attempting to create a comment for post_id={post_id} by user_id={current_user.id}")

    if await new_comment.check_profanity():
        logger.warning(
            f"Profanity detected in comment for post_id={post_id} by user_id={current_user.id}. Comment blocked.")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Comment contains forbidden words and is blocked.")

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    logger.info(f"Comment for post_id={post_id} by user_id={current_user.id} created successfully.")

    if current_user.auto_reply_enabled:
        try:
            logger.info(
                f"Отправка автоматического ответа для post_id={post_id}, comment_id={new_comment.id}, user_id={current_user.id}")

            asyncio.create_task(send_auto_reply_after_delay(post_id, new_comment.id, current_user.id, current_user.reply_delay_minutes))

        except Exception as e:
            logger.error(f"Ошибка при отправке автоматического ответа: {str(e)}")

    return new_comment


async def update_comment(comment_id: int, body: UpdateCommentSchema, db: AsyncSession, current_user: User):
    """
    :param comment_id: The ID of the comment to update
    :param body: The data to update the comment with, encapsulated in an UpdateCommentSchema instance
    :param db: The asynchronous database session to use for the operation
    :param current_user: The currently authenticated user performing the update
    :return: The updated comment object if the update is successful
    """

    stmt = select(Comment).filter_by(id=comment_id, user=current_user)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id {comment_id} not found")

    comment.description = body.description

    if await comment.check_profanity():
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment contains forbidden words")

    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession, current_user: User):
    """
    :param comment_id: The ID of the comment to be deleted
    :param db: The database session used to perform the deletion
    :param current_user: The user attempting to delete the comment
    :return: The deleted comment if successful; None otherwise
    """

    stmt = select(Comment).filter_by(id=comment_id, user=current_user)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment


async def get_comments_daily_breakdown(date_from: date, date_to: date, db: AsyncSession):
    """
    :param date_from: The start date for the period to fetch comments breakdown.
    :param date_to: The end date for the period to fetch comments breakdown.
    :param db: The database session used to execute the query.
    :return: A list of dictionaries containing the date, total_comments, and blocked_comments for each day within the given date range.
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
