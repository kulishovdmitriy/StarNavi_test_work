import asyncio
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from src.entity.models import Comment, User
from src.schemas.comment import CreateCommentSchema, UpdateCommentSchema
from src.services.tasks import send_auto_reply_after_delay
from src.services.logger import setup_logger

logger = setup_logger(__name__)


async def get_comments(post_id: int, db: AsyncSession, current_user: User):
    """
    Asynchronously retrieves all comments for a specific post created by the current user.

    This function allows the user to fetch all comments associated with a particular post.
    It only returns comments that were created by the currently authenticated user.
    If the user has not created any comments for the specified post, an empty list is returned.

    :param post_id: The ID of the post for which comments are being fetched.
    :param db: The asynchronous session for database operations.
    :param current_user: The current authenticated user object.

    :return: A list containing all comments for the specified post created by the current user;
             returns an empty list if no comments are found.
    """

    stmt = select(Comment).filter_by(user=current_user).where(Comment.post_id == post_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    return comments


async def get_comment_by_post(post_id: int, comment_id: int, db: AsyncSession, current_user: User):
    """
    Asynchronously retrieves a specific comment from a post by its ID.

    This function allows the user to fetch a comment from a specific post identified by its post ID.
    If the comment exists and belongs to the currently authenticated user, it returns the comment.
    If the comment is not found or does not belong to the user, it returns None.

    :param post_id: ID of the post to fetch the comment from.
    :param comment_id: ID of the comment to be fetched.
    :param db: Database session to use for the query.
    :param current_user: The user requesting the comment.

    :return: The specified comment if found; returns None otherwise.
    """

    stmt = select(Comment).filter_by(user=current_user).filter(Comment.post_id == post_id, Comment.id == comment_id)
    comment = await db.execute(stmt)
    return comment.scalar_one_or_none()


async def create_comment(post_id: int, body: CreateCommentSchema, db: AsyncSession, current_user: User):
    """
    Asynchronously creates a new comment for a specified post.

    This function allows the user to add a comment to a specific post identified by the given post ID.
    If the comment contains profanity, a 400 HTTPException is raised, blocking the comment from being created.
    If the comment is successfully created, an automatic reply is sent if the feature is enabled for the user.

    :param post_id: The ID of the post to which the comment is being added.
    :param body: The schema containing data for the comment.
    :param db: The async database session used for database operations.
    :param current_user: The user currently creating the comment.

    :return: The newly created comment object; raises a 400 HTTPException if profanity is detected.
    """

    new_comment = Comment(post_id=post_id, user=current_user, **body.model_dump(exclude_unset=True))

    logger.info(f"Attempting to create a comment for post_id={post_id} by user_id={current_user.id}")

    if await new_comment.check_profanity():
        logger.warning(
            f"Profanity detected in comment for post_id={post_id} by user_id={current_user.id}. Comment blocked.")
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
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
    Asynchronously updates an existing comment with new data.

    This function allows the user to modify an existing comment. The comment can only be updated
    if it belongs to the currently authenticated user. If the comment is found and updated successfully,
    the updated comment object is returned. If the comment is not found or the user is not authorized
    to update it, an appropriate exception is raised.

    :param comment_id: The ID of the comment to update.
    :param body: The data to update the comment with, encapsulated in an UpdateCommentSchema instance.
    :param db: The asynchronous database session to use for the operation.
    :param current_user: The currently authenticated user performing the update.

    :return: The updated comment object if the update is successful; raises a 404 HTTPException if
             the comment is not found, or a 403 HTTPException if the user is not authorized to update it.
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
    Asynchronously deletes a specified comment from the database.

    This function allows the user to delete a comment they have previously created.
    If the comment is found and successfully deleted, the deleted comment object is returned.
    If the comment is not found or does not belong to the user, appropriate exceptions are raised.

    :param comment_id: The ID of the comment to be deleted.
    :param db: The asynchronous database session used to perform the deletion.
    :param current_user: The user attempting to delete the comment.

    :return: The deleted comment object if successful; raises a 404 HTTPException if the comment is not found,
             or a 403 HTTPException if the user is not authorized to delete it.
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
